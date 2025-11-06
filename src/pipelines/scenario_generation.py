"""
Scenario generation pipeline.

Generates high-quality shot definitions from text descriptions using LLMs.
Can be used standalone or integrated with film generation pipeline.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
import click

from pipelines.tasks.film_tasks import ScenarioGenerationTask
from config import CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# Main Scenario Generation Function
# ============================================================================


async def run_scenario_generation(
    description: str,
    output_path: str,
    num_shots: int = 5,
    provider: str = "openrouter",
    model: Optional[str] = None,
    style: Optional[str] = None,
    mood: Optional[str] = None,
    duration_per_shot: int = 5,
    aspect_ratio: str = "16:9",
) -> dict:
    """
    Generate shot definitions from text description.

    Args:
        description: Text description of the scene
        output_path: Path to save generated shots JSON
        num_shots: Number of shots to generate
        provider: Provider type ('openrouter', 'local')
        model: Model to use (or None for default)
        style: Visual style
        mood: Emotional mood
        duration_per_shot: Default shot duration
        aspect_ratio: Video aspect ratio

    Returns:
        Dictionary with results
    """
    logger.info("=" * 80)
    logger.info("SCENARIO GENERATION")
    logger.info("=" * 80)

    # Create task
    async with ScenarioGenerationTask(
        provider_type=provider,
        model=model,
    ) as task:
        # Show available models
        if model is None:
            models = task.get_available_models()
            logger.info(f"Using default model. Available models:")
            for m in models[:3]:  # Show first 3
                logger.info(f"  - {m['key']}: {m['description']}")

        # Estimate cost
        estimated_cost = task.estimate_cost(description, num_shots)
        logger.info(f"Estimated cost: ${estimated_cost:.4f}")

        # Generate scenario
        logger.info(f"\nGenerating {num_shots} shots from description...")
        logger.info(f"Description: {description[:100]}...")

        result = await task.generate_from_description(
            description=description,
            num_shots=num_shots,
            style=style,
            mood=mood,
            duration_per_shot=duration_per_shot,
            aspect_ratio=aspect_ratio,
        )

        # Convert shots to JSON
        shots_data = [shot.model_dump() for shot in result.shots]

        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(shots_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ Scenario generation complete!")
        logger.info(f"📁 Saved to: {output_file}")
        logger.info(f"🎬 Generated {len(result.shots)} shots")
        logger.info(f"⏱️  Total duration: {result.estimated_duration}s")
        logger.info(f"💵 Actual cost: ${result.cost_usd:.4f}")
        logger.info(f"📝 Summary: {result.scenario_summary}")

        # Print shot overview
        logger.info("\nShot Overview:")
        for shot in result.shots:
            logger.info(f"  {shot.shot_id}: {shot.shot_type} - {shot.enhanced_prompt[:60]}...")

        return {
            "output_path": str(output_file),
            "num_shots": len(result.shots),
            "total_duration": result.estimated_duration,
            "cost_usd": float(result.cost_usd),
            "scenario_summary": result.scenario_summary,
            "provider": result.provider,
            "model": result.model,
        }


# ============================================================================
# CLI Interface
# ============================================================================


@click.command()
@click.option("--description", "-d", required=True, help="Text description of the scene to generate")
@click.option("--output", "-o", required=True, help="Output path for shots JSON file")
@click.option("--num-shots", "-n", type=int, default=5, help="Number of shots to generate (default: 5)")
@click.option("--provider", type=click.Choice(["openrouter", "local"]), default="openrouter", help="Scenario provider to use (default: openrouter)")
@click.option(
    "--model",
    "-m",
    type=click.Choice(
        [
            "claude-3.5-sonnet",
            "claude-3-haiku",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "llama-3.1-70b",
            "gemini-pro",
        ]
    ),
    help="Model to use (default: from .env or claude-3-haiku)",
)
@click.option("--style", "-s", help='Visual style (e.g., "film noir", "cyberpunk", "documentary")')
@click.option("--mood", help='Emotional mood (e.g., "tense", "nostalgic", "uplifting")')
@click.option("--duration", type=int, default=5, help="Default shot duration in seconds (default: 5)")
@click.option("--aspect-ratio", type=click.Choice(["16:9", "9:16", "1:1"]), default="16:9", help="Video aspect ratio (default: 16:9)")
@click.option("--list-models", is_flag=True, help="List available models and exit")
def main(
    description: str,
    output: str,
    num_shots: int,
    provider: str,
    model: Optional[str],
    style: Optional[str],
    mood: Optional[str],
    duration: int,
    aspect_ratio: str,
    list_models: bool,
):
    """
    Generate cinematic shot definitions from text descriptions.

    Uses LLMs via OpenRouter to create high-quality shot sequences with detailed
    prompts, camera angles, lighting, and cinematic details.

    Example:

        \b
        uv run python -m pipelines.scenario_generation \\
          --description "A detective enters a dimly lit office" \\
          --output shots.json \\
          --num-shots 7 \\
          --style "film noir" \\
          --mood "tense"
    """
    if list_models:

        async def show_models():
            async with ScenarioGenerationTask(provider_type=provider) as task:
                models = task.get_available_models()
                print("\nAvailable Models:")
                print("=" * 80)
                for m in models:
                    print(f"\n{m['key']}")
                    print(f"  ID: {m['id']}")
                    print(f"  Description: {m['description']}")
                    print(f"  Cost: ${m['cost_per_1k_output_tokens']:.4f} per 1K output tokens")
                    print(f"  Context: {m['context_window']:,} tokens")

        asyncio.run(show_models())
        return

    # Run scenario generation
    result = asyncio.run(
        run_scenario_generation(
            description=description,
            output_path=output,
            num_shots=num_shots,
            provider=provider,
            model=model,
            style=style,
            mood=mood,
            duration_per_shot=duration,
            aspect_ratio=aspect_ratio,
        )
    )

    logger.info("\n" + "=" * 80)
    logger.info("NEXT STEPS")
    logger.info("=" * 80)
    logger.info(f"\n1. Review generated shots: {result['output_path']}")
    logger.info(f"\n2. Generate film from shots:")
    logger.info(f"\n   uv run python -m pipelines.film_generation \\")
    logger.info(f"     --film_id my_film \\")
    logger.info(f"     --shots_json_path {result['output_path']} \\")
    logger.info(f"     --budget_limit 10.00")


if __name__ == "__main__":
    main()
