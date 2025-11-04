"""
Cost tracking for PPTX generation.

Tracks costs across presentations and provides reporting.
"""

import json
import logging
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, List

from .models import PresentationRequest, PresentationResult

logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================


class BudgetExceededError(Exception):
    """Raised when budget limit is exceeded"""

    pass


# ============================================================================
# Cost Tracker
# ============================================================================


class CostTracker:
    """
    Tracks costs for PPTX generation.

    Features:
    - Budget enforcement
    - Cost estimation
    - Monthly cost aggregation
    - Detailed cost reports
    """

    def __init__(self, budget_limit: Optional[Decimal] = None, tracking_dir: Optional[str] = None):
        """
        Initialize cost tracker.

        Args:
            budget_limit: Maximum allowed cost in USD (None = unlimited)
            tracking_dir: Directory to store cost reports
        """
        self.budget_limit = budget_limit
        self.actual_cost = Decimal("0.00")
        self.presentations: List[PresentationResult] = []

        # Set up tracking directory
        if tracking_dir:
            self.tracking_dir = Path(tracking_dir)
        else:
            from config import CONFIG

            media_dir = CONFIG.get("MEDIA_GALLERY_DIR", "./media_gallery")
            self.tracking_dir = Path(media_dir) / "PRESENTATIONS" / "cost_reports"

        self.tracking_dir.mkdir(parents=True, exist_ok=True)

    def estimate_cost(self, request: PresentationRequest, provider_name: str = "openai", model: str = "gpt-4o-mini") -> Decimal:
        """
        Estimate cost before generation.

        Args:
            request: Presentation request
            provider_name: Content provider name
            model: Model to use

        Returns:
            Estimated cost in USD
        """
        # Import here to avoid circular dependency
        from .providers.content_provider import create_content_provider

        provider = create_content_provider(provider=provider_name, model=model)
        estimated = provider.estimate_cost(request)

        logger.info(f"Estimated cost: ${estimated:.4f} for {request.num_slides} slides")
        return estimated

    def check_budget(self, estimated_cost: Decimal) -> None:
        """
        Check if operation is within budget.

        Args:
            estimated_cost: Estimated cost of operation

        Raises:
            BudgetExceededError: If budget would be exceeded
        """
        if self.budget_limit is None:
            return

        projected_total = self.actual_cost + estimated_cost

        if projected_total > self.budget_limit:
            raise BudgetExceededError(
                f"Budget exceeded: ${projected_total:.4f} > ${self.budget_limit:.4f} "
                f"(current: ${self.actual_cost:.4f}, estimated: ${estimated_cost:.4f})"
            )

    def record_presentation(self, result: PresentationResult) -> None:
        """
        Record completed presentation cost.

        Args:
            result: Presentation result with cost information
        """
        self.presentations.append(result)
        self.actual_cost += result.cost_usd

        logger.info(f"Recorded presentation {result.presentation_id}: " f"${result.cost_usd:.4f} (total: ${self.actual_cost:.4f})")

        # Save report
        self._save_presentation_report(result)

    def get_total_cost(self) -> Decimal:
        """Get total cost of all presentations."""
        return self.actual_cost

    def get_remaining_budget(self) -> Optional[Decimal]:
        """
        Get remaining budget.

        Returns:
            Remaining budget in USD, or None if unlimited
        """
        if self.budget_limit is None:
            return None

        return max(Decimal("0.00"), self.budget_limit - self.actual_cost)

    def get_cost_by_model(self) -> Dict[str, Decimal]:
        """
        Get cost breakdown by model.

        Returns:
            Dictionary mapping model names to total cost
        """
        cost_by_model = {}

        for pres in self.presentations:
            model = pres.model_used
            if model not in cost_by_model:
                cost_by_model[model] = Decimal("0.00")
            cost_by_model[model] += pres.cost_usd

        return cost_by_model

    def get_monthly_costs(self, year: int, month: int) -> Decimal:
        """
        Get total costs for a specific month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Total cost for that month
        """
        total = Decimal("0.00")

        for pres in self.presentations:
            if pres.generated_at.year == year and pres.generated_at.month == month:
                total += pres.cost_usd

        return total

    def generate_report(self) -> Dict:
        """
        Generate comprehensive cost report.

        Returns:
            Dictionary with cost statistics
        """
        report = {
            "total_cost_usd": float(self.actual_cost),
            "budget_limit_usd": float(self.budget_limit) if self.budget_limit else None,
            "remaining_budget_usd": float(self.get_remaining_budget()) if self.get_remaining_budget() is not None else None,
            "total_presentations": len(self.presentations),
            "cost_by_model": {k: float(v) for k, v in self.get_cost_by_model().items()},
            "average_cost_per_presentation": float(self.actual_cost / len(self.presentations)) if self.presentations else 0,
            "generated_at": datetime.now().isoformat(),
        }

        return report

    def save_report(self, filename: Optional[str] = None) -> str:
        """
        Save cost report to file.

        Args:
            filename: Custom filename (default: timestamp-based)

        Returns:
            Path to saved report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cost_report_{timestamp}.json"

        report_path = self.tracking_dir / filename
        report = self.generate_report()

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved cost report to {report_path}")
        return str(report_path)

    def _save_presentation_report(self, result: PresentationResult) -> None:
        """Save individual presentation report."""
        filename = f"presentation_{result.presentation_id}_{result.generated_at.strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.tracking_dir / filename

        report = {
            "presentation_id": result.presentation_id,
            "file_path": result.file_path,
            "slide_count": result.slide_count,
            "cost_usd": float(result.cost_usd),
            "tokens_used": result.tokens_used,
            "provider": result.provider,
            "model_used": result.model_used,
            "generated_at": result.generated_at.isoformat(),
            "cache_hit": result.cache_hit,
            "metadata": result.metadata,
        }

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.debug(f"Saved presentation report to {report_path}")


# ============================================================================
# Utility Functions
# ============================================================================


def load_cost_history(tracking_dir: Optional[str] = None) -> List[Dict]:
    """
    Load all cost reports from tracking directory.

    Args:
        tracking_dir: Directory to load from (uses default if None)

    Returns:
        List of cost report dictionaries
    """
    if tracking_dir:
        dir_path = Path(tracking_dir)
    else:
        from config import CONFIG

        media_dir = CONFIG.get("MEDIA_GALLERY_DIR", "./media_gallery")
        dir_path = Path(media_dir) / "PRESENTATIONS" / "cost_reports"

    if not dir_path.exists():
        return []

    reports = []
    for report_file in dir_path.glob("presentation_*.json"):
        try:
            with open(report_file) as f:
                reports.append(json.load(f))
        except Exception as e:
            logger.warning(f"Failed to load report {report_file}: {e}")

    return reports
