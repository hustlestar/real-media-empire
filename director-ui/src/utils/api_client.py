"""HTTP client for bot to communicate with the API."""

import logging
from typing import Optional, Dict, Any
import httpx
from config.settings import BotConfig

logger = logging.getLogger(__name__)


class APIClient:
    """Client for the bot to communicate with the API."""

    def __init__(self, config: BotConfig):
        self.base_url = f"http://{config.api_host}:{config.api_port}/api"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_content_from_url(
        self,
        url: str,
        source_type: str,
        user_id: int,
        force_reprocess: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Create content from URL via API."""
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/content/from-url",
                json={
                    "url": url,
                    "source_type": source_type,
                    "user_id": user_id,
                    "force_reprocess": force_reprocess
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating content via API: {e}")
            return None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()