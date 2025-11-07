"""
Stock Video API Router

Search and fetch stock videos for avatar backgrounds.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal
import os

from media.stock_videos import StockVideoSearcher, VideoResult

router = APIRouter()


# Dependency injection
_stock_video_searcher: Optional[StockVideoSearcher] = None


async def get_stock_video_searcher() -> StockVideoSearcher:
    """Get or create stock video searcher singleton."""
    global _stock_video_searcher
    if _stock_video_searcher is None:
        pexels_api_key = os.getenv("PEXELS_API_KEY")
        if not pexels_api_key:
            raise HTTPException(
                status_code=500,
                detail="PEXELS_API_KEY environment variable not set. Get free API key from https://www.pexels.com/api/"
            )

        pixabay_api_key = os.getenv("PIXABAY_API_KEY")  # Optional

        _stock_video_searcher = StockVideoSearcher(
            pexels_api_key=pexels_api_key,
            pixabay_api_key=pixabay_api_key
        )

    return _stock_video_searcher


# Request/Response Models

class SearchStockVideosRequest(BaseModel):
    """Request to search stock videos."""
    query: str
    per_page: int = 10
    orientation: Optional[Literal["landscape", "portrait", "square"]] = None
    size: Optional[Literal["large", "medium", "small"]] = None
    provider: Optional[Literal["pexels", "pixabay", "both"]] = "both"


class SearchStockVideosResponse(BaseModel):
    """Response from stock video search."""
    query: str
    total_results: int
    videos: List[VideoResult]


class GetVideoDownloadUrlRequest(BaseModel):
    """Request to get video download URL."""
    video_id: str
    provider: Literal["pexels", "pixabay"]
    quality: str = "hd"


class GetVideoDownloadUrlResponse(BaseModel):
    """Response with video download URL."""
    video_id: str
    provider: str
    download_url: HttpUrl
    quality: str


# Endpoints

@router.post("/search", response_model=SearchStockVideosResponse)
async def search_stock_videos(
    request: SearchStockVideosRequest,
    searcher: StockVideoSearcher = Depends(get_stock_video_searcher)
):
    """
    Search stock videos from Pexels and Pixabay.

    **Use Cases:**
    - Find background videos for avatar videos
    - Search by topic: "business", "nature", "technology", "fitness"
    - Get relevant videos for any subject

    **Providers:**
    - Pexels: 100k+ free HD videos
    - Pixabay: 50k+ free videos

    **Example queries:**
    - "business meeting"
    - "nature landscape"
    - "technology abstract"
    - "workout gym"
    - "cooking food"
    """
    try:
        videos = await searcher.search_videos(
            query=request.query,
            per_page=request.per_page,
            orientation=request.orientation,
            size=request.size,
            provider=request.provider
        )

        return SearchStockVideosResponse(
            query=request.query,
            total_results=len(videos),
            videos=videos
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/search", response_model=SearchStockVideosResponse)
async def search_stock_videos_get(
    query: str = Query(..., description="Search query"),
    per_page: int = Query(10, ge=1, le=50, description="Results per page"),
    orientation: Optional[Literal["landscape", "portrait", "square"]] = Query(None, description="Video orientation"),
    provider: Optional[Literal["pexels", "pixabay", "both"]] = Query("both", description="Video provider"),
    searcher: StockVideoSearcher = Depends(get_stock_video_searcher)
):
    """
    Search stock videos (GET version for easy browser testing).

    Try it:
    - /api/stock-videos/search?query=business&per_page=5
    - /api/stock-videos/search?query=nature&orientation=landscape
    """
    try:
        videos = await searcher.search_videos(
            query=query,
            per_page=per_page,
            orientation=orientation,
            provider=provider
        )

        return SearchStockVideosResponse(
            query=query,
            total_results=len(videos),
            videos=videos
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/download-url", response_model=GetVideoDownloadUrlResponse)
async def get_video_download_url(
    request: GetVideoDownloadUrlRequest,
    searcher: StockVideoSearcher = Depends(get_stock_video_searcher)
):
    """
    Get direct download URL for a specific video.

    Returns a direct link to download the video file in the requested quality.
    """
    try:
        download_url = await searcher.get_video_download_url(
            video_id=request.video_id,
            provider=request.provider,
            quality=request.quality
        )

        return GetVideoDownloadUrlResponse(
            video_id=request.video_id,
            provider=request.provider,
            download_url=download_url,
            quality=request.quality
        )

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Video not found: {str(e)}")


@router.get("/providers")
async def get_providers_info():
    """
    Get information about available stock video providers.

    Returns details about Pexels and Pixabay APIs.
    """
    return {
        "providers": [
            {
                "name": "Pexels",
                "status": "active" if os.getenv("PEXELS_API_KEY") else "not_configured",
                "free": True,
                "attribution_required": False,
                "video_count": "100,000+",
                "rate_limit": "200 requests/hour",
                "quality": ["4K", "HD", "SD"],
                "signup_url": "https://www.pexels.com/api/",
                "features": [
                    "High quality curated videos",
                    "Search by keyword",
                    "Multiple resolutions",
                    "No watermarks",
                    "Commercial use allowed"
                ]
            },
            {
                "name": "Pixabay",
                "status": "active" if os.getenv("PIXABAY_API_KEY") else "not_configured",
                "free": True,
                "attribution_required": False,
                "video_count": "50,000+",
                "rate_limit": "5,000 requests/hour",
                "quality": ["HD", "SD"],
                "signup_url": "https://pixabay.com/api/docs/",
                "features": [
                    "Good quality videos",
                    "Large selection",
                    "Tag-based search",
                    "No watermarks",
                    "Commercial use allowed"
                ]
            }
        ],
        "recommendation": "Use both providers for maximum content variety. Pexels is primary (better quality), Pixabay as fallback."
    }


@router.get("/popular-topics")
async def get_popular_topics():
    """
    Get suggested popular video topics for avatar backgrounds.

    These topics work well as background videos for various content types.
    """
    return {
        "business": [
            "business meeting",
            "office workspace",
            "city skyline",
            "financial charts",
            "teamwork collaboration"
        ],
        "technology": [
            "coding programming",
            "data visualization",
            "futuristic technology",
            "circuit boards",
            "abstract digital"
        ],
        "nature": [
            "forest trees",
            "ocean waves",
            "mountain landscape",
            "sunset sunrise",
            "flowing water"
        ],
        "health_fitness": [
            "workout gym",
            "running jogging",
            "yoga meditation",
            "healthy food",
            "active lifestyle"
        ],
        "education": [
            "books library",
            "classroom learning",
            "science laboratory",
            "writing notes",
            "graduation ceremony"
        ],
        "creative": [
            "painting art",
            "music instruments",
            "photography camera",
            "design workspace",
            "creative studio"
        ],
        "lifestyle": [
            "cooking kitchen",
            "travel adventure",
            "city street",
            "fashion style",
            "home interior"
        ],
        "abstract": [
            "particles motion",
            "geometric shapes",
            "color gradients",
            "light effects",
            "bokeh background"
        ]
    }
