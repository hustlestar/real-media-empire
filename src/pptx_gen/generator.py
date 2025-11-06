"""
Main presentation generator orchestrator.

Coordinates content generation, template management, slide building,
and cost tracking.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .models import (
    PresentationRequest,
    PresentationConfig,
    PresentationResult,
    ContentGenerationResult,
)
from .providers.content_provider import create_content_provider
from .template_manager import TemplateManager
from .slide_builder import SlideBuilder
from .cost_tracker import CostTracker

logger = logging.getLogger(__name__)


# ============================================================================
# Presentation Generator
# ============================================================================


class PresentationGenerator:
    """
    Main orchestrator for PowerPoint presentation generation.

    Coordinates:
    - Content generation via AI providers
    - Template loading/creation
    - Slide building
    - Cost tracking
    - Caching for cost savings
    """

    def __init__(
        self,
        config: PresentationConfig,
        cost_tracker: Optional[CostTracker] = None,
        cache_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize presentation generator.

        Args:
            config: Presentation configuration
            cost_tracker: Cost tracker (creates new if None)
            cache_dir: Directory for cached content
            output_dir: Directory for output files
        """
        self.config = config
        self.cost_tracker = cost_tracker or CostTracker()

        # Set up directories
        from config import CONFIG

        media_dir = CONFIG.get("MEDIA_GALLERY_DIR", "./media_gallery")
        pres_base = Path(media_dir) / "PRESENTATIONS"

        self.cache_dir = Path(cache_dir) if cache_dir else pres_base / "cache"
        self.output_dir = Path(output_dir) if output_dir else pres_base / "output"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized generator with cache: {self.cache_dir}, output: {self.output_dir}")

    def generate(
        self, request: PresentationRequest, provider_name: str = "openai", model: str = "gpt-4o-mini", skip_cache: bool = False
    ) -> PresentationResult:
        """
        Generate complete presentation.

        Main entry point for end-to-end generation.

        Args:
            request: Presentation request
            provider_name: Content provider to use
            model: Model name
            skip_cache: Skip cache lookup if True

        Returns:
            PresentationResult with file path and metadata

        Raises:
            BudgetExceededError: If budget exceeded
            ContentGenerationError: If generation fails
        """
        logger.info(f"Generating presentation: {request.presentation_id}")

        # Step 1: Check cache
        content_result = None
        cache_hit = False

        if not skip_cache:
            content_result = self._lookup_cache(request, provider_name, model)
            if content_result:
                cache_hit = True
                logger.info("Cache hit! Reusing content.")

        # Step 2: Estimate cost and check budget
        if not cache_hit:
            estimated_cost = self.cost_tracker.estimate_cost(request, provider_name, model)
            self.cost_tracker.check_budget(estimated_cost)
            logger.info(f"Estimated cost: ${estimated_cost:.4f}")

        # Step 3: Generate content if needed
        if not cache_hit:
            provider = create_content_provider(provider=provider_name, model=model)
            content_result = provider.generate_all_content(request)
            logger.info(f"Generated {len(content_result.slides)} slides")

            # Cache the content
            self._cache_content(request, provider_name, model, content_result)

        # Step 4: Build presentation
        template_manager = TemplateManager(self.config)
        template_manager.load_or_create_presentation()

        slide_builder = SlideBuilder(template_manager, self.config)

        for slide_def in content_result.slides:
            slide_builder.build_slide(slide_def)

        logger.info("Built all slides")

        # Step 5: Save presentation
        output_filename = f"{request.presentation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
        output_path = self.output_dir / output_filename
        saved_path = template_manager.save_presentation(str(output_path))

        # Step 6: Create result
        result = PresentationResult(
            presentation_id=request.presentation_id,
            file_path=saved_path,
            slide_count=len(content_result.slides),
            cost_usd=content_result.cost_usd if not cache_hit else Decimal("0.00"),
            tokens_used=content_result.tokens_used,
            provider=provider_name,
            model_used=model,
            generated_at=datetime.now(),
            cache_hit=cache_hit,
            outline=content_result.outline,
            metadata={"request": request.model_dump(), "config": self.config.model_dump()},
        )

        # Step 7: Record cost
        if not cache_hit:
            self.cost_tracker.record_presentation(result)

        logger.info(f"Presentation complete: {saved_path} (${result.cost_usd:.4f})")
        return result

    def generate_from_slides(
        self,
        presentation_id: str,
        outline: "PresentationOutline",
        slides: list,
    ) -> PresentationResult:
        """
        Generate presentation from pre-built slides (e.g., from text file).

        Args:
            presentation_id: Unique presentation ID
            outline: Presentation outline
            slides: List of SlideDefinition objects

        Returns:
            PresentationResult with file path and metadata
        """
        from .models import PresentationOutline

        logger.info(f"Generating presentation from {len(slides)} slides")

        # Step 1: Load or create template
        template_manager = TemplateManager(self.config)
        template_manager.load_or_create_presentation()

        # Step 2: Build slides
        slide_builder = SlideBuilder(template_manager, self.config)
        for slide_def in slides:
            slide_builder.build_slide(slide_def)

        logger.info("Built all slides")

        # Step 3: Save presentation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{presentation_id}_{timestamp}.pptx"
        output_path = self.output_dir / output_filename

        saved_path = template_manager.save_presentation(str(output_path))

        # Step 4: Create result
        result = PresentationResult(
            presentation_id=presentation_id,
            file_path=saved_path,
            slide_count=len(slides),
            cost_usd=Decimal("0.00"),  # No AI cost for file-based input
            tokens_used=0,
            provider="text_file",
            model_used="n/a",
            generated_at=datetime.now(),
            cache_hit=False,
            outline=outline,
            metadata={"source": "text_file", "config": self.config.model_dump()},
        )

        logger.info(f"Presentation complete: {saved_path} (no AI cost)")
        return result

    def _compute_cache_key(self, request: PresentationRequest, provider_name: str, model: str) -> str:
        """
        Compute cache key for request.

        Uses SHA256 hash of request parameters.

        Args:
            request: Presentation request
            provider_name: Provider name
            model: Model name

        Returns:
            Cache key (hex string)
        """
        cache_data = {
            "topic": request.topic,
            "brief": request.brief,
            "num_slides": request.num_slides,
            "tone": request.tone.value,
            "key_points": request.key_points,
            "provider": provider_name,
            "model": model,
        }

        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_str.encode()).hexdigest()

        return cache_hash

    def _lookup_cache(self, request: PresentationRequest, provider_name: str, model: str) -> Optional[ContentGenerationResult]:
        """
        Look up cached content.

        Args:
            request: Presentation request
            provider_name: Provider name
            model: Model name

        Returns:
            ContentGenerationResult if found, None otherwise
        """
        cache_key = self._compute_cache_key(request, provider_name, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            # Reconstruct ContentGenerationResult
            content_result = ContentGenerationResult.model_validate(data)
            logger.info(f"Cache hit for key {cache_key[:8]}...")
            return content_result

        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")
            return None

    def _cache_content(self, request: PresentationRequest, provider_name: str, model: str, content_result: ContentGenerationResult) -> None:
        """
        Cache generated content.

        Args:
            request: Presentation request
            provider_name: Provider name
            model: Model name
            content_result: Generated content to cache
        """
        cache_key = self._compute_cache_key(request, provider_name, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(content_result.model_dump(), f, indent=2, default=str)

            logger.info(f"Cached content with key {cache_key[:8]}...")

        except Exception as e:
            logger.warning(f"Failed to cache content: {e}")


# ============================================================================
# Convenience Functions
# ============================================================================


def generate_presentation(
    topic: str,
    brief: Optional[str] = None,
    num_slides: int = 10,
    output_path: Optional[str] = None,
    template_path: Optional[str] = None,
    budget_limit: Optional[float] = None,
    model: str = "gpt-4o-mini",
) -> PresentationResult:
    """
    Convenience function for quick presentation generation.

    Args:
        topic: Presentation topic
        brief: Optional detailed brief
        num_slides: Number of slides
        output_path: Custom output path
        template_path: Custom template path
        budget_limit: Budget limit in USD
        model: Model to use

    Returns:
        PresentationResult

    Example:
        >>> result = generate_presentation(
        ...     topic="Quarterly Sales Review",
        ...     brief="Q3 achievements and Q4 goals",
        ...     num_slides=10,
        ...     budget_limit=1.00
        ... )
    """
    # Create request
    request = PresentationRequest(presentation_id=f"pres_{datetime.now().strftime('%Y%m%d_%H%M%S')}", topic=topic, brief=brief, num_slides=num_slides)

    # Create config
    config = PresentationConfig(template_path=template_path)

    # Create cost tracker
    cost_tracker = CostTracker(budget_limit=Decimal(str(budget_limit)) if budget_limit else None)

    # Create generator
    generator = PresentationGenerator(config=config, cost_tracker=cost_tracker)

    # Generate
    result = generator.generate(request, model=model)

    # Optionally move to custom output path
    if output_path:
        import shutil

        shutil.move(result.file_path, output_path)
        result.file_path = output_path

    return result
