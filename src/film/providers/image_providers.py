"""
Image generation provider implementations.

Supports:
- FAL.ai (primary, fast and affordable)
- Replicate (alternative)
"""

import asyncio
import logging
import time
from decimal import Decimal
from typing import Optional

import httpx

from film.models import ImageConfig, ImageResult
from film.providers.base import (
    BaseImageProvider,
    ProviderError,
    ProviderTimeoutError,
    ProviderAuthError,
)

logger = logging.getLogger(__name__)


# ============================================================================
# FAL.ai Image Provider
# ============================================================================


class FalImageProvider(BaseImageProvider):
    """
    FAL.ai image generation provider.

    Uses FLUX model for high-quality cinematic images.
    Cost: ~$0.003 per image
    """

    BASE_URL = "https://queue.fal.run"
    DEFAULT_MODEL = "fal-ai/flux/dev"
    MAX_POLL_ATTEMPTS = 60  # 3 minutes with 3s intervals
    POLL_INTERVAL = 3  # seconds

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, name="FAL.ai")

    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        config: ImageConfig,
    ) -> ImageResult:
        """
        Generate image using FAL.ai FLUX model.

        Process:
        1. Submit generation request
        2. Poll status until complete
        3. Download result
        """
        start_time = time.time()

        try:
            # Submit request
            logger.info(f"[{self.name}] Submitting image generation request")
            status_url, request_id = await self._submit_request(prompt, negative_prompt, config)

            # Poll for completion
            logger.info(f"[{self.name}] Polling for completion: {request_id}")
            result_data = await self.poll_status(status_url)

            # Extract image URL
            image_url = self._extract_image_url(result_data)
            width = result_data.get("images", [{}])[0].get("width", config.width)
            height = result_data.get("images", [{}])[0].get("height", config.height)

            generation_time = int(time.time() - start_time)

            logger.info(f"[{self.name}] Image generated successfully in {generation_time}s: {image_url}")

            return ImageResult(
                success=True,
                provider=self.name,
                model=config.model or self.DEFAULT_MODEL,
                cost_usd=self.estimate_cost(config),
                generation_time_seconds=generation_time,
                request_id=request_id,
                image_url=image_url,
                width=width,
                height=height,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ProviderAuthError(f"Authentication failed: {e}")
            raise ProviderError(f"HTTP error: {e}")

        except Exception as e:
            logger.error(f"[{self.name}] Generation failed: {e}")
            raise ProviderError(f"Image generation failed: {e}")

    async def _submit_request(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        config: ImageConfig,
    ) -> tuple[str, str]:
        """Submit generation request to FAL API"""
        model = config.model or self.DEFAULT_MODEL
        url = f"{self.BASE_URL}/{model}"

        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "image_size": {
                "width": config.width,
                "height": config.height,
            },
            "num_inference_steps": config.inference_steps,
            "guidance_scale": config.guidance_scale,
            "num_images": config.num_images,
            "enable_safety_checker": config.enable_safety_checker,
            "output_format": config.output_format,
        }

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        status_url = data.get("status_url")
        request_id = data.get("request_id")

        if not status_url:
            raise ProviderError(f"No status_url in response: {data}")

        return status_url, request_id

    async def poll_status(self, status_url: str) -> dict:
        """Poll status URL until generation completes"""
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
                    # Get the actual data from response_url
                    response_url = status_data.get("response_url")
                    if response_url:
                        data_response = await client.get(response_url, headers=headers)
                        data_response.raise_for_status()
                        return data_response.json()
                    return status_data

                if status == "FAILED":
                    error = status_data.get("error", "Unknown error")
                    raise ProviderError(f"Generation failed: {error}")

                # Still processing, wait and retry
                await asyncio.sleep(self.POLL_INTERVAL)

        raise ProviderTimeoutError(f"Polling timeout after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL}s")

    def _extract_image_url(self, result_data: dict) -> str:
        """Extract image URL from various possible locations in response"""
        # Try different possible locations
        image_url = (
            result_data.get("images", [{}])[0].get("url")
            or result_data.get("data", {}).get("images", [{}])[0].get("url")
            or result_data.get("image", {}).get("url")
        )

        if not image_url:
            raise ProviderError(f"No image URL found in response: {result_data}")

        return image_url

    def estimate_cost(self, config: ImageConfig) -> Decimal:
        """
        Estimate cost for FAL image generation.

        FAL pricing: ~$0.003 per image
        """
        base_cost_per_image = Decimal("0.003")
        return base_cost_per_image * config.num_images


# ============================================================================
# Replicate Image Provider
# ============================================================================


class ReplicateImageProvider(BaseImageProvider):
    """
    Replicate image generation provider.

    Alternative to FAL with different models available.
    """

    BASE_URL = "https://api.replicate.com/v1"
    MAX_POLL_ATTEMPTS = 60
    POLL_INTERVAL = 3

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, name="Replicate")

    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        config: ImageConfig,
    ) -> ImageResult:
        """Generate image using Replicate API"""
        # TODO: Implement Replicate-specific generation
        raise NotImplementedError("Replicate provider not yet implemented")

    async def poll_status(self, status_url: str) -> dict:
        """Poll Replicate prediction status"""
        # TODO: Implement Replicate polling
        raise NotImplementedError("Replicate polling not yet implemented")

    def estimate_cost(self, config: ImageConfig) -> Decimal:
        """Estimate cost for Replicate generation"""
        # Varies by model, placeholder
        return Decimal("0.005") * config.num_images


# ============================================================================
# Provider Registry
# ============================================================================


def create_image_provider(provider_name: str, api_key: str) -> BaseImageProvider:
    """Factory function to create image providers"""
    providers = {
        "fal": FalImageProvider,
        "replicate": ReplicateImageProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown image provider: {provider_name}. " f"Available: {list(providers.keys())}")

    return provider_class(api_key)
