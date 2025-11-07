"""
VEED.io Talking Avatar Provider via FAL.ai

Creates AI talking avatar videos from a static photo + audio with automatic lip-sync.
This is an alternative to HeyGen for faceless content creation.
"""

import asyncio
from typing import Optional, Literal
from pydantic import BaseModel, HttpUrl
import httpx

from ..base_provider import VideoProvider, VideoGenerationResult


class VEEDConfig(BaseModel):
    """Configuration for VEED provider via FAL.ai."""
    fal_api_key: str
    base_url: str = "https://queue.fal.run"
    poll_interval: int = 10
    max_wait_time: int = 600  # 10 minutes
    max_retries: int = 3


class VEEDProvider(VideoProvider):
    """
    VEED.io talking avatar provider using FAL.ai API.

    Creates AI talking avatar videos where a static photo speaks
    with automatic lip-sync matching the provided audio.

    Use cases:
    - Faceless content creation
    - UGC-style videos
    - Educational content
    - Product demonstrations
    - Social media shorts
    """

    def __init__(self, config: VEEDConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Key {config.fal_api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def generate_talking_avatar(
        self,
        image_url: str,
        audio_url: str,
        resolution: Literal["480p", "720p", "1080p"] = "720p"
    ) -> VideoGenerationResult:
        """
        Generate a talking avatar video from a photo and audio.

        Args:
            image_url: URL to the source photo (person's face)
            audio_url: URL to the audio file (voice-over)
            resolution: Video resolution (480p, 720p, or 1080p)

        Returns:
            VideoGenerationResult with the generated video URL

        Raises:
            Exception: If generation fails or times out
        """
        # Submit generation request
        payload = {
            "image_url": image_url,
            "audio_url": audio_url,
            "resolution": resolution
        }

        response = await self.client.post(
            f"{self.config.base_url}/veed/fabric-1.0",
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        request_id = result.get("request_id")
        if not request_id:
            raise Exception(f"No request_id in VEED response: {result}")

        # Poll for completion
        video_url = await self._poll_status(request_id)

        return VideoGenerationResult(
            video_id=request_id,
            video_url=video_url,
            provider="veed",
            duration=None,  # Unknown until video is analyzed
            cost=0.10,  # Approximate cost per generation
            metadata={
                "image_url": image_url,
                "audio_url": audio_url,
                "resolution": resolution,
                "model": "veed-fabric-1.0"
            }
        )

    async def _poll_status(self, request_id: str) -> str:
        """
        Poll VEED generation status until complete.

        Args:
            request_id: The request ID from initial submission

        Returns:
            URL to the generated video

        Raises:
            TimeoutError: If generation exceeds max_wait_time
            Exception: If generation fails
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > self.config.max_wait_time:
                raise TimeoutError(
                    f"VEED generation timed out after {self.config.max_wait_time}s"
                )

            response = await self.client.get(
                f"{self.config.base_url}/veed/fabric-1.0/requests/{request_id}"
            )
            response.raise_for_status()
            result = response.json()

            status = result.get("status", "").upper()

            if status == "COMPLETED":
                video_data = result.get("video", {})
                video_url = video_data.get("url")
                if not video_url:
                    raise Exception(f"No video URL in completed response: {result}")
                return video_url

            elif status == "FAILED":
                error = result.get("error", "Unknown error")
                raise Exception(f"VEED generation failed: {error}")

            elif status in ["PENDING", "IN_PROGRESS", "IN_QUEUE"]:
                # Still processing
                await asyncio.sleep(self.config.poll_interval)
                continue

            else:
                # Unknown status
                raise Exception(f"Unknown VEED status: {status}")

    async def generate(self, *args, **kwargs) -> VideoGenerationResult:
        """
        Main generate method for VideoProvider interface.
        Routes to generate_talking_avatar.
        """
        return await self.generate_talking_avatar(*args, **kwargs)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
