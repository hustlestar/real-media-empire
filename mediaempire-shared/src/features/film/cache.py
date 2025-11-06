"""
Asset caching system with content-based addressing.

Caches generated images, videos, and audio by content hash to avoid
regeneration of identical assets. Significant cost savings!

Key Features:
- Content-addressed storage (hash of generation params)
- Automatic cache hit/miss logging
- Download and store remote assets locally
- Cost savings tracking
"""

import hashlib
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from decimal import Decimal

import httpx

from config import CONFIG
from film.models import (
    ImageResult,
    VideoResult,
    AudioResult,
    AssetMetadata,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Cache Configuration
# ============================================================================


class CacheConfig:
    """Configuration for asset cache"""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or CONFIG.get("FILM_GALLERY_DIR", "./film_gallery"))
        self.cache_dir = self.base_dir / "cache"
        self.images_dir = self.cache_dir / "images"
        self.videos_dir = self.cache_dir / "videos"
        self.audio_dir = self.cache_dir / "audio"
        self.metadata_dir = self.base_dir / "metadata" / "by_prompt_hash"

        # Ensure directories exist
        for directory in [
            self.cache_dir,
            self.images_dir,
            self.videos_dir,
            self.audio_dir,
            self.metadata_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self, asset_type: str, content_hash: str, extension: str) -> Path:
        """Get file path for cached asset"""
        type_dirs = {
            "image": self.images_dir,
            "video": self.videos_dir,
            "audio": self.audio_dir,
        }

        cache_dir = type_dirs.get(asset_type)
        if not cache_dir:
            raise ValueError(f"Unknown asset type: {asset_type}")

        return cache_dir / f"{content_hash}.{extension}"

    def get_metadata_path(self, content_hash: str) -> Path:
        """Get metadata file path"""
        return self.metadata_dir / f"{content_hash}.json"


# ============================================================================
# Asset Cache
# ============================================================================


class AssetCache:
    """
    Content-addressed cache for generated assets.

    Prevents regeneration of identical assets, saving costs and time.
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.cache_hits = 0
        self.cache_misses = 0
        self.cost_saved = Decimal("0")

    def _compute_content_hash(self, **kwargs) -> str:
        """
        Compute deterministic hash from generation parameters.

        Two identical generation requests will have the same hash.
        """
        # Sort keys for deterministic ordering
        sorted_kwargs = {k: kwargs[k] for k in sorted(kwargs.keys())}

        # Convert to JSON string
        content_str = json.dumps(sorted_kwargs, sort_keys=True, default=str)

        # SHA256 hash
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    # ========================================================================
    # Image Caching
    # ========================================================================

    async def get_or_generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        provider: str,
        model: str,
        config_dict: Dict[str, Any],
        generate_func,  # Async callable that generates the image
    ) -> tuple[ImageResult, bool]:
        """
        Get cached image or generate new one.

        Returns:
            (ImageResult, was_cached)
        """
        # Compute content hash
        # Remove model from config_dict if present to avoid duplicate kwarg
        config_without_model = {k: v for k, v in config_dict.items() if k != 'model'}
        content_hash = self._compute_content_hash(
            prompt=prompt,
            negative_prompt=negative_prompt or "",
            provider=provider,
            model=model,
            **config_without_model,
        )

        # Check cache
        cached_result = self._lookup_image_cache(content_hash)
        if cached_result:
            self.cache_hits += 1
            self.cost_saved += cached_result.cost_usd
            logger.info(f"✓ IMAGE CACHE HIT: {content_hash[:12]}... " f"(saved ${cached_result.cost_usd})")
            return cached_result, True

        # Cache miss - generate
        self.cache_misses += 1
        logger.info(f"✗ Image cache miss: {content_hash[:12]}... Generating...")

        result: ImageResult = await generate_func()

        # Download and cache
        await self._cache_image(result, content_hash, prompt, negative_prompt, config_dict)

        return result, False

    def _lookup_image_cache(self, content_hash: str) -> Optional[ImageResult]:
        """Look up cached image by content hash"""
        # Check if file exists
        for ext in ["jpg", "jpeg", "png", "webp"]:
            cache_path = self.config.get_cache_path("image", content_hash, ext)
            if cache_path.exists():
                # Load metadata
                metadata = self._load_metadata(content_hash)
                if metadata:
                    return ImageResult(
                        success=True,
                        provider=metadata.provider,
                        model=metadata.model,
                        cost_usd=metadata.cost_usd,
                        generation_time_seconds=0,  # Instant from cache
                        image_url=metadata.file_path,
                        image_path=str(cache_path),
                        width=metadata.config.get("width", 1024),
                        height=metadata.config.get("height", 576),
                        content_hash=content_hash,
                    )
        return None

    async def _cache_image(
        self,
        result: ImageResult,
        content_hash: str,
        prompt: str,
        negative_prompt: Optional[str],
        config_dict: Dict[str, Any],
    ):
        """Download and cache image, save metadata"""
        # Determine extension
        ext = config_dict.get("output_format", "jpeg")
        if ext == "jpeg":
            ext = "jpg"

        cache_path = self.config.get_cache_path("image", content_hash, ext)

        # Download image
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(result.image_url)
                response.raise_for_status()

                with open(cache_path, "wb") as f:
                    f.write(response.content)

            logger.info(f"Cached image: {cache_path}")

            # Update result with local path
            result.image_path = str(cache_path)
            result.content_hash = content_hash

            # Save metadata
            metadata = AssetMetadata(
                asset_id=content_hash,
                asset_type="image",
                content_hash=content_hash,
                file_path=str(cache_path),
                prompt=prompt,
                negative_prompt=negative_prompt,
                provider=result.provider,
                model=result.model,
                config=config_dict,
                cost_usd=result.cost_usd,
                generation_time_seconds=result.generation_time_seconds,
            )
            self._save_metadata(metadata)

        except Exception as e:
            logger.warning(f"Failed to cache image: {e}")

    # ========================================================================
    # Video Caching
    # ========================================================================

    async def get_or_generate_video(
        self,
        image_url: str,
        prompt: str,
        provider: str,
        model: str,
        config_dict: Dict[str, Any],
        generate_func,
    ) -> tuple[VideoResult, bool]:
        """Get cached video or generate new one"""
        # Remove model from config_dict if present to avoid duplicate kwarg
        config_without_model = {k: v for k, v in config_dict.items() if k != 'model'}
        content_hash = self._compute_content_hash(
            image_url=image_url,
            prompt=prompt,
            provider=provider,
            model=model,
            **config_without_model,
        )

        cached_result = self._lookup_video_cache(content_hash)
        if cached_result:
            self.cache_hits += 1
            self.cost_saved += cached_result.cost_usd
            logger.info(f"✓ VIDEO CACHE HIT: {content_hash[:12]}... " f"(saved ${cached_result.cost_usd})")
            return cached_result, True

        self.cache_misses += 1
        logger.info(f"✗ Video cache miss: {content_hash[:12]}... Generating...")

        result: VideoResult = await generate_func()
        await self._cache_video(result, content_hash, image_url, prompt, config_dict)

        return result, False

    def _lookup_video_cache(self, content_hash: str) -> Optional[VideoResult]:
        """Look up cached video"""
        cache_path = self.config.get_cache_path("video", content_hash, "mp4")
        if cache_path.exists():
            metadata = self._load_metadata(content_hash)
            if metadata:
                return VideoResult(
                    success=True,
                    provider=metadata.provider,
                    model=metadata.model,
                    cost_usd=metadata.cost_usd,
                    generation_time_seconds=0,
                    video_url=metadata.file_path,
                    video_path=str(cache_path),
                    duration=metadata.config.get("duration", 5.0),
                    fps=metadata.config.get("fps", 24),
                    content_hash=content_hash,
                )
        return None

    async def _cache_video(
        self,
        result: VideoResult,
        content_hash: str,
        image_url: str,
        prompt: str,
        config_dict: Dict[str, Any],
    ):
        """Download and cache video"""
        cache_path = self.config.get_cache_path("video", content_hash, "mp4")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.get(result.video_url)
                response.raise_for_status()

                with open(cache_path, "wb") as f:
                    f.write(response.content)

            logger.info(f"Cached video: {cache_path}")

            result.video_path = str(cache_path)
            result.content_hash = content_hash

            metadata = AssetMetadata(
                asset_id=content_hash,
                asset_type="video",
                content_hash=content_hash,
                file_path=str(cache_path),
                prompt=prompt,
                provider=result.provider,
                model=result.model,
                config=config_dict,
                cost_usd=result.cost_usd,
                generation_time_seconds=result.generation_time_seconds,
            )
            self._save_metadata(metadata)

        except Exception as e:
            logger.warning(f"Failed to cache video: {e}")

    # ========================================================================
    # Audio Caching
    # ========================================================================

    async def get_or_generate_audio(
        self,
        text: str,
        provider: str,
        model: str,
        voice: str,
        config_dict: Dict[str, Any],
        generate_func,
    ) -> tuple[AudioResult, bool]:
        """Get cached audio or generate new one"""
        # Remove model from config_dict if present to avoid duplicate kwarg
        config_without_model = {k: v for k, v in config_dict.items() if k != 'model'}
        content_hash = self._compute_content_hash(
            text=text,
            provider=provider,
            model=model,
            voice=voice,
            **config_without_model,
        )

        cached_result = self._lookup_audio_cache(content_hash)
        if cached_result:
            self.cache_hits += 1
            self.cost_saved += cached_result.cost_usd
            logger.info(f"✓ AUDIO CACHE HIT: {content_hash[:12]}... " f"(saved ${cached_result.cost_usd})")
            return cached_result, True

        self.cache_misses += 1
        logger.info(f"✗ Audio cache miss: {content_hash[:12]}... Generating...")

        result: AudioResult = await generate_func()
        await self._cache_audio(result, content_hash, text, config_dict)

        return result, False

    def _lookup_audio_cache(self, content_hash: str) -> Optional[AudioResult]:
        """Look up cached audio"""
        for ext in ["mp3", "wav", "opus"]:
            cache_path = self.config.get_cache_path("audio", content_hash, ext)
            if cache_path.exists():
                metadata = self._load_metadata(content_hash)
                if metadata:
                    return AudioResult(
                        success=True,
                        provider=metadata.provider,
                        model=metadata.model,
                        cost_usd=metadata.cost_usd,
                        generation_time_seconds=0,
                        audio_url=None,
                        audio_path=str(cache_path),
                        duration_seconds=0.0,  # Would need to parse audio file
                        content_hash=content_hash,
                    )
        return None

    async def _cache_audio(
        self,
        result: AudioResult,
        content_hash: str,
        text: str,
        config_dict: Dict[str, Any],
    ):
        """Cache audio file"""
        ext = config_dict.get("output_format", "mp3")
        cache_path = self.config.get_cache_path("audio", content_hash, ext)

        try:
            # Audio might be URL or binary data
            if result.audio_url:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(result.audio_url)
                    response.raise_for_status()
                    audio_data = response.content
            else:
                # Binary data already available (implementation dependent)
                logger.warning("No audio URL - cannot cache audio")
                return

            with open(cache_path, "wb") as f:
                f.write(audio_data)

            logger.info(f"Cached audio: {cache_path}")

            result.audio_path = str(cache_path)
            result.content_hash = content_hash

            metadata = AssetMetadata(
                asset_id=content_hash,
                asset_type="audio",
                content_hash=content_hash,
                file_path=str(cache_path),
                prompt=text,
                provider=result.provider,
                model=result.model,
                config=config_dict,
                cost_usd=result.cost_usd,
                generation_time_seconds=result.generation_time_seconds,
            )
            self._save_metadata(metadata)

        except Exception as e:
            logger.warning(f"Failed to cache audio: {e}")

    # ========================================================================
    # Metadata Management
    # ========================================================================

    def _save_metadata(self, metadata: AssetMetadata):
        """Save asset metadata as JSON"""
        metadata_path = self.config.get_metadata_path(metadata.content_hash)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata.model_dump(), f, indent=2, default=str)

    def _load_metadata(self, content_hash: str) -> Optional[AssetMetadata]:
        """Load asset metadata from JSON"""
        metadata_path = self.config.get_metadata_path(content_hash)
        if not metadata_path.exists():
            return None

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AssetMetadata(**data)
        except Exception as e:
            logger.warning(f"Failed to load metadata for {content_hash}: {e}")
            return None

    # ========================================================================
    # Cache Statistics
    # ========================================================================

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_cost_saved_usd": str(self.cost_saved),
        }

    def log_cache_stats(self):
        """Log cache statistics"""
        stats = self.get_cache_stats()
        logger.info(
            f"Cache Stats: {stats['cache_hits']} hits, {stats['cache_misses']} misses "
            f"({stats['hit_rate_percent']}% hit rate), "
            f"${stats['total_cost_saved_usd']} saved"
        )
