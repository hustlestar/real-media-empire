"""
Film generation tasks - Business logic layer.

Orchestrates providers, caching, and metadata for film asset generation.
Can be used independently of ZenML pipelines.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Optional

from film.cache import AssetCache, CacheConfig
from film.cost_tracker import CostTracker
from film.metadata import MetadataIndex
from film.models import (
    ShotDefinition,
    ShotConfig,
    ImageConfig,
    VideoConfig,
    AudioConfig,
    CompletedShot,
    ImageResult,
    VideoResult,
    AudioResult,
)
from film.providers.image_providers import create_image_provider
from film.providers.video_providers import create_video_provider
from film.providers.audio_providers import create_audio_provider
from film.providers.scenario_providers import (
    create_scenario_provider,
    ScenarioRequest,
    ScenarioResult,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Film Generation Task
# ============================================================================


class FilmGenerationTask:
    """
    Main task for generating film assets.

    Orchestrates:
    - Image generation
    - Video animation
    - Audio synthesis
    - Asset caching
    - Cost tracking
    - Metadata indexing
    """

    def __init__(
        self,
        project_id: str,
        api_keys: dict,
        cache_config: Optional[CacheConfig] = None,
        use_cache: bool = True,
    ):
        self.project_id = project_id
        self.api_keys = api_keys

        # Initialize subsystems
        self.cache = AssetCache(cache_config) if use_cache else None
        self.metadata_index = MetadataIndex()
        self.use_cache = use_cache

    async def generate_shot(
        self,
        shot_config: ShotConfig,
    ) -> CompletedShot:
        """
        Generate all assets for a single shot.

        Process:
        1. Generate/cache image
        2. Animate image to video
        3. Generate audio (if has dialogue)
        4. Record metadata
        """
        logger.info(f"🎬 Generating shot: {shot_config.shot_def.shot_id}")

        # Step 1: Generate image
        image_result = await self._generate_or_cache_image(shot_config)

        # Step 2: Animate to video
        video_result = await self._generate_or_cache_video(shot_config, image_result)

        # Step 3: Generate audio (if needed)
        audio_result = None
        if shot_config.has_dialogue:
            audio_result = await self._generate_or_cache_audio(shot_config)

        # Calculate total cost and time
        total_cost = image_result.cost_usd + video_result.cost_usd
        if audio_result:
            total_cost += audio_result.cost_usd

        total_time = (
            image_result.generation_time_seconds
            + video_result.generation_time_seconds
            + (audio_result.generation_time_seconds if audio_result else 0)
        )

        completed_shot = CompletedShot(
            shot_config=shot_config,
            image_result=image_result,
            video_result=video_result,
            audio_result=audio_result,
            total_cost_usd=total_cost,
            total_time_seconds=total_time,
        )

        logger.info(f"✓ Shot {shot_config.shot_def.shot_id} complete: " f"${total_cost:.4f} in {total_time}s")

        return completed_shot

    # ========================================================================
    # Image Generation
    # ========================================================================

    async def _generate_or_cache_image(
        self,
        shot_config: ShotConfig,
    ) -> ImageResult:
        """Generate or retrieve cached image"""
        shot_def = shot_config.shot_def

        if self.use_cache and self.cache:
            # Try cache first
            async def generate():
                return await self._generate_image(shot_config)

            result, was_cached = await self.cache.get_or_generate_image(
                prompt=shot_def.enhanced_prompt,
                negative_prompt=shot_def.negative_prompt,
                provider=shot_config.image_provider.value,
                model=shot_config.image_config.model,
                config_dict=shot_config.image_config.to_dict(),
                generate_func=generate,
            )

            # Index metadata if newly generated
            if not was_cached and result.content_hash:
                from film.models import AssetMetadata

                metadata = AssetMetadata(
                    asset_id=result.content_hash,
                    asset_type="image",
                    content_hash=result.content_hash,
                    file_path=result.image_path or result.image_url,
                    characters=shot_def.characters,
                    landscapes=shot_def.landscapes,
                    styles=shot_def.styles,
                    mood=shot_def.mood,
                    time_of_day=shot_def.time_of_day,
                    shot_type=shot_def.shot_type,
                    prompt=shot_def.enhanced_prompt,
                    negative_prompt=shot_def.negative_prompt,
                    provider=result.provider,
                    model=result.model,
                    config=shot_config.image_config.to_dict(),
                    cost_usd=result.cost_usd,
                    generation_time_seconds=result.generation_time_seconds,
                )
                self.metadata_index.index_asset(metadata)

            return result
        else:
            # No cache, generate directly
            return await self._generate_image(shot_config)

    async def _generate_image(self, shot_config: ShotConfig) -> ImageResult:
        """Actually generate image using provider"""
        provider = create_image_provider(shot_config.image_provider.value, self.api_keys.get("fal", ""))

        logger.info(f"Generating image with {provider.name}...")

        result = await provider.generate(
            prompt=shot_config.shot_def.enhanced_prompt,
            negative_prompt=shot_config.shot_def.negative_prompt,
            config=shot_config.image_config,
        )

        return result

    # ========================================================================
    # Video Generation
    # ========================================================================

    async def _generate_or_cache_video(
        self,
        shot_config: ShotConfig,
        image_result: ImageResult,
    ) -> VideoResult:
        """Generate or retrieve cached video"""
        if self.use_cache and self.cache:

            async def generate():
                return await self._generate_video(shot_config, image_result)

            result, was_cached = await self.cache.get_or_generate_video(
                image_url=image_result.image_url,
                prompt=shot_config.shot_def.enhanced_prompt,
                provider=shot_config.video_provider.value,
                model=shot_config.video_config.model or shot_config.video_provider.value,
                config_dict=shot_config.video_config.to_dict(),
                generate_func=generate,
            )

            # Index if new
            if not was_cached and result.content_hash:
                from film.models import AssetMetadata

                metadata = AssetMetadata(
                    asset_id=result.content_hash,
                    asset_type="video",
                    content_hash=result.content_hash,
                    file_path=result.video_path or result.video_url,
                    characters=shot_config.shot_def.characters,
                    landscapes=shot_config.shot_def.landscapes,
                    styles=shot_config.shot_def.styles,
                    mood=shot_config.shot_def.mood,
                    time_of_day=shot_config.shot_def.time_of_day,
                    shot_type=shot_config.shot_def.shot_type,
                    prompt=shot_config.shot_def.enhanced_prompt,
                    provider=result.provider,
                    model=result.model,
                    config=shot_config.video_config.to_dict(),
                    cost_usd=result.cost_usd,
                    generation_time_seconds=result.generation_time_seconds,
                )
                self.metadata_index.index_asset(metadata)

            return result
        else:
            return await self._generate_video(shot_config, image_result)

    async def _generate_video(
        self,
        shot_config: ShotConfig,
        image_result: ImageResult,
    ) -> VideoResult:
        """Actually generate video using provider"""
        provider = create_video_provider(shot_config.video_provider.value, self.api_keys.get("fal", ""))

        logger.info(f"Generating video with {provider.name}...")

        result = await provider.generate(
            image_url=image_result.image_url,
            prompt=shot_config.shot_def.enhanced_prompt,
            config=shot_config.video_config,
        )

        return result

    # ========================================================================
    # Audio Generation
    # ========================================================================

    async def _generate_or_cache_audio(
        self,
        shot_config: ShotConfig,
    ) -> Optional[AudioResult]:
        """Generate or retrieve cached audio"""
        dialogue = shot_config.shot_def.dialogue
        if not dialogue:
            return None

        if self.use_cache and self.cache:

            async def generate():
                return await self._generate_audio(shot_config)

            result, was_cached = await self.cache.get_or_generate_audio(
                text=dialogue,
                provider=shot_config.audio_provider.value,
                model=shot_config.audio_config.model,
                voice=shot_config.audio_config.voice,
                config_dict=shot_config.audio_config.to_dict(),
                generate_func=generate,
            )

            # Index if new
            if not was_cached and result.content_hash:
                from film.models import AssetMetadata

                metadata = AssetMetadata(
                    asset_id=result.content_hash,
                    asset_type="audio",
                    content_hash=result.content_hash,
                    file_path=result.audio_path or result.audio_url or "",
                    prompt=dialogue,
                    provider=result.provider,
                    model=result.model,
                    config=shot_config.audio_config.to_dict(),
                    cost_usd=result.cost_usd,
                    generation_time_seconds=result.generation_time_seconds,
                )
                self.metadata_index.index_asset(metadata)

            return result
        else:
            return await self._generate_audio(shot_config)

    async def _generate_audio(self, shot_config: ShotConfig) -> AudioResult:
        """Actually generate audio using provider"""
        dialogue = shot_config.shot_def.dialogue
        if not dialogue:
            raise ValueError("Cannot generate audio without dialogue")

        provider_key = "openai" if shot_config.audio_provider.value == "openai" else "elevenlabs"
        provider = create_audio_provider(shot_config.audio_provider.value, self.api_keys.get(provider_key, ""))

        logger.info(f"Generating audio with {provider.name}...")

        result = await provider.generate(
            text=dialogue,
            config=shot_config.audio_config,
        )

        return result


# ============================================================================
# Batch Generation
# ============================================================================


async def generate_all_shots(
    project_id: str,
    shot_configs: List[ShotConfig],
    api_keys: dict,
    use_cache: bool = True,
    max_concurrent: int = 3,
) -> List[CompletedShot]:
    """
    Generate all shots concurrently (with limit).

    Args:
        project_id: Project identifier
        shot_configs: List of shot configurations
        api_keys: API keys dictionary
        use_cache: Enable caching
        max_concurrent: Maximum concurrent generations

    Returns:
        List of completed shots
    """
    task = FilmGenerationTask(
        project_id=project_id,
        api_keys=api_keys,
        use_cache=use_cache,
    )

    # Use semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_with_limit(shot_config):
        async with semaphore:
            return await task.generate_shot(shot_config)

    # Generate all shots concurrently
    logger.info(f"Starting generation of {len(shot_configs)} shots...")
    completed_shots = await asyncio.gather(*[generate_with_limit(sc) for sc in shot_configs])

    # Log cache stats
    if task.cache:
        task.cache.log_cache_stats()

    return completed_shots


# ============================================================================
# Scenario Generation Task
# ============================================================================


class ScenarioGenerationTask:
    """
    Task for generating shot definitions from text descriptions.

    Uses LLMs to create high-quality cinematic shot sequences.
    """

    def __init__(
        self,
        provider_type: str = "openrouter",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize scenario generation task.

        Args:
            provider_type: Type of scenario provider ('openrouter', 'local')
            model: Model to use (e.g., 'claude-3.5-sonnet', 'gpt-4-turbo')
            api_key: API key (or from environment)
        """
        self.provider_type = provider_type
        self.model = model
        self.provider = create_scenario_provider(provider_type, api_key=api_key)

    async def generate_from_description(
        self,
        description: str,
        num_shots: int = 5,
        style: Optional[str] = None,
        mood: Optional[str] = None,
        duration_per_shot: int = 5,
        aspect_ratio: str = "16:9",
    ) -> ScenarioResult:
        """
        Generate shot definitions from text description.

        Args:
            description: Text description of the scene
            num_shots: Number of shots to generate
            style: Visual style (e.g., 'film noir', 'cyberpunk')
            mood: Emotional tone (e.g., 'tense', 'nostalgic')
            duration_per_shot: Default shot duration
            aspect_ratio: Video aspect ratio

        Returns:
            ScenarioResult with generated shots
        """
        request = ScenarioRequest(
            description=description,
            num_shots=num_shots,
            style=style,
            mood=mood,
            duration_per_shot=duration_per_shot,
            aspect_ratio=aspect_ratio,
        )

        logger.info(f"Generating {num_shots} shots from scenario...")
        logger.info(f"Using {self.provider_type} with model: {self.model or 'default'}")

        result = await self.provider.generate_scenario(request, model=self.model)

        logger.info(f"✓ Generated {len(result.shots)} shots")
        logger.info(f"  Scenario: {result.scenario_summary}")
        logger.info(f"  Duration: {result.estimated_duration}s")
        logger.info(f"  Cost: ${result.cost_usd:.4f}")

        return result

    def estimate_cost(
        self,
        description: str,
        num_shots: int = 5,
    ) -> float:
        """
        Estimate cost for scenario generation.

        Args:
            description: Scene description
            num_shots: Number of shots

        Returns:
            Estimated cost in USD
        """
        request = ScenarioRequest(
            description=description,
            num_shots=num_shots,
        )

        cost = self.provider.estimate_cost(request, model=self.model)
        return float(cost)

    def get_available_models(self) -> List[dict]:
        """Get list of available models."""
        return self.provider.get_available_models()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self.provider, "__aexit__"):
            await self.provider.__aexit__(exc_type, exc_val, exc_tb)


async def generate_scenario_to_shots(
    description: str,
    num_shots: int = 5,
    provider_type: str = "openrouter",
    model: Optional[str] = None,
    style: Optional[str] = None,
    mood: Optional[str] = None,
) -> List[ShotDefinition]:
    """
    Convenience function to generate shots from description.

    Args:
        description: Scene description
        num_shots: Number of shots to generate
        provider_type: Provider type ('openrouter', 'local')
        model: Model to use
        style: Visual style
        mood: Emotional mood

    Returns:
        List of generated shot definitions
    """
    async with ScenarioGenerationTask(provider_type=provider_type, model=model) as task:
        result = await task.generate_from_description(
            description=description,
            num_shots=num_shots,
            style=style,
            mood=mood,
        )
        return result.shots
