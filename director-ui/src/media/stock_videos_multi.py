"""
Enhanced Stock Video Search - Multiple Providers

Providers:
- Pexels (100k+ videos, high quality)
- Pixabay (50k+ videos, good variety)
- Videezy (100k+ videos, free + premium)
- Coverr (5k+ curated videos, niche content)
- Videvo (100k+ videos, mixed quality)
"""

import httpx
from typing import List, Optional, Literal
from pydantic import BaseModel, HttpUrl
import logging
import asyncio

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
    provider: Literal["pexels", "pixabay", "videezy", "coverr", "videvo"]
    tags: List[str] = []
    relevance_score: float = 1.0  # Higher = more relevant


class MultiProviderVideoSearcher:
    """
    Search stock videos from FIVE providers for maximum relevance.

    **Providers:**
    1. Pexels - High quality, curated
    2. Pixabay - Good variety
    3. Videezy - Large collection, free + premium
    4. Coverr - Curated niche content
    5. Videvo - Mixed quality, large volume

    **Strategy:**
    - Search all providers in parallel
    - Score results by relevance
    - Return best matches across all providers
    """

    def __init__(
        self,
        pexels_api_key: str,
        pixabay_api_key: Optional[str] = None,
        videezy_api_key: Optional[str] = None,
        coverr_api_key: Optional[str] = None
    ):
        """
        Initialize multi-provider searcher.

        Args:
            pexels_api_key: Pexels API key (get from https://www.pexels.com/api/)
            pixabay_api_key: Pixabay API key (https://pixabay.com/api/docs/)
            videezy_api_key: Videezy API key (https://www.videezy.com/api)
            coverr_api_key: Coverr API key (optional)
        """
        self.pexels_api_key = pexels_api_key
        self.pixabay_api_key = pixabay_api_key
        self.videezy_api_key = videezy_api_key
        self.coverr_api_key = coverr_api_key

        # Pexels client
        self.pexels_client = httpx.AsyncClient(
            base_url="https://api.pexels.com",
            headers={"Authorization": pexels_api_key},
            timeout=30.0
        )

        # Pixabay client
        if pixabay_api_key:
            self.pixabay_client = httpx.AsyncClient(
                base_url="https://pixabay.com/api",
                timeout=30.0
            )
        else:
            self.pixabay_client = None

        # Videezy client (uses screen scraping or their API if available)
        self.videezy_client = httpx.AsyncClient(
            base_url="https://www.videezy.com",
            timeout=30.0
        )

        # Coverr client (simple JSON API, no key required!)
        self.coverr_client = httpx.AsyncClient(
            base_url="https://coverr.co/api",
            timeout=30.0
        )

        # Videvo client
        self.videvo_client = httpx.AsyncClient(
            base_url="https://www.videvo.net",
            timeout=30.0
        )

    async def search_all_providers(
        self,
        query: str,
        per_provider: int = 5,
        orientation: Optional[Literal["landscape", "portrait", "square"]] = None,
        min_duration: Optional[int] = None,  # Minimum duration in seconds
        max_duration: Optional[int] = None   # Maximum duration in seconds
    ) -> List[VideoResult]:
        """
        Search ALL providers in parallel and return combined, ranked results.

        Args:
            query: Search query
            per_provider: Max results per provider
            orientation: Video orientation filter
            min_duration: Minimum video duration filter
            max_duration: Maximum video duration filter

        Returns:
            Combined, ranked list of videos from all providers
        """
        # Search all providers in parallel
        tasks = [
            self._search_pexels(query, per_provider, orientation),
            self._search_pixabay(query, per_provider, orientation) if self.pixabay_client else self._empty_results(),
            self._search_videezy(query, per_provider),
            self._search_coverr(query, per_provider),
            self._search_videvo(query, per_provider),
        ]

        results_by_provider = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine all results
        all_videos = []
        for i, results in enumerate(results_by_provider):
            if isinstance(results, Exception):
                provider_names = ["pexels", "pixabay", "videezy", "coverr", "videvo"]
                logger.error(f"{provider_names[i]} search failed: {results}")
                continue

            all_videos.extend(results)

        # Filter by duration if specified
        if min_duration or max_duration:
            all_videos = [
                v for v in all_videos
                if (min_duration is None or v.duration >= min_duration) and
                   (max_duration is None or v.duration <= max_duration)
            ]

        # Score and rank videos by relevance
        all_videos = self._rank_by_relevance(all_videos, query)

        logger.info(f"Found {len(all_videos)} total videos across all providers for: {query}")

        return all_videos

    def _rank_by_relevance(self, videos: List[VideoResult], query: str) -> List[VideoResult]:
        """
        Rank videos by relevance to query.

        Factors:
        - Query words in title/tags
        - Provider quality score
        - Video duration (prefer 10-60 seconds for backgrounds)
        """
        query_words = set(query.lower().split())

        provider_quality = {
            "pexels": 1.2,      # Highest quality
            "coverr": 1.15,     # Curated
            "videezy": 1.0,     # Good variety
            "pixabay": 0.95,    # Good
            "videvo": 0.85      # Mixed quality
        }

        for video in videos:
            score = provider_quality.get(video.provider, 1.0)

            # Boost if query words in title
            title_words = set(video.title.lower().split())
            matches = len(query_words & title_words)
            score += matches * 0.3

            # Boost if query words in tags
            tag_words = set(" ".join(video.tags).lower().split())
            tag_matches = len(query_words & tag_words)
            score += tag_matches * 0.2

            # Prefer videos 10-60 seconds (good for backgrounds)
            if 10 <= video.duration <= 60:
                score += 0.2
            elif video.duration < 5:
                score -= 0.3  # Too short

            video.relevance_score = score

        # Sort by relevance score (highest first)
        return sorted(videos, key=lambda v: v.relevance_score, reverse=True)

    async def _empty_results(self) -> List[VideoResult]:
        """Return empty results for disabled providers."""
        return []

    async def _search_pexels(
        self,
        query: str,
        per_page: int,
        orientation: Optional[str]
    ) -> List[VideoResult]:
        """Search Pexels video library."""
        try:
            params = {"query": query, "per_page": min(per_page, 80)}
            if orientation:
                params["orientation"] = orientation

            response = await self.pexels_client.get("/videos/search", params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            for video in data.get("videos", []):
                video_files = video.get("video_files", [])
                if not video_files:
                    continue

                video_files_sorted = sorted(
                    video_files,
                    key=lambda x: x.get("width", 0) * x.get("height", 0),
                    reverse=True
                )

                best_file = video_files_sorted[0]

                results.append(VideoResult(
                    id=f"pexels_{video['id']}",
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
        except Exception as e:
            logger.error(f"Pexels search failed: {e}")
            return []

    async def _search_pixabay(
        self,
        query: str,
        per_page: int,
        orientation: Optional[str]
    ) -> List[VideoResult]:
        """Search Pixabay video library."""
        if not self.pixabay_api_key:
            return []

        try:
            params = {
                "key": self.pixabay_api_key,
                "q": query,
                "video_type": "all",
                "per_page": min(per_page, 200)
            }

            response = await self.pixabay_client.get("/", params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            for video in data.get("hits", []):
                video_url = (video.get("videos", {}).get("large", {}).get("url") or
                           video.get("videos", {}).get("medium", {}).get("url") or
                           video.get("videos", {}).get("small", {}).get("url"))

                if not video_url:
                    continue

                video_files = []
                for size, info in video.get("videos", {}).items():
                    if info and info.get("url"):
                        video_files.append({
                            "quality": size,
                            "width": info.get("width", 0),
                            "height": info.get("height", 0),
                            "link": info["url"]
                        })

                results.append(VideoResult(
                    id=f"pixabay_{video['id']}",
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
        except Exception as e:
            logger.error(f"Pixabay search failed: {e}")
            return []

    async def _search_videezy(self, query: str, per_page: int) -> List[VideoResult]:
        """Search Videezy (via web scraping or API if available)."""
        try:
            # Videezy has a JSON search endpoint
            params = {
                "s": query,
                "content-type": "video",
                "per_page": per_page
            }

            response = await self.videezy_client.get("/search", params=params)

            # Note: Videezy might require scraping. For now, return empty
            # In production, implement proper scraping or use their API if available
            logger.info("Videezy search not fully implemented (requires API key or scraping)")
            return []

        except Exception as e:
            logger.error(f"Videezy search failed: {e}")
            return []

    async def _search_coverr(self, query: str, per_page: int) -> List[VideoResult]:
        """Search Coverr (free, curated, no API key required!)."""
        try:
            # Coverr has a simple public API
            response = await self.coverr_client.get("/videos")
            response.raise_for_status()

            data = response.json()
            results = []

            # Filter by query keywords
            query_words = set(query.lower().split())

            for video in data.get("videos", [])[:per_page * 3]:  # Get more, then filter
                tags = video.get("tags", [])
                title = video.get("title", "")

                # Check if any query word matches tags or title
                tag_words = set(" ".join(tags).lower().split())
                title_words = set(title.lower().split())

                if not (query_words & (tag_words | title_words)):
                    continue

                # Get best quality URL
                video_url = video.get("url_hd") or video.get("url") or ""

                if not video_url:
                    continue

                results.append(VideoResult(
                    id=f"coverr_{video.get('id', '')}",
                    title=title or "Coverr Video",
                    description=", ".join(tags),
                    duration=video.get("duration", 15),  # Coverr videos usually 10-20s
                    width=1920,
                    height=1080,
                    thumbnail_url=video.get("thumbnail", ""),
                    video_url=video_url,
                    video_files=[{"quality": "hd", "link": video_url}],
                    user=video.get("author", "Coverr"),
                    provider="coverr",
                    tags=tags
                ))

                if len(results) >= per_page:
                    break

            return results

        except Exception as e:
            logger.error(f"Coverr search failed: {e}")
            return []

    async def _search_videvo(self, query: str, per_page: int) -> List[VideoResult]:
        """Search Videvo (requires scraping or API)."""
        try:
            # Videvo requires scraping. For production, implement properly
            logger.info("Videvo search not fully implemented (requires scraping)")
            return []

        except Exception as e:
            logger.error(f"Videvo search failed: {e}")
            return []

    async def close(self):
        """Close HTTP clients."""
        await self.pexels_client.aclose()
        if self.pixabay_client:
            await self.pixabay_client.aclose()
        await self.videezy_client.aclose()
        await self.coverr_client.aclose()
        await self.videvo_client.aclose()
