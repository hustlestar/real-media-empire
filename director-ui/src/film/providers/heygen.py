"""
HeyGen video provider for AI avatar generation.

Supports:
- Text-to-avatar video generation
- Custom avatars and voices
- Background customization (color, image, video)
- Multiple aspect ratios for social media
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Literal
from datetime import datetime

import httpx
from pydantic import BaseModel, Field

from ..base_provider import VideoProvider, VideoGenerationResult, ProviderConfig

logger = logging.getLogger(__name__)


class HeyGenVoiceConfig(BaseModel):
    """Configuration for HeyGen voice settings."""
    type: Literal["text"] = "text"
    input_text: str
    voice_id: str
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: int = Field(default=50, ge=0, le=100)
    emotion: Optional[str] = None  # "Excited", "Friendly", "Serious", etc.


class HeyGenCharacterConfig(BaseModel):
    """Configuration for HeyGen avatar character."""
    type: Literal["avatar"] = "avatar"
    avatar_id: str
    avatar_style: Literal["normal", "circle"] = "normal"
    scale: float = Field(default=1.0, ge=0.5, le=2.0)
    offset: Optional[Dict[str, float]] = None  # {"x": 0.15, "y": 0.15}
    matting: bool = False  # Remove background (requires green screen avatar)


class HeyGenBackgroundConfig(BaseModel):
    """Configuration for video background."""
    type: Literal["color", "image", "video"]
    value: Optional[str] = None  # Color hex or URL
    url: Optional[str] = None  # For image/video
    play_style: Optional[Literal["loop", "once"]] = "loop"
    fit: Optional[Literal["cover", "contain"]] = "cover"


class HeyGenDimensionConfig(BaseModel):
    """Video dimension configuration."""
    width: int
    height: int

    @classmethod
    def from_aspect_ratio(cls, aspect_ratio: Literal["9:16", "16:9", "1:1", "4:5"]):
        """Create dimension from common aspect ratios."""
        dimensions = {
            "9:16": {"width": 720, "height": 1280},   # TikTok, Instagram Reels
            "16:9": {"width": 1280, "height": 720},   # YouTube, LinkedIn
            "1:1": {"width": 1080, "height": 1080},   # Instagram Feed, Facebook
            "4:5": {"width": 1080, "height": 1350},   # Instagram Portrait
        }
        return cls(**dimensions[aspect_ratio])


class HeyGenConfig(ProviderConfig):
    """HeyGen provider configuration."""
    api_key: str = Field(..., description="HeyGen API key")
    base_url: str = Field(default="https://api.heygen.com", description="HeyGen API base URL")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    poll_interval: int = Field(default=10, description="Status polling interval in seconds")
    max_wait_time: int = Field(default=300, description="Maximum wait time in seconds")


class HeyGenProvider(VideoProvider):
    """
    HeyGen video generation provider.

    Features:
    - AI avatar video generation
    - Custom voices (HeyGen + ElevenLabs integration)
    - Background customization
    - Multiple aspect ratios
    """

    def __init__(self, config: HeyGenConfig):
        super().__init__(config)
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "X-Api-Key": config.api_key,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    async def generate(
        self,
        script: str,
        avatar_id: str,
        voice_id: str,
        background: Optional[HeyGenBackgroundConfig] = None,
        dimension: Optional[HeyGenDimensionConfig] = None,
        voice_config: Optional[HeyGenVoiceConfig] = None,
        character_config: Optional[HeyGenCharacterConfig] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Generate avatar video using HeyGen API.

        Args:
            script: Text script for avatar to speak
            avatar_id: HeyGen avatar ID
            voice_id: HeyGen voice ID
            background: Background configuration (optional)
            dimension: Video dimensions (optional, defaults to 9:16)
            voice_config: Advanced voice settings (optional)
            character_config: Advanced character settings (optional)
            **kwargs: Additional parameters

        Returns:
            VideoGenerationResult with video URL and metadata
        """
        try:
            # Build video input configuration
            video_input = self._build_video_input(
                script=script,
                avatar_id=avatar_id,
                voice_id=voice_id,
                background=background,
                voice_config=voice_config,
                character_config=character_config
            )

            # Set default dimension if not provided
            if dimension is None:
                dimension = HeyGenDimensionConfig.from_aspect_ratio("9:16")

            # Create generation request
            request_data = {
                "video_inputs": [video_input],
                "dimension": dimension.dict(),
                "aspect_ratio": kwargs.get("aspect_ratio"),
                "caption": kwargs.get("caption", False),
                "title": kwargs.get("title", ""),
                "test": kwargs.get("test", False)
            }

            # Remove None values
            request_data = {k: v for k, v in request_data.items() if v is not None}

            logger.info(f"Initiating HeyGen video generation with avatar {avatar_id}")

            # Submit generation request
            response = await self.client.post("/v2/video/generate", json=request_data)
            response.raise_for_status()

            result = response.json()
            video_id = result["data"]["video_id"]

            logger.info(f"HeyGen video generation started: {video_id}")

            # Poll for completion
            video_url = await self._poll_video_status(video_id)

            return VideoGenerationResult(
                video_url=video_url,
                provider="heygen",
                cost=self._estimate_cost(script, dimension),
                metadata={
                    "video_id": video_id,
                    "avatar_id": avatar_id,
                    "voice_id": voice_id,
                    "dimension": dimension.dict(),
                    "duration": self._estimate_duration(script),
                    "generated_at": datetime.utcnow().isoformat()
                }
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HeyGen API error: {e.response.text}")
            raise Exception(f"HeyGen generation failed: {e.response.text}")
        except Exception as e:
            logger.error(f"HeyGen generation error: {str(e)}")
            raise

    def _build_video_input(
        self,
        script: str,
        avatar_id: str,
        voice_id: str,
        background: Optional[HeyGenBackgroundConfig],
        voice_config: Optional[HeyGenVoiceConfig],
        character_config: Optional[HeyGenCharacterConfig]
    ) -> Dict[str, Any]:
        """Build video input configuration."""

        # Character configuration
        if character_config is None:
            character_config = HeyGenCharacterConfig(avatar_id=avatar_id)
        else:
            character_config.avatar_id = avatar_id

        # Voice configuration
        if voice_config is None:
            voice_config = HeyGenVoiceConfig(
                input_text=script,
                voice_id=voice_id,
                speed=1.1,  # Slightly faster for natural pacing
                pitch=50,
                emotion="Excited"
            )
        else:
            voice_config.input_text = script
            voice_config.voice_id = voice_id

        # Build input
        video_input = {
            "character": character_config.dict(exclude_none=True),
            "voice": voice_config.dict(exclude_none=True)
        }

        # Add background if specified
        if background:
            if background.type == "color":
                video_input["background"] = {
                    "type": "color",
                    "value": background.value or "#000000"
                }
            elif background.type in ["image", "video"]:
                video_input["background"] = {
                    "type": background.type,
                    "url": background.url,
                    "play_style": background.play_style,
                    "fit": background.fit
                }

        return video_input

    async def _poll_video_status(self, video_id: str) -> str:
        """
        Poll HeyGen API for video generation status.

        Args:
            video_id: HeyGen video ID

        Returns:
            Video URL when generation is complete

        Raises:
            Exception: If generation fails or times out
        """
        start_time = datetime.utcnow()
        attempt = 0

        while True:
            attempt += 1
            elapsed = (datetime.utcnow() - start_time).total_seconds()

            # Check timeout
            if elapsed > self.config.max_wait_time:
                raise Exception(f"HeyGen generation timeout after {elapsed}s")

            try:
                # Check status
                response = await self.client.get(
                    "/v1/video_status.get",
                    params={"video_id": video_id}
                )
                response.raise_for_status()

                result = response.json()
                status = result["data"]["status"]

                logger.info(f"HeyGen video {video_id} status: {status} (attempt {attempt})")

                if status == "completed":
                    video_url = result["data"]["video_url"]
                    logger.info(f"HeyGen video completed: {video_url}")
                    return video_url

                elif status == "failed":
                    error = result["data"].get("error", "Unknown error")
                    raise Exception(f"HeyGen generation failed: {error}")

                elif status in ["pending", "processing", "waiting"]:
                    # Continue polling
                    await asyncio.sleep(self.config.poll_interval)
                    continue

                else:
                    raise Exception(f"Unknown HeyGen status: {status}")

            except httpx.HTTPStatusError as e:
                if attempt >= self.config.max_retries:
                    raise Exception(f"HeyGen status check failed: {e.response.text}")
                logger.warning(f"HeyGen status check error, retrying... ({attempt}/{self.config.max_retries})")
                await asyncio.sleep(self.config.poll_interval)

    def _estimate_cost(self, script: str, dimension: HeyGenDimensionConfig) -> float:
        """
        Estimate generation cost based on script length and video quality.

        HeyGen pricing (approximate):
        - $0.06-0.12 per minute depending on resolution
        """
        duration = self._estimate_duration(script)

        # Calculate cost per minute based on resolution
        pixels = dimension.width * dimension.height

        if pixels <= 720 * 1280:  # 720p vertical
            cost_per_minute = 0.06
        elif pixels <= 1080 * 1920:  # 1080p vertical
            cost_per_minute = 0.09
        else:  # Higher resolution
            cost_per_minute = 0.12

        return duration * cost_per_minute

    def _estimate_duration(self, script: str) -> float:
        """
        Estimate video duration from script.

        Average speaking rate: ~150 words per minute
        """
        word_count = len(script.split())
        duration_minutes = word_count / 150
        return duration_minutes

    async def list_avatars(self) -> list[Dict[str, Any]]:
        """
        List available HeyGen avatars.

        Returns:
            List of avatar objects with id, name, preview, etc.
        """
        try:
            response = await self.client.get("/v2/avatars")
            response.raise_for_status()
            result = response.json()
            return result["data"]["avatars"]
        except Exception as e:
            logger.error(f"Failed to list avatars: {str(e)}")
            raise

    async def list_voices(self) -> list[Dict[str, Any]]:
        """
        List available HeyGen voices.

        Returns:
            List of voice objects with id, name, language, etc.
        """
        try:
            response = await self.client.get("/v2/voices")
            response.raise_for_status()
            result = response.json()
            return result["data"]["voices"]
        except Exception as e:
            logger.error(f"Failed to list voices: {str(e)}")
            raise

    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed status of a HeyGen video.

        Args:
            video_id: HeyGen video ID

        Returns:
            Status object with status, progress, video_url, etc.
        """
        try:
            response = await self.client.get(
                "/v1/video_status.get",
                params={"video_id": video_id}
            )
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            logger.error(f"Failed to get video status: {str(e)}")
            raise

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
