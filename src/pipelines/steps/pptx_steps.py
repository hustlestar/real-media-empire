"""
ZenML pipeline steps for PPTX generation.

Provides steps for generating presentations using the PPTX generator.
"""

import logging
from decimal import Decimal
from typing import Tuple, Optional

# ZenML is disabled - steps are plain functions
ZENML_AVAILABLE = False

def step(*args, **kwargs):
    """No-op decorator for step (ZenML disabled)"""
    if len(args) == 1 and callable(args[0]):
        return args[0]

    def decorator(func):
        return func

    return decorator


from pptx_gen.models import (
    PresentationRequest,
    PresentationConfig,
    PresentationResult,
    ContentGenerationResult,
)
from pptx_gen.providers.content_provider import create_content_provider
from pptx_gen.template_manager import TemplateManager
from pptx_gen.slide_builder import SlideBuilder
from pptx_gen.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


# ============================================================================
# Pipeline Steps
# ============================================================================


@step
def create_presentation_request(
    presentation_id: str, topic: str, brief: Optional[str], num_slides: int, tone: str, target_audience: Optional[str]
) -> PresentationRequest:
    """
    Create and validate presentation request.

    Args:
        presentation_id: Unique ID for presentation
        topic: Main topic
        brief: Optional detailed brief
        num_slides: Number of slides
        tone: Presentation tone
        target_audience: Target audience

    Returns:
        Validated PresentationRequest
    """
    from pptx_gen.models import ToneType

    request = PresentationRequest(
        presentation_id=presentation_id, topic=topic, brief=brief, num_slides=num_slides, tone=ToneType(tone), target_audience=target_audience
    )

    logger.info(f"Created request for '{topic}' with {num_slides} slides")
    return request


@step
def create_presentation_config(
    template_path: Optional[str], aspect_ratio: str, theme_name: str, font_family: str, primary_color: str
) -> PresentationConfig:
    """
    Create presentation configuration.

    Args:
        template_path: Path to custom template
        aspect_ratio: Aspect ratio (4:3 or 16:9)
        theme_name: Theme name
        font_family: Font family
        primary_color: Primary color hex

    Returns:
        PresentationConfig
    """
    from pptx_gen.models import AspectRatio

    config = PresentationConfig(
        template_path=template_path,
        aspect_ratio=AspectRatio(aspect_ratio),
        theme_name=theme_name,
        font_family=font_family,
        primary_color=primary_color,
    )

    logger.info(f"Created config with {aspect_ratio} aspect ratio")
    return config


@step
def estimate_generation_cost(request: PresentationRequest, provider_name: str, model: str, budget_limit: Optional[float]) -> Tuple[Decimal, bool]:
    """
    Estimate cost and check against budget.

    Args:
        request: Presentation request
        provider_name: Provider name
        model: Model name
        budget_limit: Budget limit in USD

    Returns:
        Tuple of (estimated_cost, within_budget)
    """
    cost_tracker = CostTracker(budget_limit=Decimal(str(budget_limit)) if budget_limit else None)

    estimated = cost_tracker.estimate_cost(request, provider_name, model)
    within_budget = True

    if budget_limit:
        within_budget = estimated <= Decimal(str(budget_limit))

    logger.info(f"Estimated cost: ${estimated:.4f}, within budget: {within_budget}")
    return estimated, within_budget


@step
def generate_content(request: PresentationRequest, provider_name: str, model: str) -> ContentGenerationResult:
    """
    Generate presentation content using AI.

    Args:
        request: Presentation request
        provider_name: Provider name
        model: Model name

    Returns:
        ContentGenerationResult with slides
    """
    provider = create_content_provider(provider=provider_name, model=model)
    result = provider.generate_all_content(request)

    logger.info(f"Generated {len(result.slides)} slides, cost: ${result.cost_usd:.4f}")
    return result


@step
def build_presentation_file(request: PresentationRequest, config: PresentationConfig, content: ContentGenerationResult, output_dir: str) -> str:
    """
    Build PowerPoint file from content.

    Args:
        request: Original request
        config: Presentation config
        content: Generated content
        output_dir: Output directory

    Returns:
        Path to generated PPTX file
    """
    from datetime import datetime
    from pathlib import Path

    # Create template manager and load presentation
    template_manager = TemplateManager(config)
    template_manager.load_or_create_presentation()

    # Build slides
    slide_builder = SlideBuilder(template_manager, config)
    for slide_def in content.slides:
        slide_builder.build_slide(slide_def)

    # Save presentation
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{request.presentation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    file_path = output_path / filename

    saved_path = template_manager.save_presentation(str(file_path))
    logger.info(f"Saved presentation to {saved_path}")

    return saved_path


@step
def record_presentation_cost(
    request: PresentationRequest, content: ContentGenerationResult, file_path: str, provider_name: str, model: str, cache_hit: bool
) -> PresentationResult:
    """
    Record presentation result and cost.

    Args:
        request: Original request
        content: Generated content
        file_path: Path to saved file
        provider_name: Provider used
        model: Model used
        cache_hit: Whether cache was used

    Returns:
        PresentationResult
    """
    from datetime import datetime

    result = PresentationResult(
        presentation_id=request.presentation_id,
        file_path=file_path,
        slide_count=len(content.slides),
        cost_usd=content.cost_usd if not cache_hit else Decimal("0.00"),
        tokens_used=content.tokens_used,
        provider=provider_name,
        model_used=model,
        generated_at=datetime.now(),
        cache_hit=cache_hit,
        outline=content.outline,
    )

    # Record with cost tracker
    cost_tracker = CostTracker()
    if not cache_hit:
        cost_tracker.record_presentation(result)

    logger.info(f"Recorded presentation result: ${result.cost_usd:.4f}")
    return result


@step
def save_presentation_metadata(result: PresentationResult, output_dir: str) -> str:
    """
    Save presentation metadata to JSON.

    Args:
        result: Presentation result
        output_dir: Output directory

    Returns:
        Path to metadata file
    """
    import json
    from pathlib import Path

    metadata_dir = Path(output_dir) / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = metadata_dir / f"{result.presentation_id}_metadata.json"

    with open(metadata_file, "w") as f:
        json.dump(result.model_dump(), f, indent=2, default=str)

    logger.info(f"Saved metadata to {metadata_file}")
    return str(metadata_file)
