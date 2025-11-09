"""
Replicate image generation client for character creation.

Simplified async client for character image generation.
"""

import asyncio
import logging
import httpx
import os
from typing import Optional

logger = logging.getLogger(__name__)


class ReplicateClient:
    """Simplified Replicate client for character image generation."""

    BASE_URL = "https://api.replicate.com/v1"
    DEFAULT_MODEL = "stability-ai/sdxl"
    MAX_POLL_ATTEMPTS = 120
    POLL_INTERVAL = 5

    def __init__(self):
        """Initialize Replicate client with API key from environment."""
        self.api_key = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_key:
            logger.warning("REPLICATE_API_TOKEN not set in environment")

    async def generate_image(
        self,
        prompt: str,
        model: str = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> str:
        """
        Generate a single image and return the URL.

        Args:
            prompt: Text description of the image
            model: Model identifier (defaults to SDXL)
            negative_prompt: Things to avoid in the image
            seed: Random seed for reproducibility
            width: Image width
            height: Image height

        Returns:
            URL of the generated image

        Raises:
            Exception: If generation fails
        """
        if not self.api_key:
            raise ValueError("REPLICATE_API_TOKEN not set. Please set environment variable.")

        model_version = model or self.DEFAULT_MODEL

        payload = {
            "version": model_version,
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
            }
        }

        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt

        if seed is not None:
            payload["input"]["seed"] = seed

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }

        logger.info(f"Submitting Replicate image generation request")

        try:
            # Submit prediction
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/predictions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                prediction = response.json()

            prediction_url = prediction.get("urls", {}).get("get")
            if not prediction_url:
                raise Exception(f"No prediction URL in response: {prediction}")

            # Poll for completion
            logger.info(f"Polling for completion...")
            result_data = await self._poll_prediction(prediction_url, headers)

            # Extract image URL
            image_url = self._extract_image_url(result_data)
            logger.info(f"Image generated successfully: {image_url[:80]}...")

            return image_url

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Replicate API error: {e.response.text}")

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    async def _poll_prediction(self, prediction_url: str, headers: dict) -> dict:
        """Poll prediction URL until generation completes."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(self.MAX_POLL_ATTEMPTS):
                try:
                    response = await client.get(prediction_url, headers=headers)
                    response.raise_for_status()
                    prediction = response.json()

                    status = prediction.get("status")

                    if status == "succeeded":
                        return prediction

                    if status == "failed":
                        error = prediction.get("error", "Unknown error")
                        raise Exception(f"Generation failed: {error}")

                    # Still processing, wait and retry
                    await asyncio.sleep(self.POLL_INTERVAL)

                except httpx.HTTPError as e:
                    if attempt < self.MAX_POLL_ATTEMPTS - 1:
                        await asyncio.sleep(self.POLL_INTERVAL)
                        continue
                    raise

        raise Exception(f"Polling timeout after {self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL}s")

    def _extract_image_url(self, result_data: dict) -> str:
        """Extract image URL from response."""
        output = result_data.get("output")

        if isinstance(output, list) and len(output) > 0:
            return output[0]
        elif isinstance(output, str):
            return output

        raise Exception(f"No image URL found in response: {result_data}")
