import click
import logging
from pathlib import Path
from typing import Optional

# Try to import ZenML, but provide fallback
try:
    from zenml import pipeline

    ZENML_AVAILABLE = True
except ImportError:
    ZENML_AVAILABLE = False

    # Fallback decorator
    def pipeline(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]

        def decorator(func):
            return func

        return decorator


from pipelines.steps.pptx_steps import (
    create_presentation_request,
    create_presentation_config,
    estimate_generation_cost,
    generate_content,
    build_presentation_file,
    record_presentation_cost,
    save_presentation_metadata,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Pipeline Definition
# ============================================================================


@pipeline(enable_cache=True)
def pptx_generation_pipeline(
    presentation_id: str,
    topic: str,
    brief: Optional[str] = None,
    num_slides: int = 10,
    tone: str = "professional",
    target_audience: Optional[str] = None,
    template_path: Optional[str] = None,
    aspect_ratio: str = "16:9",
    theme_name: str = "professional",
    font_family: str = "Calibri",
    primary_color: str = "#1F4E78",
    provider_name: str = "openai",
    model: str = "gpt-4o-mini",
    budget_limit: Optional[float] = None,
    output_dir: str = "./presentations",
):
    """
    Complete PPTX generation pipeline.

    Args:
        presentation_id: Unique presentation ID
        topic: Main topic
        brief: Optional detailed brief
        num_slides: Number of slides
        tone: Presentation tone
        target_audience: Target audience
        template_path: Custom template path
        aspect_ratio: Aspect ratio (4:3 or 16:9)
        theme_name: Theme name
        font_family: Font family
        primary_color: Primary color hex
        provider_name: Content provider
        model: Model name
        budget_limit: Budget limit in USD
        output_dir: Output directory
    """
    # Step 1: Create request
    request = create_presentation_request(
        presentation_id=presentation_id, topic=topic, brief=brief, num_slides=num_slides, tone=tone, target_audience=target_audience
    )

    # Step 2: Create config
    config = create_presentation_config(
        template_path=template_path, aspect_ratio=aspect_ratio, theme_name=theme_name, font_family=font_family, primary_color=primary_color
    )

    # Step 3: Estimate cost
    estimated_cost, within_budget = estimate_generation_cost(request=request, provider_name=provider_name, model=model, budget_limit=budget_limit)

    # Step 4: Generate content
    content = generate_content(request=request, provider_name=provider_name, model=model)

    # Step 5: Build presentation
    file_path = build_presentation_file(request=request, config=config, content=content, output_dir=output_dir)

    # Step 6: Record cost
    result = record_presentation_cost(
        request=request, content=content, file_path=file_path, provider_name=provider_name, model=model, cache_hit=False
    )

    # Step 7: Save metadata
    metadata_path = save_presentation_metadata(result=result, output_dir=output_dir)

    return result


# ============================================================================
# Standalone Execution (No ZenML)
# ============================================================================


def run_pptx_generation_standalone(
    presentation_id: str,
    topic: Optional[str] = None,
    brief: Optional[str] = None,
    num_slides: int = 10,
    tone: str = "professional",
    additional_instructions: Optional[str] = None,
    reference_file: Optional[str] = None,
    content_file: Optional[str] = None,
    template_path: Optional[str] = None,
    budget_limit: Optional[float] = None,
    model: str = "gpt-4o-mini",
    output_dir: str = "./presentations",
):
    """
    Run PPTX generation without ZenML.

    Fallback implementation for when ZenML is not available.
    Can use AI generation or text file input.
    """
    from datetime import datetime
    from decimal import Decimal
    from pptx_gen.generator import PresentationGenerator
    from pptx_gen.models import PresentationRequest, PresentationConfig, ToneType
    from pptx_gen.cost_tracker import CostTracker
    from pptx_gen.text_parser import parse_presentation_from_file

    logger.info("Running PPTX generation in standalone mode (no ZenML)")

    # Create config
    config = PresentationConfig(template_path=template_path)

    # Create cost tracker
    cost_tracker = CostTracker(budget_limit=Decimal(str(budget_limit)) if budget_limit else None)

    # Create generator
    generator = PresentationGenerator(config=config, cost_tracker=cost_tracker, output_dir=output_dir)

    # Check if using content file
    if content_file:
        logger.info(f"Using content from file: {content_file}")
        outline, slides = parse_presentation_from_file(content_file)

        # Build presentation directly from parsed content
        result = generator.generate_from_slides(presentation_id=presentation_id, outline=outline, slides=slides)
    else:
        # Use AI generation
        if not topic:
            raise ValueError("Either topic or content_file must be provided")

        # Load reference content if provided
        reference_content = None
        if reference_file:
            logger.info(f"Loading reference content from: {reference_file}")
            try:
                with open(reference_file, "r", encoding="utf-8") as f:
                    reference_content = f.read()
                logger.info(f"Loaded {len(reference_content)} characters of reference content")
            except Exception as e:
                logger.warning(f"Failed to load reference file: {e}")

        request = PresentationRequest(
            presentation_id=presentation_id,
            topic=topic,
            brief=brief,
            num_slides=num_slides,
            tone=ToneType(tone),
            additional_instructions=additional_instructions,
            reference_content=reference_content,
        )

        result = generator.generate(request, model=model)

    logger.info(f"Presentation generated: {result.file_path}")
    logger.info(f"   Slides: {result.slide_count}")
    logger.info(f"   Cost: ${result.cost_usd:.4f}")
    logger.info(f"   Cache hit: {result.cache_hit}")

    return result


# ============================================================================
# CLI Interface
# ============================================================================


@click.command()
@click.option("--presentation-id", required=True, help="Unique presentation ID")
@click.option("--topic", default=None, help="Main topic or title (not needed if using --content-file)")
@click.option("--brief", default=None, help="Detailed brief or description")
@click.option("--num-slides", default=10, type=int, help="Number of slides")
@click.option(
    "--tone",
    default="professional",
    type=click.Choice(["professional", "casual", "motivational", "educational", "sales", "technical"]),
    help="Presentation tone",
)
@click.option("--target-audience", default=None, help="Target audience")
@click.option("--additional-instructions", default=None, help="Additional instructions for AI content generation")
@click.option("--reference-file", default=None, help="Path to reference text file (content will be used as context for AI)")
@click.option("--content-file", default=None, help="Path to text file with presentation content (bypasses AI generation)")
@click.option("--template-path", default=None, help="Path to custom PPTX template")
@click.option("--aspect-ratio", default="16:9", type=click.Choice(["4:3", "16:9"]), help="Aspect ratio")
@click.option("--theme-name", default="professional", help="Theme name")
@click.option("--font-family", default="Calibri", help="Font family")
@click.option("--primary-color", default="#1F4E78", help="Primary color (hex)")
@click.option("--provider", default="openai", help="Content provider")
@click.option("--model", default="gpt-4o-mini", help="Model name")
@click.option("--budget-limit", default=None, type=float, help="Budget limit in USD")
@click.option("--output-dir", default="./presentations", help="Output directory")
@click.option("--use-zenml/--no-zenml", default=False, help="Use ZenML pipeline")
def main(
    presentation_id: str,
    topic: Optional[str],
    brief: Optional[str],
    num_slides: int,
    tone: str,
    target_audience: Optional[str],
    additional_instructions: Optional[str],
    reference_file: Optional[str],
    content_file: Optional[str],
    template_path: Optional[str],
    aspect_ratio: str,
    theme_name: str,
    font_family: str,
    primary_color: str,
    provider: str,
    model: str,
    budget_limit: Optional[float],
    output_dir: str,
    use_zenml: bool,
):
    """
    Generate PowerPoint presentation using AI or from text file.

    Example with AI:
        uv run python -m pipelines.pptx_generation \\
            --presentation-id "sales_q3_2025" \\
            --topic "Q3 Sales Review" \\
            --brief "Quarterly achievements and goals" \\
            --num-slides 10 \\
            --budget-limit 1.00

    Example with text file:
        uv run python -m pipelines.pptx_generation \\
            --presentation-id "my_presentation" \\
            --content-file "my_content.txt"
    """
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Validate input
    if content_file and not topic:
        # Using content file, topic not required
        pass
    elif not content_file and not topic:
        logger.error("Either --topic or --content-file must be provided")
        return

    if use_zenml and ZENML_AVAILABLE:
        logger.info("Using ZenML pipeline")
        result = pptx_generation_pipeline(
            presentation_id=presentation_id,
            topic=topic,
            brief=brief,
            num_slides=num_slides,
            tone=tone,
            target_audience=target_audience,
            template_path=template_path,
            aspect_ratio=aspect_ratio,
            theme_name=theme_name,
            font_family=font_family,
            primary_color=primary_color,
            provider_name=provider,
            model=model,
            budget_limit=budget_limit,
            output_dir=output_dir,
        )
    else:
        if use_zenml:
            logger.warning("ZenML not available, falling back to standalone mode")

        result = run_pptx_generation_standalone(
            presentation_id=presentation_id,
            topic=topic,
            brief=brief,
            num_slides=num_slides,
            tone=tone,
            additional_instructions=additional_instructions,
            reference_file=reference_file,
            content_file=content_file,
            template_path=template_path,
            budget_limit=budget_limit,
            model=model,
            output_dir=output_dir,
        )

    print(f"\n{'='*60}")
    print(f"Presentation Generated Successfully!")
    print(f"{'='*60}")
    print(f"File: {result.file_path}")
    print(f"Slides: {result.slide_count}")
    print(f"Cost: ${result.cost_usd:.4f}")
    print(f"Model: {result.model_used}")
    print(f"Cache Hit: {result.cache_hit}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
