"""
Postiz Publishing API Router

Endpoints for multi-platform social media publishing via Postiz.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from social.postiz_publisher import PostizPublisher, PostizConfig, PLATFORM_LIMITS
from social.base_publisher import PostContent, PublishResult

router = APIRouter()


# Request/Response Models

class PublishRequest(BaseModel):
    """Request to publish content to a social platform."""
    account_id: str = Field(..., description="Social account ID to publish to")
    platform: str = Field(..., description="Platform name (tiktok, youtube, instagram, etc.)")
    content_type: str = Field(..., description="Content type (video, image, text, carousel)")
    content_url: Optional[str] = Field(None, description="URL to video/image asset")
    caption: str = Field(..., description="Post caption/description")
    hashtags: List[str] = Field(default_factory=list, description="List of hashtags")
    platform_settings: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific settings")

    # Source tracking
    source_id: Optional[str] = Field(None, description="ID of source content (film_id, avatar_video_id, etc.)")
    source_type: Optional[str] = Field(None, description="Type of source (film, avatar_video, presentation)")


class ScheduleRequest(PublishRequest):
    """Request to schedule content for future publishing."""
    schedule_at: datetime = Field(..., description="When to publish the content")


class MultiPlatformPublishRequest(BaseModel):
    """Request to publish content to multiple platforms."""
    account_ids: List[str] = Field(..., description="List of social account IDs")
    content: PublishRequest


class PublishResponse(BaseModel):
    """Response from a publish operation."""
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    platform: str
    message: Optional[str] = None
    error: Optional[str] = None


class PostStatusResponse(BaseModel):
    """Response for post status query."""
    post_id: str
    status: str
    platform: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}


class PlatformLimitsResponse(BaseModel):
    """Response with platform content limits."""
    platform: str
    max_caption_length: int
    max_hashtags: int
    max_video_size_mb: int
    max_image_size_mb: int
    supported_formats: List[str]
    requires_approval: bool


class AccountVerificationResponse(BaseModel):
    """Response for account verification."""
    account_id: str
    is_valid: bool
    message: Optional[str] = None


# Dependency injection

_postiz_publisher: Optional[PostizPublisher] = None


async def get_postiz_publisher() -> PostizPublisher:
    """Get or create Postiz publisher singleton."""
    global _postiz_publisher

    if _postiz_publisher is None:
        # In production, load from environment variables
        import os

        postiz_api_key = os.getenv("POSTIZ_API_KEY")
        if not postiz_api_key:
            raise HTTPException(
                status_code=500,
                detail="POSTIZ_API_KEY not configured"
            )

        postiz_base_url = os.getenv("POSTIZ_BASE_URL", "https://api.postiz.com")

        config = PostizConfig(
            api_key=postiz_api_key,
            base_url=postiz_base_url,
            timeout=30,
            max_retries=3
        )

        _postiz_publisher = PostizPublisher(config)

    return _postiz_publisher


# API Endpoints

@router.post("/publish", response_model=PublishResponse)
async def publish_content(
    request: PublishRequest,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    """
    Publish content immediately to a social media platform.

    This endpoint accepts content (video, image, text) and publishes it
    immediately to the specified platform via the configured social account.
    """
    # Convert request to PostContent
    content = PostContent(
        platform=request.platform,
        content_type=request.content_type,
        content_url=request.content_url,
        caption=request.caption,
        hashtags=request.hashtags,
        platform_settings=request.platform_settings,
        source_id=request.source_id,
        source_type=request.source_type
    )

    # Publish the content
    result = await publisher.publish(content, request.account_id)

    return PublishResponse(
        success=result.success,
        post_id=result.post_id,
        post_url=result.post_url,
        platform=result.platform,
        message=result.message,
        error=result.error
    )


@router.post("/schedule", response_model=PublishResponse)
async def schedule_content(
    request: ScheduleRequest,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    """
    Schedule content for future publishing.

    This endpoint accepts content and a scheduled time, then queues the
    content for automatic publishing at the specified time.
    """
    # Convert request to PostContent
    content = PostContent(
        platform=request.platform,
        content_type=request.content_type,
        content_url=request.content_url,
        caption=request.caption,
        hashtags=request.hashtags,
        platform_settings=request.platform_settings,
        source_id=request.source_id,
        source_type=request.source_type
    )

    # Schedule the content
    result = await publisher.schedule(content, request.account_id, request.schedule_at)

    return PublishResponse(
        success=result.success,
        post_id=result.post_id,
        post_url=result.post_url,
        platform=result.platform,
        message=result.message,
        error=result.error
    )


@router.post("/publish/multi-platform", response_model=List[PublishResponse])
async def publish_multi_platform(
    request: MultiPlatformPublishRequest,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    """
    Publish the same content to multiple platforms simultaneously.

    This is useful for cross-platform campaigns where identical content
    should be published to TikTok, Instagram, YouTube, etc. at once.
    """
    # Convert request to PostContent
    content = PostContent(
        platform=request.content.platform,
        content_type=request.content.content_type,
        content_url=request.content.content_url,
        caption=request.content.caption,
        hashtags=request.content.hashtags,
        platform_settings=request.content.platform_settings,
        source_id=request.content.source_id,
        source_type=request.content.source_type
    )

    # Publish to all platforms
    results = await publisher.publish_multi_platform(content, request.account_ids)

    return [
        PublishResponse(
            success=result.success,
            post_id=result.post_id,
            post_url=result.post_url,
            platform=result.platform,
            message=result.message,
            error=result.error
        )
        for result in results
    ]


@router.get("/posts/{post_id}/status", response_model=PostStatusResponse)
async def get_post_status(
    post_id: str,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    """
    Get the current status of a published or scheduled post.

    Returns information about the post including its publishing status,
    platform, and any relevant metadata.
    """
    status_data = await publisher.get_post_status(post_id)

    if "error" in status_data:
        raise HTTPException(
            status_code=404,
            detail=f"Post not found or error retrieving status: {status_data['error']}"
        )

    return PostStatusResponse(
        post_id=post_id,
        status=status_data.get("status", "unknown"),
        platform=status_data.get("platform"),
        published_at=status_data.get("publishedAt"),
        metadata=status_data
    )


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    """
    Delete a published post from a social media platform.

    Note: Deletion capabilities vary by platform. Some platforms may not
    allow programmatic deletion of posts.
    """
    success = await publisher.delete_post(post_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to delete post. Post may not exist or platform may not support deletion."
        )

    return {"message": "Post deleted successfully", "post_id": post_id}


@router.get("/accounts/{account_id}/verify", response_model=AccountVerificationResponse)
async def verify_account(
    account_id: str,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    """
    Verify that a social media account is properly configured and accessible.

    This checks if the account credentials are valid and the account is
    ready to accept publishing requests.
    """
    is_valid = await publisher.verify_account(account_id)

    return AccountVerificationResponse(
        account_id=account_id,
        is_valid=is_valid,
        message="Account is valid and ready for publishing" if is_valid else "Account verification failed"
    )


@router.get("/platforms/{platform}/limits", response_model=PlatformLimitsResponse)
async def get_platform_limits(
    platform: str,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    """
    Get content limits and requirements for a specific platform.

    Returns information about maximum caption length, hashtag limits,
    file size limits, and supported content formats.
    """
    limits = await publisher.get_platform_limits(platform)

    if not limits:
        raise HTTPException(
            status_code=404,
            detail=f"Platform '{platform}' not supported or limits not available"
        )

    return PlatformLimitsResponse(
        platform=platform,
        max_caption_length=limits.max_caption_length,
        max_hashtags=limits.max_hashtags,
        max_video_size_mb=limits.max_video_size_mb,
        max_image_size_mb=limits.max_image_size_mb,
        supported_formats=limits.supported_formats,
        requires_approval=limits.requires_approval
    )


@router.get("/platforms", response_model=List[str])
async def list_supported_platforms():
    """
    Get a list of all supported social media platforms.

    Returns platform identifiers that can be used in publish requests.
    """
    return list(PLATFORM_LIMITS.keys())


@router.get("/platforms/limits", response_model=Dict[str, PlatformLimitsResponse])
async def get_all_platform_limits():
    """
    Get content limits for all supported platforms.

    Returns a comprehensive map of platform limits for easy reference.
    """
    return {
        platform: PlatformLimitsResponse(
            platform=platform,
            max_caption_length=limits.max_caption_length,
            max_hashtags=limits.max_hashtags,
            max_video_size_mb=limits.max_video_size_mb,
            max_image_size_mb=limits.max_image_size_mb,
            supported_formats=limits.supported_formats,
            requires_approval=limits.requires_approval
        )
        for platform, limits in PLATFORM_LIMITS.items()
    }
