"""
Stock Video Search - Pexels and Pixabay integration

Provides searching and downloading stock videos for avatar backgrounds.
"""

import httpx
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl
import logging

logger = logging.getLogger(__name__)


class VideoResult(BaseModel):
    """Stock video search result."""
    id: str
    title: str
    description: Optional[str] = None
    duration: int  # Duration in seconds
    width: int
    height: int
    thumbnail_url: HttpUrl
    video_url: HttpUrl  # Direct video URL
    video_files: List[dict]  # Available quality options
    user: str  # Creator name
    provider: Literal["pexels", "pixabay"]
    tags: List[str] = []


class StockVideoSearcher:
    """
    Search stock videos from multiple providers.

    Providers:
    - Pexels (primary)
    - Pixabay (fallback)
    """

    def __init__(self, pexels_api_key: str, pixabay_api_key: Optional[str] = None):
        """
        Initialize stock video searcher.

        Args:
            pexels_api_key: Pexels API key (get from https://www.pexels.com/api/)
            pixabay_api_key: Pixabay API key (optional, get from https://pixabay.com/api/docs/)
        """
        self.pexels_api_key = pexels_api_key
        self.pixabay_api_key = pixabay_api_key

        self.pexels_client = httpx.AsyncClient(
            base_url="https://api.pexels.com",
            headers={"Authorization": pexels_api_key},
            timeout=30.0
        )

        if pixabay_api_key:
            self.pixabay_client = httpx.AsyncClient(
                base_url="https://pixabay.com/api",
                timeout=30.0
            )
        else:
            self.pixabay_client = None

    async def search_videos(
        self,
        query: str,
        per_page: int = 10,
        orientation: Optional[Literal["landscape", "portrait", "square"]] = None,
        size: Optional[Literal["large", "medium", "small"]] = None,
        provider: Optional[Literal["pexels", "pixabay", "both"]] = "both"
    ) -> List[VideoResult]:
        """
        Search for stock videos across providers.

        Args:
            query: Search query (e.g., "business meeting", "nature", "technology")
            per_page: Number of results per provider
            orientation: Video orientation filter
            size: Preferred video size
            provider: Which provider(s) to search

        Returns:
            List of video results sorted by relevance
        """
        results = []

        # Search Pexels
        if provider in ["pexels", "both"]:
            try:
                pexels_results = await self._search_pexels(query, per_page, orientation, size)
                results.extend(pexels_results)
                logger.info(f"Found {len(pexels_results)} videos from Pexels for query: {query}")
            except Exception as e:
                logger.error(f"Pexels search failed: {e}")

        # Search Pixabay (fallback)
        if provider in ["pixabay", "both"] and self.pixabay_client:
            try:
                pixabay_results = await self._search_pixabay(query, per_page, orientation)
                results.extend(pixabay_results)
                logger.info(f"Found {len(pixabay_results)} videos from Pixabay for query: {query}")
            except Exception as e:
                logger.error(f"Pixabay search failed: {e}")

        return results

    async def _search_pexels(
        self,
        query: str,
        per_page: int,
        orientation: Optional[str],
        size: Optional[str]
    ) -> List[VideoResult]:
        """Search Pexels video library."""
        params = {
            "query": query,
            "per_page": min(per_page, 80),  # Pexels max is 80
        }

        if orientation:
            params["orientation"] = orientation
        if size:
            params["size"] = size

        response = await self.pexels_client.get("/videos/search", params=params)
        response.raise_for_status()

        data = response.json()
        results = []

        for video in data.get("videos", []):
            # Get best quality video file
            video_files = video.get("video_files", [])
            if not video_files:
                continue

            # Sort by quality (prefer HD)
            video_files_sorted = sorted(
                video_files,
                key=lambda x: x.get("width", 0) * x.get("height", 0),
                reverse=True
            )

            best_file = video_files_sorted[0]

            results.append(VideoResult(
                id=str(video["id"]),
                title=f"Pexels Video {video['id']}",
                description=None,
                duration=video.get("duration", 0),
                width=video.get("width", best_file.get("width", 1920)),
                height=video.get("height", best_file.get("height", 1080)),
                thumbnail_url=video.get("image"),
                video_url=best_file.get("link"),
                video_files=video_files,
                user=video.get("user", {}).get("name", "Unknown"),
                provider="pexels",
                tags=[]
            ))

        return results

    async def _search_pixabay(
        self,
        query: str,
        per_page: int,
        orientation: Optional[str]
    ) -> List[VideoResult]:
        """Search Pixabay video library."""
        if not self.pixabay_api_key:
            return []

        params = {
            "key": self.pixabay_api_key,
            "q": query,
            "video_type": "all",
            "per_page": min(per_page, 200),  # Pixabay max is 200
        }

        response = await self.pixabay_client.get("/", params=params)
        response.raise_for_status()

        data = response.json()
        results = []

        for video in data.get("hits", []):
            # Get video URL (prefer large size)
            video_files = []
            video_url = video.get("videos", {}).get("large", {}).get("url")
            if not video_url:
                video_url = video.get("videos", {}).get("medium", {}).get("url")
            if not video_url:
                video_url = video.get("videos", {}).get("small", {}).get("url")

            if not video_url:
                continue

            # Build video files list
            for size, info in video.get("videos", {}).items():
                if info and info.get("url"):
                    video_files.append({
                        "quality": size,
                        "width": info.get("width", 0),
                        "height": info.get("height", 0),
                        "link": info["url"],
                        "size": info.get("size", 0)
                    })

            results.append(VideoResult(
                id=str(video["id"]),
                title=video.get("tags", "Video").split(",")[0].strip(),
                description=video.get("tags"),
                duration=video.get("duration", 0),
                width=video.get("videos", {}).get("large", {}).get("width", 1920),
                height=video.get("videos", {}).get("large", {}).get("height", 1080),
                thumbnail_url=video.get("userImageURL", video.get("previewURL", "")),
                video_url=video_url,
                video_files=video_files,
                user=video.get("user", "Unknown"),
                provider="pixabay",
                tags=video.get("tags", "").split(",")
            ))

        return results

    async def get_video_download_url(
        self,
        video_id: str,
        provider: Literal["pexels", "pixabay"],
        quality: Optional[str] = "hd"
    ) -> str:
        """
        Get direct download URL for a specific video.

        Args:
            video_id: Video ID
            provider: Video provider
            quality: Preferred quality (hd, sd, etc.)

        Returns:
            Direct download URL
        """
        if provider == "pexels":
            response = await self.pexels_client.get(f"/videos/videos/{video_id}")
            response.raise_for_status()

            data = response.json()
            video_files = data.get("video_files", [])

            # Find requested quality
            for vf in video_files:
                if quality.lower() in vf.get("quality", "").lower():
                    return vf["link"]

            # Return best quality if requested not found
            if video_files:
                return video_files[0]["link"]

        elif provider == "pixabay" and self.pixabay_client:
            params = {
                "key": self.pixabay_api_key,
                "id": video_id
            }
            response = await self.pixabay_client.get("/", params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("hits"):
                video = data["hits"][0]
                videos = video.get("videos", {})

                # Try to get requested quality
                if quality in videos and videos[quality].get("url"):
                    return videos[quality]["url"]

                # Fallback to large -> medium -> small
                for size in ["large", "medium", "small"]:
                    if size in videos and videos[size].get("url"):
                        return videos[size]["url"]

        raise ValueError(f"Could not find video download URL for {provider}:{video_id}")

    async def close(self):
        """Close HTTP clients."""
        await self.pexels_client.aclose()
        if self.pixabay_client:
            await self.pixabay_client.aclose()
