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
    MAX_POLL_ATTEMPTS = 120  # 10 minutes with 5s intervals
    POLL_INTERVAL = 5  # seconds
    MAX_RETRIES = 3  # Retry failed requests

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
        1. Submit generation request (with retries)
        2. Poll status until complete
        3. Extract result

        Includes retry logic for transient failures.
        """
        start_time = time.time()
        last_error = None

        for retry in range(self.MAX_RETRIES):
            try:
                # Submit request
                if retry > 0:
                    logger.info(f"[{self.name}] Retry attempt {retry + 1}/{self.MAX_RETRIES}")
                    await asyncio.sleep(5)  # Wait before retry

                logger.info(f"[{self.name}] Submitting image generation request")
                logger.info(f"[{self.name}] Prompt: {prompt[:100]}...")
                status_url, request_id = await self._submit_request(prompt, negative_prompt, config)

                # Poll for completion
                logger.info(f"[{self.name}] Request submitted. ID: {request_id}")
                logger.info(f"[{self.name}] Polling for completion (max {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL}s)...")
                result_data = await self.poll_status(status_url)

                # Extract image URL
                image_url = self._extract_image_url(result_data)
                width = result_data.get("images", [{}])[0].get("width", config.width)
                height = result_data.get("images", [{}])[0].get("height", config.height)

                generation_time = int(time.time() - start_time)

                logger.info(f"[{self.name}] SUCCESS: Image generated in {generation_time}s")
                logger.info(f"[{self.name}] Image URL: {image_url[:80]}...")

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

            except ProviderTimeoutError as e:
                # Don't retry on timeout - it's a long wait issue, not transient
                logger.error(f"[{self.name}] Timeout error (not retrying): {e}")
                raise

            except ProviderAuthError as e:
                # Don't retry on auth errors
                logger.error(f"[{self.name}] Authentication error (not retrying): {e}")
                raise

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise ProviderAuthError(f"Authentication failed: {e}")

                last_error = e
                logger.warning(f"[{self.name}] HTTP error (attempt {retry + 1}/{self.MAX_RETRIES}): {e}")

                if retry == self.MAX_RETRIES - 1:
                    raise ProviderError(f"HTTP error after {self.MAX_RETRIES} retries: {e}")

            except Exception as e:
                last_error = e
                logger.warning(f"[{self.name}] Error (attempt {retry + 1}/{self.MAX_RETRIES}): {e}")

                if retry == self.MAX_RETRIES - 1:
                    logger.error(f"[{self.name}] All retries exhausted")
                    raise ProviderError(f"Image generation failed after {self.MAX_RETRIES} retries: {e}")

        # Shouldn't reach here, but just in case
        raise ProviderError(f"Image generation failed: {last_error}")

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

        logger.debug(f"[{self.name}] Submitting to {url}")
        logger.debug(f"[{self.name}] Image size: {config.width}x{config.height}")
        logger.debug(f"[{self.name}] Inference steps: {config.inference_steps}, Guidance: {config.guidance_scale}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            status_url = data.get("status_url")
            request_id = data.get("request_id")

            if not status_url:
                logger.error(f"[{self.name}] Invalid response: {data}")
                raise ProviderError(f"No status_url in response: {data}")

            logger.debug(f"[{self.name}] Status URL: {status_url}")
            return status_url, request_id

        except httpx.HTTPStatusError as e:
            logger.error(f"[{self.name}] HTTP {e.response.status_code}: {e.response.text}")
            raise

        except httpx.RequestError as e:
            logger.error(f"[{self.name}] Request error: {e}")
            raise ProviderError(f"Failed to submit request: {e}")

    async def poll_status(self, status_url: str) -> dict:
        """Poll status URL until generation completes"""
        headers = {
            "Authorization": f"Key {self.api_key}",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            last_logged_time = 0
            log_interval = 30  # Log every 30 seconds

            for attempt in range(self.MAX_POLL_ATTEMPTS):
                elapsed = attempt * self.POLL_INTERVAL

                # Log progress periodically
                if elapsed - last_logged_time >= log_interval:
                    logger.info(f"[{self.name}] Still generating... ({elapsed}s elapsed, attempt {attempt + 1}/{self.MAX_POLL_ATTEMPTS})")
                    last_logged_time = elapsed

                try:
                    response = await client.get(status_url, headers=headers)
                    response.raise_for_status()
                    status_data = response.json()

                    status = status_data.get("status")

                    logger.debug(f"[{self.name}] Status: {status} (attempt {attempt + 1})")

                    if status == "COMPLETED":
                        logger.info(f"[{self.name}] Generation completed after {elapsed}s")
                        # Get the actual data from response_url
                        response_url = status_data.get("response_url")
                        if response_url:
                            data_response = await client.get(response_url, headers=headers)
                            data_response.raise_for_status()
                            return data_response.json()
                        return status_data

                    if status == "FAILED":
                        error = status_data.get("error", "Unknown error")
                        logger.error(f"[{self.name}] Generation failed: {error}")
                        raise ProviderError(f"Generation failed: {error}")

                    # Still processing, wait and retry
                    await asyncio.sleep(self.POLL_INTERVAL)

                except httpx.HTTPError as e:
                    logger.warning(f"[{self.name}] HTTP error during polling (attempt {attempt + 1}): {e}")
                    if attempt < self.MAX_POLL_ATTEMPTS - 1:
                        await asyncio.sleep(self.POLL_INTERVAL)
                        continue
                    raise

        total_time = self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL
        logger.error(f"[{self.name}] Timeout after {total_time}s ({self.MAX_POLL_ATTEMPTS} attempts)")
        raise ProviderTimeoutError(
            f"Polling timeout after {total_time}s. "
            f"The FAL API is taking longer than expected. "
            f"This might be due to high load or complex image generation."
        )

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
    MAX_POLL_ATTEMPTS = 120  # 10 minutes with 5s intervals
    POLL_INTERVAL = 5  # seconds
    MAX_RETRIES = 3  # Retry failed requests

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
