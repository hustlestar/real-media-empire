"""
Video generation provider implementations.

Supports:
- Minimax (cheap: ~$0.05 per 6s)
- Kling (premium: ~$1.84 per 10s)
- Runway (ultra-premium, future)
"""

import asyncio
import logging
import time
from decimal import Decimal
from typing import Optional

import httpx

from film.models import VideoConfig, VideoResult
from film.providers.base import (
    BaseVideoProvider,
    ProviderError,
    ProviderTimeoutError,
    ProviderAuthError,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Minimax Video Provider (via FAL)
# ============================================================================


class MinimaxVideoProvider(BaseVideoProvider):
    """
    Minimax video generation provider (via FAL.ai).

    Fast and affordable image-to-video animation.
    Cost: ~$0.05 per 6 seconds
    Duration: 5-6 seconds
    """

    BASE_URL = "https://queue.fal.run/fal-ai/minimax/video-01"
    MAX_POLL_ATTEMPTS = 120  # Videos take longer, 10 minutes
    POLL_INTERVAL = 5  # seconds

    COST_PER_6_SECONDS = Decimal("0.05")

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, name="Minimax")

    async def generate(
        self,
        image_url: str,
        prompt: str,
        config: VideoConfig,
    ) -> VideoResult:
        """
        Animate image to video using Minimax.

        Process:
        1. Submit animation request with image URL
        2. Poll until video ready
        3. Return video URL
        """
        start_time = time.time()

        try:
            logger.info(f"[{self.name}] Submitting video animation request")
            status_url, request_id = await self._submit_request(image_url, prompt, config)

            logger.info(f"[{self.name}] Polling for completion: {request_id}")
            result_data = await self.poll_status(status_url)

            # Extract video URL
            video_url = self._extract_video_url(result_data)
            duration = config.duration
            fps = config.fps

            generation_time = int(time.time() - start_time)

            logger.info(f"[{self.name}] Video generated in {generation_time}s: {video_url}")

            return VideoResult(
                success=True,
                provider=self.name,
                model="minimax-video-01",
                cost_usd=self.estimate_cost(config),
                generation_time_seconds=generation_time,
                request_id=request_id,
                video_url=video_url,
                duration=float(duration),
                fps=fps,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ProviderAuthError(f"Authentication failed: {e}")
            raise ProviderError(f"HTTP error: {e}")

        except Exception as e:
            logger.error(f"[{self.name}] Generation failed: {e}")
            raise ProviderError(f"Video generation failed: {e}")

    async def _submit_request(
        self,
        image_url: str,
        prompt: str,
        config: VideoConfig,
    ) -> tuple[str, str]:
        """Submit video animation request to Minimax via FAL"""
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": str(config.duration),  # Minimax expects string
        }

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        status_url = data.get("status_url")
        request_id = data.get("request_id")

        if not status_url:
            raise ProviderError(f"No status_url in response: {data}")

        return status_url, request_id

    async def poll_status(self, status_url: str) -> dict:
        """Poll status URL until video generation completes"""
        headers = {
            "Authorization": f"Key {self.api_key}",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(self.MAX_POLL_ATTEMPTS):
                response = await client.get(status_url, headers=headers)
                response.raise_for_status()
                status_data = response.json()

                status = status_data.get("status")

                if status == "COMPLETED":
                    # The response might have data directly or in response_url
                    response_url = status_data.get("response_url")
                    if response_url:
                        data_response = await client.get(response_url, headers=headers)
                        data_response.raise_for_status()
                        return data_response.json()
                    return status_data

                if status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    raise ProviderError(f"Video generation failed: {error}")

                # Still processing
                await asyncio.sleep(self.POLL_INTERVAL)

        raise ProviderTimeoutError(f"Polling timeout after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL}s")

    def _extract_video_url(self, result_data: dict) -> str:
        """Extract video URL from response"""
        # Try different possible locations
        video_url = (
            result_data.get("video", {}).get("url")
            or result_data.get("data", {}).get("video", {}).get("url")
            or result_data.get("output")  # Sometimes output is direct URL
        )

        if not video_url:
            raise ProviderError(f"No video URL found in response: {result_data}")

        return video_url

    def estimate_cost(self, config: VideoConfig) -> Decimal:
        """
        Estimate cost for Minimax video generation.

        Pricing: ~$0.05 per 6 seconds
        """
        # Round up to nearest 6 seconds
        duration_in_6s_units = (config.duration + 5) // 6
        return self.COST_PER_6_SECONDS * duration_in_6s_units


# ============================================================================
# Kling Video Provider (via FAL)
# ============================================================================


class KlingVideoProvider(BaseVideoProvider):
    """
    Kling video generation provider (via FAL.ai).

    Higher quality than Minimax, more expensive.
    Cost: ~$1.84 per 10 seconds
    Duration: 5-10 seconds
    """

    BASE_URL = "https://queue.fal.run/fal-ai/kling-video/v1/standard/image-to-video"
    MAX_POLL_ATTEMPTS = 180  # Kling can take longer
    POLL_INTERVAL = 5

    COST_PER_10_SECONDS = Decimal("1.84")

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, name="Kling")

    async def generate(
        self,
        image_url: str,
        prompt: str,
        config: VideoConfig,
    ) -> VideoResult:
        """Animate image to video using Kling"""
        start_time = time.time()

        try:
            logger.info(f"[{self.name}] Submitting video animation request")
            status_url, request_id = await self._submit_request(image_url, prompt, config)

            logger.info(f"[{self.name}] Polling for completion: {request_id}")
            result_data = await self.poll_status(status_url)

            video_url = self._extract_video_url(result_data)
            duration = config.duration
            fps = config.fps

            generation_time = int(time.time() - start_time)

            logger.info(f"[{self.name}] Video generated in {generation_time}s: {video_url}")

            return VideoResult(
                success=True,
                provider=self.name,
                model="kling-v1-standard",
                cost_usd=self.estimate_cost(config),
                generation_time_seconds=generation_time,
                request_id=request_id,
                video_url=video_url,
                duration=float(duration),
                fps=fps,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ProviderAuthError(f"Authentication failed: {e}")
            raise ProviderError(f"HTTP error: {e}")

        except Exception as e:
            logger.error(f"[{self.name}] Generation failed: {e}")
            raise ProviderError(f"Video generation failed: {e}")

    async def _submit_request(
        self,
        image_url: str,
        prompt: str,
        config: VideoConfig,
    ) -> tuple[str, str]:
        """Submit request to Kling via FAL"""
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "duration": config.duration,
            "aspect_ratio": "16:9",  # Cinematic
            "mode": config.mode,  # 'standard' or 'professional'
        }

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        status_url = data.get("status_url")
        request_id = data.get("request_id")

        if not status_url:
            raise ProviderError(f"No status_url in response: {data}")

        return status_url, request_id

    async def poll_status(self, status_url: str) -> dict:
        """Poll Kling status until complete"""
        headers = {
            "Authorization": f"Key {self.api_key}",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(self.MAX_POLL_ATTEMPTS):
                response = await client.get(status_url, headers=headers)
                response.raise_for_status()
                status_data = response.json()

                status = status_data.get("status")

                if status == "COMPLETED":
                    response_url = status_data.get("response_url")
                    if response_url:
                        data_response = await client.get(response_url, headers=headers)
                        data_response.raise_for_status()
                        return data_response.json()
                    return status_data

                if status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    raise ProviderError(f"Video generation failed: {error}")

                await asyncio.sleep(self.POLL_INTERVAL)

        raise ProviderTimeoutError(f"Polling timeout after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL}s")

    def _extract_video_url(self, result_data: dict) -> str:
        """Extract video URL from Kling response"""
        video_url = result_data.get("video", {}).get("url") or result_data.get("data", {}).get("video", {}).get("url") or result_data.get("output")

        if not video_url:
            raise ProviderError(f"No video URL found in response: {result_data}")

        return video_url

    def estimate_cost(self, config: VideoConfig) -> Decimal:
        """
        Estimate cost for Kling video generation.

        Pricing: ~$1.84 per 10 seconds
        """
        duration_in_10s_units = (config.duration + 9) // 10
        return self.COST_PER_10_SECONDS * duration_in_10s_units


# ============================================================================
# Runway Video Provider
# ============================================================================


class RunwayVideoProvider(BaseVideoProvider):
    """
    Runway Gen-3 video provider.

    Ultra-premium quality, very expensive.
    Cost: ~$0.05 per frame (24fps = $1.20/second!)
    """

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, name="Runway")

    async def generate(
        self,
        image_url: str,
        prompt: str,
        config: VideoConfig,
    ) -> VideoResult:
        """Generate video using Runway Gen-3"""
        # TODO: Implement Runway-specific generation
        raise NotImplementedError("Runway provider not yet implemented")

    async def poll_status(self, status_url: str) -> dict:
        """Poll Runway status"""
        raise NotImplementedError("Runway polling not yet implemented")

    def estimate_cost(self, config: VideoConfig) -> Decimal:
        """Estimate Runway costs (very expensive!)"""
        cost_per_frame = Decimal("0.05")
        total_frames = config.duration * config.fps
        return cost_per_frame * total_frames


# ============================================================================
# Provider Registry
# ============================================================================


def create_video_provider(provider_name: str, api_key: str) -> BaseVideoProvider:
    """Factory function to create video providers"""
    providers = {
        "minimax": MinimaxVideoProvider,
        "kling": KlingVideoProvider,
        "runway": RunwayVideoProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown video provider: {provider_name}. " f"Available: {list(providers.keys())}")

    return provider_class(api_key)
