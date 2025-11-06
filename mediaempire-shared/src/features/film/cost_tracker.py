"""
Cost tracking and budget enforcement for film generation.

Features:
- Pre-execution cost estimation
- Real-time cost tracking during generation
- Budget limit enforcement
- Monthly/yearly cost reporting
- Provider cost comparison
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Dict, Any

from config import CONFIG
from film.models import (
    ShotConfig,
    ShotCostEstimate,
    CostEstimate,
    CompletedShot,
)
from film.providers.image_providers import create_image_provider
from film.providers.video_providers import create_video_provider
from film.providers.audio_providers import create_audio_provider

logger = logging.getLogger(__name__)


# ============================================================================
# Budget Exceeded Exception
# ============================================================================


class BudgetExceededError(Exception):
    """Raised when generation would exceed budget limit"""

    pass


# ============================================================================
# Cost Tracker
# ============================================================================


class CostTracker:
    """
    Track costs during film generation and enforce budget limits.

    Usage:
        tracker = CostTracker(budget_limit_usd=Decimal('10.00'))
        estimate = tracker.estimate_project_cost(project)
        tracker.check_budget(estimate.total_estimated_cost)
        # ... generate shots ...
        tracker.record_shot_cost(completed_shot)
    """

    def __init__(
        self,
        project_id: str,
        budget_limit_usd: Optional[Decimal] = None,
        api_keys: Optional[Dict[str, str]] = None,
    ):
        self.project_id = project_id
        self.budget_limit = budget_limit_usd
        self.api_keys = api_keys or {}

        # Cost tracking
        self.estimated_cost = Decimal("0")
        self.actual_cost = Decimal("0")
        self.cost_log: List[Dict[str, Any]] = []

        # Setup cost tracking directory
        base_dir = Path(CONFIG.get("FILM_GALLERY_DIR", "./film_gallery"))
        self.cost_dir = base_dir / "cost_tracking"
        self.monthly_dir = self.cost_dir / datetime.now().strftime("%Y-%m")
        self.monthly_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # Cost Estimation
    # ========================================================================

    def estimate_project_cost(
        self,
        shot_configs: List[ShotConfig],
    ) -> CostEstimate:
        """
        Estimate total cost for a project before generation.

        Returns detailed cost breakdown per shot.
        """
        logger.info(f"Estimating cost for {len(shot_configs)} shots...")

        shot_estimates = []
        total_cost = Decimal("0")

        for shot_config in shot_configs:
            estimate = self._estimate_shot_cost(shot_config)
            shot_estimates.append(estimate)
            total_cost += estimate.total_cost

        self.estimated_cost = total_cost

        within_budget = True
        if self.budget_limit:
            within_budget = total_cost <= self.budget_limit

        cost_estimate = CostEstimate(
            project_id=self.project_id,
            shot_estimates=shot_estimates,
            total_estimated_cost=total_cost,
            budget_limit=self.budget_limit,
            within_budget=within_budget,
        )

        # Log estimate
        logger.info(f"Estimated cost: ${total_cost:.4f} " f"(budget: ${self.budget_limit or 'unlimited'})")

        if not within_budget:
            logger.warning(f"⚠️  Estimated cost ${total_cost:.4f} exceeds " f"budget ${self.budget_limit:.4f}")

        return cost_estimate

    def _estimate_shot_cost(self, shot_config: ShotConfig) -> ShotCostEstimate:
        """Estimate cost for a single shot"""
        # Image cost
        try:
            image_provider = create_image_provider(shot_config.image_provider.value, self.api_keys.get("fal", ""))
            image_cost = image_provider.estimate_cost(shot_config.image_config)
        except Exception as e:
            logger.warning(f"Failed to estimate image cost: {e}")
            image_cost = Decimal("0.003")  # Default FAL cost

        # Video cost
        try:
            video_provider = create_video_provider(shot_config.video_provider.value, self.api_keys.get("fal", ""))
            video_cost = video_provider.estimate_cost(shot_config.video_config)
        except Exception as e:
            logger.warning(f"Failed to estimate video cost: {e}")
            video_cost = Decimal("0.05")  # Default Minimax cost

        # Audio cost (only if has dialogue)
        audio_cost = Decimal("0")
        if shot_config.has_dialogue:
            try:
                audio_provider = create_audio_provider(shot_config.audio_provider.value, self.api_keys.get("openai", ""))
                audio_cost = audio_provider.estimate_cost(shot_config.shot_def.dialogue or "", shot_config.audio_config)
            except Exception as e:
                logger.warning(f"Failed to estimate audio cost: {e}")
                audio_cost = Decimal("0.001")  # Minimal

        total_cost = image_cost + video_cost + audio_cost

        return ShotCostEstimate(
            shot_id=shot_config.shot_def.shot_id,
            image_cost=image_cost,
            video_cost=video_cost,
            audio_cost=audio_cost,
            total_cost=total_cost,
        )

    # ========================================================================
    # Budget Enforcement
    # ========================================================================

    def check_budget(self, estimated_additional_cost: Decimal):
        """
        Check if adding this cost would exceed budget.

        Raises BudgetExceededError if would exceed.
        """
        if not self.budget_limit:
            return  # No budget limit

        projected_total = self.actual_cost + estimated_additional_cost

        if projected_total > self.budget_limit:
            raise BudgetExceededError(
                f"Budget exceeded: ${projected_total:.4f} > ${self.budget_limit:.4f}. "
                f"Current: ${self.actual_cost:.4f}, "
                f"Additional: ${estimated_additional_cost:.4f}"
            )

    # ========================================================================
    # Cost Recording
    # ========================================================================

    def record_shot_cost(self, shot: CompletedShot):
        """Record actual cost after shot generation"""
        self.actual_cost += shot.total_cost_usd

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "shot_id": shot.shot_config.shot_def.shot_id,
            "image_cost": str(shot.image_result.cost_usd),
            "video_cost": str(shot.video_result.cost_usd),
            "audio_cost": str(shot.audio_result.cost_usd) if shot.audio_result else "0",
            "total_cost": str(shot.total_cost_usd),
            "cumulative_cost": str(self.actual_cost),
            "image_provider": shot.image_result.provider,
            "video_provider": shot.video_result.provider,
            "audio_provider": shot.audio_result.provider if shot.audio_result else None,
        }

        self.cost_log.append(log_entry)

        logger.info(f"Shot {shot.shot_config.shot_def.shot_id}: " f"${shot.total_cost_usd:.4f} " f"(cumulative: ${self.actual_cost:.4f})")

        # Check if approaching budget
        if self.budget_limit:
            remaining = self.budget_limit - self.actual_cost
            if remaining < Decimal("1.00"):
                logger.warning(f"⚠️  Low budget: ${remaining:.4f} remaining " f"of ${self.budget_limit:.4f}")

    def record_cache_hit(self, asset_type: str, cost_saved: Decimal):
        """Record cost saved from cache hit"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "cache_hit",
            "asset_type": asset_type,
            "cost_saved": str(cost_saved),
        }
        self.cost_log.append(log_entry)

    # ========================================================================
    # Cost Reporting
    # ========================================================================

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost summary"""
        # Calculate savings
        cost_saved = self.estimated_cost - self.actual_cost if self.estimated_cost > 0 else Decimal("0")

        # Provider breakdown
        provider_costs = self._calculate_provider_breakdown()

        return {
            "project_id": self.project_id,
            "estimated_cost": str(self.estimated_cost),
            "actual_cost": str(self.actual_cost),
            "cost_saved": str(cost_saved),
            "budget_limit": str(self.budget_limit) if self.budget_limit else None,
            "budget_remaining": str(self.budget_limit - self.actual_cost) if self.budget_limit else None,
            "shots_generated": len([log for log in self.cost_log if "shot_id" in log]),
            "provider_breakdown": provider_costs,
        }

    def _calculate_provider_breakdown(self) -> Dict[str, Dict[str, str]]:
        """Calculate costs by provider"""
        breakdown = {
            "image": {},
            "video": {},
            "audio": {},
        }

        for log_entry in self.cost_log:
            if "shot_id" not in log_entry:
                continue

            # Image
            img_provider = log_entry.get("image_provider")
            if img_provider:
                img_cost = Decimal(log_entry["image_cost"])
                breakdown["image"][img_provider] = str(Decimal(breakdown["image"].get(img_provider, "0")) + img_cost)

            # Video
            vid_provider = log_entry.get("video_provider")
            if vid_provider:
                vid_cost = Decimal(log_entry["video_cost"])
                breakdown["video"][vid_provider] = str(Decimal(breakdown["video"].get(vid_provider, "0")) + vid_cost)

            # Audio
            aud_provider = log_entry.get("audio_provider")
            if aud_provider:
                aud_cost = Decimal(log_entry["audio_cost"])
                breakdown["audio"][aud_provider] = str(Decimal(breakdown["audio"].get(aud_provider, "0")) + aud_cost)

        return breakdown

    def save_cost_report(self):
        """Save detailed cost report to file"""
        report = {
            "project_id": self.project_id,
            "summary": self.get_cost_summary(),
            "detailed_log": self.cost_log,
            "generated_at": datetime.now().isoformat(),
        }

        # Save to monthly directory
        report_file = self.monthly_dir / f"{self.project_id}_costs.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Cost report saved: {report_file}")

    def log_cost_summary(self):
        """Log cost summary to console"""
        summary = self.get_cost_summary()

        logger.info("=" * 60)
        logger.info("COST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Project: {summary['project_id']}")
        logger.info(f"Estimated: ${summary['estimated_cost']}")
        logger.info(f"Actual:    ${summary['actual_cost']}")
        logger.info(f"Saved:     ${summary['cost_saved']}")

        if summary["budget_limit"]:
            logger.info(f"Budget:    ${summary['budget_limit']}")
            logger.info(f"Remaining: ${summary['budget_remaining']}")

        logger.info(f"Shots:     {summary['shots_generated']}")
        logger.info("=" * 60)


# ============================================================================
# Monthly Cost Aggregator
# ============================================================================


def get_monthly_costs(year: int, month: int) -> Dict[str, Any]:
    """
    Aggregate all costs for a given month.

    Returns summary of all projects generated that month.
    """
    base_dir = Path(CONFIG.get("FILM_GALLERY_DIR", "./film_gallery"))
    monthly_dir = base_dir / "cost_tracking" / f"{year:04d}-{month:02d}"

    if not monthly_dir.exists():
        return {
            "year": year,
            "month": month,
            "total_cost": "0",
            "projects": [],
        }

    total_cost = Decimal("0")
    projects = []

    for report_file in monthly_dir.glob("*_costs.json"):
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report = json.load(f)
                project_cost = Decimal(report["summary"]["actual_cost"])
                total_cost += project_cost
                projects.append(
                    {
                        "project_id": report["project_id"],
                        "cost": str(project_cost),
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to read cost report {report_file}: {e}")

    return {
        "year": year,
        "month": month,
        "total_cost": str(total_cost),
        "project_count": len(projects),
        "projects": projects,
    }
