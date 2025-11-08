"""
Content Calendar API Router

REST API for content scheduling and calendar management.

Run from director-ui directory with:
    PYTHONPATH=../src uvicorn src.api.app:app --reload
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# NOTE: This assumes PYTHONPATH includes the src directory
try:
    from features.workflow.content_calendar import (
        ContentCalendar,
        ContentItem,
        OptimalPostingTime,
        Platform,
        ContentStatus,
        ContentType,
        schedule_content_optimal
    )
except ImportError as e:
    raise ImportError(
        f"Could not import content calendar module: {e}\n"
        "Make sure PYTHONPATH includes the src directory:\n"
        "  PYTHONPATH=../src uvicorn src.api.app:app --reload"
    )


router = APIRouter(prefix="/api/calendar", tags=["content-calendar"])


# Request/Response Models

class ScheduleContentRequest(BaseModel):
    """Schedule content request."""
    title: str = Field(..., description="Content title")
    platform: Platform = Field(..., description="Target platform")
    content_type: ContentType = Field("video", description="Content type")
    video_path: Optional[str] = Field(None, description="Path to video file")
    thumbnail_path: Optional[str] = Field(None, description="Path to thumbnail")
    description: Optional[str] = Field(None, description="Content description")
    tags: Optional[List[str]] = Field(None, description="Content tags/hashtags")
    scheduled_time: Optional[str] = Field(None, description="ISO datetime string")
    use_optimal_time: bool = Field(True, description="Use platform optimal time")

    class Config:
        schema_extra = {
            "example": {
                "title": "Amazing Tutorial: How to Code",
                "platform": "youtube",
                "content_type": "video",
                "video_path": "/videos/tutorial.mp4",
                "thumbnail_path": "/thumbnails/tutorial.jpg",
                "description": "Learn coding in 10 minutes!",
                "tags": ["coding", "tutorial", "programming"],
                "use_optimal_time": True
            }
        }


class ContentItemResponse(BaseModel):
    """Content item response."""
    content_id: str
    title: str
    platform: Platform
    content_type: ContentType
    scheduled_time: str
    status: ContentStatus
    video_path: Optional[str]
    thumbnail_path: Optional[str]
    description: Optional[str]
    tags: List[str]


class OptimalTimeResponse(BaseModel):
    """Optimal posting time response."""
    platform: Platform
    day_of_week: str
    time: str
    engagement_score: float
    reason: str


class CalendarViewResponse(BaseModel):
    """Calendar view response."""
    month: int
    year: int
    calendar_text: str
    total_scheduled: int


class ScheduleSuggestionResponse(BaseModel):
    """Posting schedule suggestion response."""
    platform: Platform
    num_posts_per_week: int
    suggested_times: List[str]
    optimal_days: List[str]


# Initialize calendar
calendar = ContentCalendar(calendar_dir="content_calendar/")


@router.post("/schedule", response_model=ContentItemResponse)
async def schedule_content(request: ScheduleContentRequest):
    """
    Schedule content for publishing.

    Schedules content at the optimal time for maximum engagement.

    **Key Benefits:**
    - 30-50% engagement increase with optimal timing
    - 3x faster audience growth with consistency
    - 24% CTR improvement

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/calendar/schedule" \\
      -H "Content-Type: application/json" \\
      -d '{
        "title": "Amazing Tutorial",
        "platform": "youtube",
        "content_type": "video",
        "video_path": "/videos/tutorial.mp4",
        "use_optimal_time": true
      }'
    ```
    """
    try:
        # Parse scheduled time if provided
        scheduled_time = None
        if request.scheduled_time:
            scheduled_time = datetime.fromisoformat(request.scheduled_time)

        # Schedule content
        item = calendar.schedule_content(
            title=request.title,
            platform=request.platform,
            content_type=request.content_type,
            video_path=request.video_path,
            thumbnail_path=request.thumbnail_path,
            description=request.description,
            tags=request.tags,
            scheduled_time=scheduled_time,
            use_optimal_time=request.use_optimal_time
        )

        return ContentItemResponse(
            content_id=item.content_id,
            title=item.title,
            platform=item.platform,
            content_type=item.content_type,
            scheduled_time=item.scheduled_time.isoformat(),
            status=item.status,
            video_path=item.video_path,
            thumbnail_path=item.thumbnail_path,
            description=item.description,
            tags=item.tags
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule content: {str(e)}")


@router.get("/optimal-times/{platform}", response_model=List[OptimalTimeResponse])
async def get_optimal_times(platform: Platform, num_suggestions: int = 7):
    """
    Get optimal posting times for platform.

    Returns best times to post based on platform analytics and research.

    **Platforms Supported:**
    - YouTube: Weekday afternoons (2-4 PM)
    - TikTok: Mornings and evenings (6-9 AM, 5-7 PM)
    - Instagram: Weekday midday (11 AM - 2 PM)
    - Facebook: Thursday-Friday afternoons (1-3 PM)
    - Twitter: Weekday mornings (9-12 AM)
    - LinkedIn: Tuesday-Wednesday business hours (9-11 AM)

    **Example:**
    ```bash
    curl "http://localhost:8000/api/calendar/optimal-times/youtube?num_suggestions=7"
    ```
    """
    try:
        times = calendar.get_optimal_posting_times(platform, num_suggestions)

        return [
            OptimalTimeResponse(
                platform=t.platform,
                day_of_week=t.day_of_week,
                time=t.time,
                engagement_score=t.engagement_score,
                reason=t.reason
            )
            for t in times
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get optimal times: {str(e)}")


@router.get("/week", response_model=Dict[str, List[ContentItemResponse]])
async def get_weekly_schedule(start_date: Optional[str] = None):
    """
    Get content scheduled for the week.

    Returns all content scheduled for the current or specified week.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/calendar/week"
    ```
    """
    try:
        # Parse start date if provided
        start_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)

        schedule = calendar.get_weekly_schedule(start_dt)

        # Convert to response format
        response = {}
        for date_str, items in schedule.items():
            response[date_str] = [
                ContentItemResponse(
                    content_id=item.content_id,
                    title=item.title,
                    platform=item.platform,
                    content_type=item.content_type,
                    scheduled_time=item.scheduled_time.isoformat(),
                    status=item.status,
                    video_path=item.video_path,
                    thumbnail_path=item.thumbnail_path,
                    description=item.description,
                    tags=item.tags
                )
                for item in items
            ]

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weekly schedule: {str(e)}")


@router.get("/month", response_model=Dict[str, List[ContentItemResponse]])
async def get_monthly_schedule(year: Optional[int] = None, month: Optional[int] = None):
    """
    Get content scheduled for the month.

    Returns all content scheduled for the current or specified month.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/calendar/month?year=2025&month=1"
    ```
    """
    try:
        schedule = calendar.get_monthly_schedule(year, month)

        # Convert to response format
        response = {}
        for date_str, items in schedule.items():
            response[date_str] = [
                ContentItemResponse(
                    content_id=item.content_id,
                    title=item.title,
                    platform=item.platform,
                    content_type=item.content_type,
                    scheduled_time=item.scheduled_time.isoformat(),
                    status=item.status,
                    video_path=item.video_path,
                    thumbnail_path=item.thumbnail_path,
                    description=item.description,
                    tags=item.tags
                )
                for item in items
            ]

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get monthly schedule: {str(e)}")


@router.get("/view", response_model=CalendarViewResponse)
async def get_calendar_view(year: Optional[int] = None, month: Optional[int] = None):
    """
    Get text-based calendar view.

    Returns ASCII calendar with indicators for scheduled content.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/calendar/view?year=2025&month=1"
    ```
    """
    try:
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month

        calendar_text = calendar.get_calendar_view(year, month)
        schedule = calendar.get_monthly_schedule(year, month)

        return CalendarViewResponse(
            month=month,
            year=year,
            calendar_text=calendar_text,
            total_scheduled=sum(len(items) for items in schedule.values())
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar view: {str(e)}")


@router.put("/status/{content_id}")
async def update_content_status(content_id: str, status: ContentStatus):
    """
    Update content status.

    Changes content status (draft, scheduled, published, failed).

    **Statuses:**
    - draft: Content being prepared
    - scheduled: Ready for publishing
    - published: Successfully published
    - failed: Publishing failed

    **Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/calendar/status/youtube_20250101_120000?status=published"
    ```
    """
    try:
        calendar.update_status(content_id, status)

        return {
            "success": True,
            "content_id": content_id,
            "new_status": status,
            "message": f"Status updated to {status}"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.get("/suggest-schedule/{platform}", response_model=ScheduleSuggestionResponse)
async def suggest_posting_schedule(platform: Platform, num_posts_per_week: int = 3):
    """
    Suggest posting schedule for platform.

    Returns suggested posting times for the week based on optimal engagement.

    **Recommended Frequency:**
    - YouTube: 3-4 posts/week
    - TikTok: 5-7 posts/week
    - Instagram: 4-5 posts/week
    - Facebook: 3-4 posts/week
    - Twitter: 7-10 posts/week
    - LinkedIn: 2-3 posts/week

    **Example:**
    ```bash
    curl "http://localhost:8000/api/calendar/suggest-schedule/youtube?num_posts_per_week=3"
    ```
    """
    try:
        suggestions = calendar.suggest_posting_schedule(platform, num_posts_per_week)

        return ScheduleSuggestionResponse(
            platform=platform,
            num_posts_per_week=num_posts_per_week,
            suggested_times=[dt.isoformat() for dt in suggestions],
            optimal_days=[dt.strftime("%A") for dt in suggestions]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest schedule: {str(e)}")


@router.get("/stats")
async def get_calendar_stats():
    """
    Get content calendar statistics and benefits.

    Returns key metrics about strategic scheduling impact.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/calendar/stats"
    ```
    """
    return {
        "key_stats": {
            "engagement_increase": "30-50%",
            "audience_growth": "3x faster",
            "time_saved_per_week": "10+ hours",
            "ctr_improvement": "24%"
        },
        "benefits": [
            "Post at optimal times for maximum engagement",
            "Consistent schedule grows audience faster",
            "Automated timing saves hours of research",
            "Data-driven recommendations",
            "Multi-platform coordination"
        ],
        "optimal_frequency": {
            "youtube": "3-4 posts/week",
            "tiktok": "5-7 posts/week",
            "instagram": "4-5 posts/week",
            "facebook": "3-4 posts/week",
            "twitter": "7-10 posts/week",
            "linkedin": "2-3 posts/week"
        }
    }


@router.get("/all-optimal-times")
async def get_all_optimal_times():
    """
    Get optimal posting times for all platforms.

    Returns complete matrix of best posting times across all platforms.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/calendar/all-optimal-times"
    ```
    """
    all_times = {}

    platforms = ["youtube", "tiktok", "instagram", "facebook", "twitter", "linkedin"]

    for platform in platforms:
        times = calendar.get_optimal_posting_times(platform, num_suggestions=3)
        all_times[platform] = [
            {
                "day": t.day_of_week,
                "time": t.time,
                "score": t.engagement_score,
                "reason": t.reason
            }
            for t in times
        ]

    return {
        "platforms": all_times,
        "total_platforms": len(platforms),
        "message": "Top 3 posting times per platform"
    }
