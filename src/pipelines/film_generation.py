"""
Main film generation pipeline.

Orchestrates the complete film generation workflow:
1. Load shot definitions
2. Configure providers and quality settings
3. Estimate costs
4. Generate all assets (images, videos, audio)
5. Save metadata and cost reports
6. (Future) Compose final film

Usage:
    # From command line
    uv run python -m pipelines.film_generation \\
        --film_id "my_film_001" \\
        --shots_json_path "./shots.json" \\
        --budget_limit 10.00

    # Programmatically
    from pipelines.film_generation import run_film_pipeline
    run_film_pipeline(film_id="test", shots_json_path="shots.json")
"""

import asyncio
import click
import logging
from pathlib import Path

# ZenML is disabled - use standalone mode
# (ZenML initialization issues on Windows, not needed for this project)
ZENML_AVAILABLE = False

def pipeline(**kwargs):
    """No-op decorator for pipeline (ZenML disabled)"""
    def decorator(func):
        return func
    return decorator


from config import CONFIG
from pipelines.params.film_params import create_film_params_from_cli, FilmPipelineParams
from pipelines.steps.film_steps import (
    load_shot_definitions,
    configure_shots,
    estimate_costs,
    generate_shots,
    save_shots_metadata,
    record_costs,
    compose_final_film,
)
from common.log import me_init_logger

me_init_logger()
logger = logging.getLogger(__name__)


# ============================================================================
# Pipeline Definition
# ============================================================================

def film_generation_pipeline(params: FilmPipelineParams) -> str:
    """
    Film generation pipeline - runs steps sequentially.

    Generates film from shot definitions including:
    - Image generation
    - Video animation
    - Audio synthesis
    - Cost tracking
    """
    logger.info("Running film pipeline...")

    # Log full configuration
    logger.info("=" * 60)
    logger.info("PIPELINE CONFIGURATION:")
    logger.info(f"  Film ID: {params.film_id}")
    logger.info(f"  Shots JSON: {params.shots_json_path}")
    logger.info(f"  Budget Limit: ${params.budget_limit_usd if params.budget_limit_usd else 'unlimited'}")
    logger.info(f"  Output Directory: {params.output_dir}")
    logger.info(f"  Use Cache: {params.use_cache}")
    logger.info("")
    logger.info("PROVIDERS:")
    logger.info(f"  Image: {params.default_image_provider}")
    logger.info(f"  Video: {params.default_video_provider}")
    logger.info(f"  Audio: {params.default_audio_provider}")
    logger.info("")
    logger.info("API KEYS:")
    logger.info(f"  FAL: {'[SET]' if params.fal_api_key else '[NOT SET]'}")
    logger.info(f"  Replicate: {'[SET]' if params.replicate_api_key else '[NOT SET]'}")
    logger.info(f"  OpenAI: {'[SET]' if params.openai_api_key else '[NOT SET]'}")
    logger.info(f"  ElevenLabs: {'[SET]' if params.elevenlabs_api_key else '[NOT SET]'}")
    logger.info("=" * 60)

    # Execute steps
    shot_definitions = load_shot_definitions(params)
    shot_configs = configure_shots(shot_definitions, params)
    cost_estimate = estimate_costs(shot_configs, params)
    completed_shots = generate_shots(shot_configs, params)
    metadata_path = save_shots_metadata(completed_shots, params)
    cost_report = record_costs(completed_shots, cost_estimate, params)
    final_film_path = compose_final_film(completed_shots, params)

    return final_film_path


# ============================================================================
# CLI Interface
# ============================================================================


@click.command()
@click.option("--film_id", required=True, help="Unique identifier for this film project")
@click.option("--shots_json_path", required=True, type=click.Path(exists=True), help="Path to JSON file with shot definitions")
@click.option("--budget_limit", type=float, default=None, help="Maximum budget in USD (optional)")
@click.option("--image_provider", type=click.Choice(["fal", "replicate"]), default="fal", help="Image generation provider")
@click.option("--video_provider", type=click.Choice(["minimax", "kling", "runway"]), default="minimax", help="Video generation provider")
@click.option("--audio_provider", type=click.Choice(["openai", "elevenlabs"]), default="openai", help="Audio synthesis provider")
@click.option("--no_cache", is_flag=True, default=False, help="Disable asset caching")
@click.option("--output_dir", type=click.Path(), default=None, help="Output directory (defaults to FILM_GALLERY_DIR/projects/{film_id})")
def main(
    film_id: str,
    shots_json_path: str,
    budget_limit: float,
    image_provider: str,
    video_provider: str,
    audio_provider: str,
    no_cache: bool,
    output_dir: str,
):
    """
    Generate a film from shot definitions.

    This pipeline:
    - Loads shot definitions from JSON
    - Generates images using AI
    - Animates images to videos
    - Synthesizes dialogue audio
    - Tracks costs and enforces budgets
    - Caches assets to save money

    Example:
        uv run python -m pipelines.film_generation \\
            --film_id "my_first_film" \\
            --shots_json_path "./example_shots.json" \\
            --budget_limit 5.00 \\
            --video_provider minimax
    """
    logger.info("=" * 60)
    logger.info("FILM GENERATION PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Film ID: {film_id}")
    logger.info(f"Shots: {shots_json_path}")
    logger.info(f"Budget: ${budget_limit or 'unlimited'}")
    logger.info(f"Providers: {image_provider} + {video_provider} + {audio_provider}")
    logger.info("=" * 60)

    # Create parameters
    params = create_film_params_from_cli(
        film_id=film_id,
        shots_json_path=shots_json_path,
        budget_limit=budget_limit,
        default_image_provider=image_provider,
        default_video_provider=video_provider,
        default_audio_provider=audio_provider,
        use_cache=not no_cache,
        output_dir=output_dir,
    )

    # Validate API keys
    missing_keys = []
    if not params.fal_api_key:
        missing_keys.append("FAL_API_KEY")
    if not params.openai_api_key and audio_provider == "openai":
        missing_keys.append("OPENAI_API_KEY")
    if not params.elevenlabs_api_key and audio_provider == "elevenlabs":
        missing_keys.append("ELEVENLABS_API_KEY")

    if missing_keys:
        logger.error(f"[ERROR] Missing required API keys in .env: {', '.join(missing_keys)}")
        logger.error("Please add them to your .env file")
        return

    try:
        # Run pipeline
        final_film_path = film_generation_pipeline(params)

        logger.info("=" * 60)
        logger.info("[SUCCESS] PIPELINE COMPLETE")
        logger.info(f"Final film: {final_film_path}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"[ERROR] Pipeline failed: {e}", exc_info=True)
        raise


# ============================================================================
# Programmatic Interface
# ============================================================================


def run_film_pipeline(film_id: str, shots_json_path: str, budget_limit: float = None, **kwargs) -> str:
    """
    Run film pipeline programmatically.

    Args:
        film_id: Unique film identifier
        shots_json_path: Path to shots JSON file
        budget_limit: Optional budget limit in USD
        **kwargs: Additional parameters

    Returns:
        Path to final film

    Example:
        from pipelines.film_generation import run_film_pipeline

        final_film = run_film_pipeline(
            film_id="test_film",
            shots_json_path="./shots.json",
            budget_limit=10.00,
            video_provider="minimax"
        )
    """
    params = create_film_params_from_cli(film_id=film_id, shots_json_path=shots_json_path, budget_limit=budget_limit, **kwargs)

    if ZENML_AVAILABLE:
        pipeline_instance = film_generation_pipeline(
            load_shot_definitions_step=load_shot_definitions(params),
            configure_shots_step=configure_shots,
            estimate_costs_step=estimate_costs(params=params),
            generate_shots_step=generate_shots(params=params),
            save_shots_metadata_step=save_shots_metadata(params=params),
            record_costs_step=record_costs(params=params),
            compose_final_film_step=compose_final_film(params=params),
        )
        return pipeline_instance.run()
    else:
        return film_generation_pipeline(params)


if __name__ == "__main__":
    main()
