"""
ZenML pipeline steps for film generation.

Note: These steps are designed for newer ZenML but may need adaptation
based on the actual ZenML version installed.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Tuple

# ZenML is disabled - steps are plain functions
def step(func):
    """No-op decorator for step (ZenML disabled)"""
    return func


from config import CONFIG
from film.cost_tracker import CostTracker
from film.models import (
    ShotDefinition,
    ShotConfig,
    ImageConfig,
    VideoConfig,
    AudioConfig,
    CostEstimate,
    CompletedShot,
)
from pipelines.params.film_params import FilmPipelineParams
from pipelines.tasks.film_tasks import generate_all_shots

logger = logging.getLogger(__name__)


# ============================================================================
# Input Loading Steps
# ============================================================================


@step
def load_shot_definitions(
    params: FilmPipelineParams,
) -> List[ShotDefinition]:
    """
    Load shot definitions from JSON file.

    Returns raw shot definitions without provider configuration.
    """
    logger.info(f"Loading shots from: {params.shots_json_path}")

    shots_file = Path(params.shots_json_path)
    if not shots_file.exists():
        raise FileNotFoundError(f"Shots file not found: {params.shots_json_path}")

    with open(shots_file, "r", encoding="utf-8") as f:
        shots_data = json.load(f)

    # Parse into ShotDefinition objects
    shot_definitions = [ShotDefinition(**shot_data) for shot_data in shots_data]

    logger.info(f"Loaded {len(shot_definitions)} shot definitions")
    return shot_definitions


@step
def configure_shots(
    shot_definitions: List[ShotDefinition],
    params: FilmPipelineParams,
) -> List[ShotConfig]:
    """
    Convert shot definitions to shot configs with provider settings.

    Applies default providers and quality settings from params.
    """
    logger.info("Configuring shots with provider settings...")

    shot_configs = []
    for shot_def in shot_definitions:
        # Build configs from params
        image_config = ImageConfig(
            width=params.image_width,
            height=params.image_height,
            guidance_scale=params.guidance_scale,
            inference_steps=params.inference_steps,
        )

        video_config = VideoConfig(
            duration=shot_def.duration,
        )

        audio_config = AudioConfig()

        # Create shot config
        shot_config = ShotConfig(
            shot_def=shot_def,
            image_provider=params.default_image_provider,
            video_provider=params.default_video_provider,
            audio_provider=params.default_audio_provider,
            image_config=image_config,
            video_config=video_config,
            audio_config=audio_config,
        )

        shot_configs.append(shot_config)

    logger.info(f"Configured {len(shot_configs)} shots")
    return shot_configs


# ============================================================================
# Cost Estimation Steps
# ============================================================================


@step
def estimate_costs(
    shot_configs: List[ShotConfig],
    params: FilmPipelineParams,
) -> CostEstimate:
    """
    Estimate total costs before generation.

    Returns detailed cost breakdown and checks budget.
    """
    logger.info("Estimating project costs...")

    cost_tracker = CostTracker(
        project_id=params.film_id,
        budget_limit_usd=params.budget_limit_usd,
        api_keys=params.get_api_keys_dict(),
    )

    cost_estimate = cost_tracker.estimate_project_cost(shot_configs)

    logger.info(f"Total estimated cost: ${cost_estimate.total_estimated_cost}")

    if not cost_estimate.within_budget:
        logger.warning(f"⚠️  Project exceeds budget! " f"Estimated: ${cost_estimate.total_estimated_cost}, " f"Budget: ${cost_estimate.budget_limit}")

    return cost_estimate


# ============================================================================
# Generation Steps
# ============================================================================


@step
def generate_shots(
    shot_configs: List[ShotConfig],
    params: FilmPipelineParams,
) -> List[CompletedShot]:
    """
    Generate all shots (images, videos, audio).

    This is the main generation step that:
    - Creates images
    - Animates to videos
    - Synthesizes audio
    - Uses caching
    - Tracks costs
    """
    logger.info(f"🎬 Starting generation of {len(shot_configs)} shots...")

    # Run async generation
    completed_shots = asyncio.run(
        generate_all_shots(
            project_id=params.film_id,
            shot_configs=shot_configs,
            api_keys=params.get_api_keys_dict(),
            use_cache=params.use_cache,
            max_concurrent=3,  # Limit concurrent API calls
        )
    )

    logger.info(f"✓ Generated {len(completed_shots)} shots")

    # Log total costs
    total_cost = sum(shot.total_cost_usd for shot in completed_shots)
    logger.info(f"Total actual cost: ${total_cost:.4f}")

    return completed_shots


# ============================================================================
# Post-Processing Steps
# ============================================================================


@step
def save_shots_metadata(
    completed_shots: List[CompletedShot],
    params: FilmPipelineParams,
) -> str:
    """
    Save shot metadata to project directory.

    Returns path to metadata file.
    """
    logger.info("Saving shot metadata...")

    # Determine output directory
    if params.output_dir:
        output_dir = Path(params.output_dir)
    else:
        base_dir = Path(CONFIG.get("FILM_GALLERY_DIR", "./film_gallery"))
        output_dir = base_dir / "projects" / params.film_id

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save metadata
    metadata_file = output_dir / "shots_metadata.json"
    metadata = {
        "film_id": params.film_id,
        "execution_date": params.execution_date,
        "shot_count": len(completed_shots),
        "shots": [
            {
                "shot_id": shot.shot_config.shot_def.shot_id,
                "image_url": shot.image_result.image_url,
                "image_path": shot.image_result.image_path,
                "video_url": shot.video_result.video_url,
                "video_path": shot.video_result.video_path,
                "audio_path": shot.audio_result.audio_path if shot.audio_result else None,
                "cost_usd": str(shot.total_cost_usd),
                "generation_time_seconds": shot.total_time_seconds,
            }
            for shot in completed_shots
        ],
        "total_cost_usd": str(sum(shot.total_cost_usd for shot in completed_shots)),
    }

    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Metadata saved to: {metadata_file}")
    return str(metadata_file)


@step
def record_costs(
    completed_shots: List[CompletedShot],
    cost_estimate: CostEstimate,
    params: FilmPipelineParams,
) -> str:
    """
    Record final costs and generate cost report.

    Returns path to cost report.
    """
    logger.info("Recording final costs...")

    cost_tracker = CostTracker(
        project_id=params.film_id,
        budget_limit_usd=params.budget_limit_usd,
        api_keys=params.get_api_keys_dict(),
    )

    # Set estimated cost
    cost_tracker.estimated_cost = cost_estimate.total_estimated_cost

    # Record all shot costs
    for shot in completed_shots:
        cost_tracker.record_shot_cost(shot)

    # Save report
    cost_tracker.save_cost_report()
    cost_tracker.log_cost_summary()

    # Return summary
    summary = cost_tracker.get_cost_summary()
    return json.dumps(summary, indent=2)


# ============================================================================
# Composition Step (Future)
# ============================================================================


@step
def compose_final_film(
    completed_shots: List[CompletedShot],
    params: FilmPipelineParams,
) -> str:
    """
    Compose individual shots into final film using FFmpeg.

    TODO: Implement video composition with:
    - Shot sequencing
    - Transitions
    - Audio mixing
    - Final export

    Returns path to final film file.
    """
    logger.warning("Film composition not yet implemented")

    # Placeholder
    output_dir = Path(params.output_dir) if params.output_dir else Path("./film_gallery/projects") / params.film_id
    final_film_path = output_dir / f"{params.film_id}_final.mp4"

    logger.info(f"Final film would be saved to: {final_film_path}")
    return str(final_film_path)
