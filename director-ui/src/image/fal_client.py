"""
FAL.ai image generation client for character creation.

Simplified async client for character image generation.
"""

import asyncio
import logging
import httpx
import os
from typing import Optional

logger = logging.getLogger(__name__)


class FALClient:
    """Simplified FAL.ai client for character image generation."""

    BASE_URL = "https://queue.fal.run"
    DEFAULT_MODEL = "fal-ai/flux/dev"
    MAX_POLL_ATTEMPTS = 120
    POLL_INTERVAL = 5

    def __init__(self):
        """Initialize FAL client with API key from environment."""
        self.api_key = os.getenv("FAL_API_KEY")
        if not self.api_key:
            logger.warning("FAL_API_KEY not set in environment")

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
            model: Model ID (defaults to flux/dev)
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
            raise ValueError("FAL_API_KEY not set. Please set environment variable.")

        model_id = model or self.DEFAULT_MODEL
        url = f"{self.BASE_URL}/{model_id}"

        payload = {
            "prompt": prompt,
            "image_size": {"width": width, "height": height},
            "num_inference_steps": 12,  # FAL API max is 12 for flux models
            "guidance_scale": 3.5,
            "num_images": 1,
            "enable_safety_checker": False,
        }

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if seed is not None:
            payload["seed"] = seed

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        logger.info(f"Submitting FAL image generation request")

        try:
            # Submit request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            status_url = data.get("status_url")
            if not status_url:
                raise Exception(f"No status_url in response: {data}")

            # Poll for completion
            logger.info(f"Polling for completion...")
            result_data = await self._poll_status(status_url)

            # Extract image URL
            image_url = self._extract_image_url(result_data)
            logger.info(f"Image generated successfully: {image_url[:80]}...")

            return image_url

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"FAL API error: {e.response.text}")

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    async def _poll_status(self, status_url: str) -> dict:
        """Poll status URL until generation completes."""
        headers = {
            "Authorization": f"Key {self.api_key}",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(self.MAX_POLL_ATTEMPTS):
                try:
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
        image_url = (
            result_data.get("images", [{}])[0].get("url")
            or result_data.get("data", {}).get("images", [{}])[0].get("url")
            or result_data.get("image", {}).get("url")
        )

        if not image_url:
            raise Exception(f"No image URL found in response: {result_data}")

        return image_url
