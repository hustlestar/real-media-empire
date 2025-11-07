"""
Trend Research API Router

Endpoints for researching viral trends, hashtags, and content strategies.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
import os

from content.trend_research import TrendResearcher, TrendInsight, TrendResearchResult

router = APIRouter()


# Dependency injection
_trend_researcher: Optional[TrendResearcher] = None


async def get_trend_researcher() -> TrendResearcher:
    """Get or create TrendResearcher singleton."""
    global _trend_researcher
    if _trend_researcher is None:
        perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if not perplexity_api_key:
            raise HTTPException(
                status_code=500,
                detail="PERPLEXITY_API_KEY environment variable not set"
            )
        _trend_researcher = TrendResearcher(api_key=perplexity_api_key)
    return _trend_researcher


# Request/Response Models

class ResearchTrendsRequest(BaseModel):
    """Request to research trending topics."""
    topic: str
    platform: Literal["tiktok", "youtube", "instagram", "twitter", "linkedin"] = "tiktok"
    num_trends: int = 3


class OptimizeHashtagsRequest(BaseModel):
    """Request to optimize hashtags for content."""
    content_description: str
    platform: Literal["tiktok", "youtube", "instagram", "twitter", "linkedin"] = "tiktok"
    max_hashtags: int = 10


class HashtagsResponse(BaseModel):
    """Response with optimized hashtags."""
    hashtags: List[str]
    platform: str
    max_allowed: int


class ContentStrategyRequest(BaseModel):
    """Request to generate content strategy."""
    topic: str
    platform: str
    trends: List[dict]


class ContentStrategyResponse(BaseModel):
    """Response with content strategy."""
    strategy: str
    topic: str
    platform: str


# Endpoints

@router.post("/research", response_model=TrendResearchResult)
async def research_trends(
    request: ResearchTrendsRequest,
    researcher: TrendResearcher = Depends(get_trend_researcher)
):
    """
    Research current viral trends for a topic.

    Uses Perplexity AI's real-time web search to find:
    - Trending topics and hashtags
    - Viral content styles and formats
    - Current platform-specific trends
    - Actionable content insights

    **Args:**
    - topic: The topic to research (e.g., "fitness", "productivity")
    - platform: Target social media platform
    - num_trends: Number of trends to return (1-10)

    **Returns:**
    - Trending insights with hashtags and content styles
    - Real-time data based on current web search

    **Example:**
    ```json
    {
      "topic": "cold showers",
      "platform": "tiktok",
      "num_trends": 3
    }
    ```
    """
    try:
        result = await researcher.research_trends(
            topic=request.topic,
            platform=request.platform,
            num_trends=request.num_trends
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trend research failed: {str(e)}"
        )


@router.post("/optimize-hashtags", response_model=HashtagsResponse)
async def optimize_hashtags(
    request: OptimizeHashtagsRequest,
    researcher: TrendResearcher = Depends(get_trend_researcher)
):
    """
    Generate optimized hashtags for content.

    Creates a mix of popular and niche hashtags based on:
    - Content description
    - Platform-specific trends
    - Current viral hashtags
    - Potential reach estimation

    **Args:**
    - content_description: Description of your content
    - platform: Target platform
    - max_hashtags: Maximum number of hashtags

    **Returns:**
    - List of optimized hashtags
    - Platform-specific recommendations

    **Example:**
    ```json
    {
      "content_description": "Video about morning routine for productivity",
      "platform": "tiktok",
      "max_hashtags": 10
    }
    ```
    """
    try:
        hashtags = await researcher.optimize_hashtags(
            content_description=request.content_description,
            platform=request.platform,
            max_hashtags=request.max_hashtags
        )

        platform_limits = {
            "tiktok": 30,
            "instagram": 30,
            "youtube": 15,
            "twitter": 10,
            "linkedin": 30
        }

        return HashtagsResponse(
            hashtags=hashtags,
            platform=request.platform,
            max_allowed=platform_limits.get(request.platform, 10)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hashtag optimization failed: {str(e)}"
        )


@router.post("/content-strategy", response_model=ContentStrategyResponse)
async def generate_content_strategy(
    request: ContentStrategyRequest,
    researcher: TrendResearcher = Depends(get_trend_researcher)
):
    """
    Generate a content strategy based on trends.

    Creates actionable content recommendations including:
    - Specific content ideas (3-5)
    - Optimal posting times/frequency
    - Hashtag strategy
    - Collaboration opportunities
    - Trend leveraging tactics

    **Args:**
    - topic: Content topic
    - platform: Target platform
    - trends: List of trend insights from research

    **Returns:**
    - Strategic content plan
    - Actionable recommendations
    """
    try:
        # Convert dicts back to TrendInsight objects
        trend_insights = [TrendInsight(**t) for t in request.trends]

        strategy = await researcher.generate_content_strategy(
            topic=request.topic,
            platform=request.platform,
            trends=trend_insights
        )

        return ContentStrategyResponse(
            strategy=strategy,
            topic=request.topic,
            platform=request.platform
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Strategy generation failed: {str(e)}"
        )


@router.get("/platform-info")
async def get_platform_info():
    """Get information about supported platforms and their characteristics."""
    return {
        "platforms": {
            "tiktok": {
                "max_hashtags": 30,
                "optimal_hashtags": "5-8",
                "content_length": "15-60 seconds",
                "best_times": ["7-9am", "12-1pm", "7-11pm"],
                "trending_formats": ["POV", "Transitions", "Duets", "Reactions"],
                "note": "Highly algorithm-driven, trending sounds matter"
            },
            "youtube": {
                "max_hashtags": 15,
                "optimal_hashtags": "3-5",
                "content_length": "Shorts: 60s, Long: 8-15min",
                "best_times": ["2-4pm", "6-9pm"],
                "trending_formats": ["Tutorials", "Reviews", "Vlogs", "Shorts"],
                "note": "SEO and thumbnails are critical"
            },
            "instagram": {
                "max_hashtags": 30,
                "optimal_hashtags": "9-11",
                "content_length": "Reels: 30-90s, Posts: Any",
                "best_times": ["11am-1pm", "7-9pm"],
                "trending_formats": ["Reels", "Carousels", "Stories", "IGTV"],
                "note": "Visual aesthetic and consistency matter"
            },
            "twitter": {
                "max_hashtags": 10,
                "optimal_hashtags": "1-2",
                "content_length": "280 characters",
                "best_times": ["9am", "12pm", "5pm"],
                "trending_formats": ["Threads", "Polls", "Quote Tweets"],
                "note": "Real-time engagement, trending topics"
            },
            "linkedin": {
                "max_hashtags": 30,
                "optimal_hashtags": "3-5",
                "content_length": "1300-2000 characters",
                "best_times": ["7-8am", "12pm", "5-6pm"],
                "trending_formats": ["Thought leadership", "Case studies", "Polls"],
                "note": "Professional tone, value-driven content"
            }
        },
        "general_tips": [
            "Mix popular and niche hashtags for better reach",
            "Research trending hashtags weekly",
            "Use platform-native features (Reels, Shorts, etc.)",
            "Engage with trending topics authentically",
            "Post consistently at optimal times",
            "Analyze competitor content for insights"
        ]
    }
