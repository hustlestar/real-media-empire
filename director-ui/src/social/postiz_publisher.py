"""
Postiz Publisher - Multi-platform social media publishing via Postiz
https://postiz.com - Open-source social media scheduling tool
"""

import httpx
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from social.base_publisher import SocialPublisher, PublishResult, PostContent

logger = logging.getLogger(__name__)


class PostizConfig(BaseModel):
    """Configuration for Postiz API."""
    api_key: str
    base_url: str = "https://api.postiz.com"  # Default Postiz API URL
    timeout: int = 30
    max_retries: int = 3


class PlatformLimits(BaseModel):
    """Platform-specific content limits."""
    max_caption_length: int
    max_hashtags: int
    max_video_size_mb: int
    max_image_size_mb: int
    supported_formats: List[str]
    requires_approval: bool = False


# Platform-specific limits (from n8n workflow patterns)
PLATFORM_LIMITS = {
    "tiktok": PlatformLimits(
        max_caption_length=2200,
        max_hashtags=30,
        max_video_size_mb=287,
        max_image_size_mb=10,
        supported_formats=["mp4", "mov", "avi", "jpg", "png"],
        requires_approval=False
    ),
    "youtube": PlatformLimits(
        max_caption_length=5000,
        max_hashtags=15,
        max_video_size_mb=256000,  # 256 GB for videos over 15 minutes
        max_image_size_mb=2,
        supported_formats=["mp4", "mov", "avi", "flv", "wmv"],
        requires_approval=False
    ),
    "instagram": PlatformLimits(
        max_caption_length=2200,
        max_hashtags=30,
        max_video_size_mb=100,
        max_image_size_mb=8,
        supported_formats=["mp4", "mov", "jpg", "png"],
        requires_approval=False
    ),
    "facebook": PlatformLimits(
        max_caption_length=63206,
        max_hashtags=30,
        max_video_size_mb=10240,  # 10 GB
        max_image_size_mb=10,
        supported_formats=["mp4", "mov", "avi", "jpg", "png"],
        requires_approval=False
    ),
    "twitter": PlatformLimits(
        max_caption_length=280,
        max_hashtags=10,
        max_video_size_mb=512,
        max_image_size_mb=5,
        supported_formats=["mp4", "mov", "jpg", "png", "gif"],
        requires_approval=False
    ),
    "linkedin": PlatformLimits(
        max_caption_length=3000,
        max_hashtags=30,
        max_video_size_mb=5120,  # 5 GB
        max_image_size_mb=10,
        supported_formats=["mp4", "mov", "jpg", "png"],
        requires_approval=False
    ),
}


class PostizPublisher(SocialPublisher):
    """Postiz social media publisher implementation."""

    def __init__(self, config: PostizConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=config.timeout
        )

    async def _optimize_content(self, content: PostContent) -> PostContent:
        """
        Optimize content for platform-specific limits.

        This follows the pattern from the n8n workflows where content
        is cleaned and truncated based on platform requirements.
        """
        platform = content.platform.lower()
        limits = PLATFORM_LIMITS.get(platform)

        if not limits:
            logger.warning(f"Unknown platform {platform}, using defaults")
            return content

        # Clone the content to avoid mutating the original
        optimized = content.model_copy(deep=True)

        # Optimize caption length
        if len(optimized.caption) > limits.max_caption_length:
            # Truncate and add ellipsis
            optimized.caption = optimized.caption[:limits.max_caption_length - 3] + "..."
            logger.info(f"Caption truncated for {platform} (max: {limits.max_caption_length})")

        # Limit hashtags
        if len(optimized.hashtags) > limits.max_hashtags:
            optimized.hashtags = optimized.hashtags[:limits.max_hashtags]
            logger.info(f"Hashtags limited for {platform} (max: {limits.max_hashtags})")

        # Platform-specific cleaning
        if platform == "twitter":
            # Twitter has special handling for mentions and links
            optimized.caption = self._clean_twitter_caption(optimized.caption)
        elif platform == "linkedin":
            # LinkedIn prefers professional tone
            optimized.caption = self._clean_linkedin_caption(optimized.caption)
        elif platform == "tiktok":
            # TikTok requires specific hashtag formatting
            optimized.hashtags = [f"#{tag.lstrip('#')}" for tag in optimized.hashtags]

        return optimized

    def _clean_twitter_caption(self, caption: str) -> str:
        """Clean caption for Twitter-specific requirements."""
        # Escape special characters, preserve mentions and hashtags
        # Remove excessive newlines
        caption = caption.replace("\n\n\n", "\n\n")
        return caption

    def _clean_linkedin_caption(self, caption: str) -> str:
        """Clean caption for LinkedIn-specific requirements."""
        # LinkedIn prefers professional formatting
        # Remove excessive emojis, format professionally
        return caption

    def _format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for inclusion in caption."""
        if not hashtags:
            return ""

        # Ensure all hashtags start with #
        formatted = [f"#{tag.lstrip('#')}" for tag in hashtags]
        return " ".join(formatted)

    async def publish(self, content: PostContent, account_id: str) -> PublishResult:
        """
        Publish content immediately to a social media platform via Postiz.
        """
        try:
            # Optimize content for platform
            optimized_content = await self._optimize_content(content)

            # Build the caption with hashtags
            full_caption = optimized_content.caption
            if optimized_content.hashtags:
                hashtag_str = self._format_hashtags(optimized_content.hashtags)
                full_caption = f"{optimized_content.caption}\n\n{hashtag_str}"

            # Prepare the request payload
            payload = {
                "accountId": account_id,
                "platform": optimized_content.platform,
                "content": {
                    "type": optimized_content.content_type,
                    "caption": full_caption,
                    "mediaUrl": optimized_content.content_url
                },
                "settings": optimized_content.platform_settings,
                "publishNow": True
            }

            # Add source tracking if available
            if optimized_content.source_id:
                payload["metadata"] = {
                    "sourceId": optimized_content.source_id,
                    "sourceType": optimized_content.source_type
                }

            # Make the API request with retries
            for attempt in range(self.config.max_retries):
                try:
                    response = await self.client.post("/v1/posts", json=payload)
                    response.raise_for_status()

                    result_data = response.json()

                    return PublishResult(
                        success=True,
                        post_id=result_data.get("postId"),
                        post_url=result_data.get("postUrl"),
                        platform=optimized_content.platform,
                        message="Post published successfully",
                        metadata=result_data
                    )

                except httpx.HTTPStatusError as e:
                    if attempt == self.config.max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        except Exception as e:
            logger.error(f"Failed to publish to {content.platform}: {str(e)}")
            return PublishResult(
                success=False,
                platform=content.platform,
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )

    async def schedule(self, content: PostContent, account_id: str, schedule_at: datetime) -> PublishResult:
        """
        Schedule content for future publishing via Postiz.
        """
        try:
            # Optimize content for platform
            optimized_content = await self._optimize_content(content)

            # Build the caption with hashtags
            full_caption = optimized_content.caption
            if optimized_content.hashtags:
                hashtag_str = self._format_hashtags(optimized_content.hashtags)
                full_caption = f"{optimized_content.caption}\n\n{hashtag_str}"

            # Prepare the request payload
            payload = {
                "accountId": account_id,
                "platform": optimized_content.platform,
                "content": {
                    "type": optimized_content.content_type,
                    "caption": full_caption,
                    "mediaUrl": optimized_content.content_url
                },
                "settings": optimized_content.platform_settings,
                "publishNow": False,
                "scheduledAt": schedule_at.isoformat()
            }

            # Add source tracking if available
            if optimized_content.source_id:
                payload["metadata"] = {
                    "sourceId": optimized_content.source_id,
                    "sourceType": optimized_content.source_type
                }

            # Make the API request
            response = await self.client.post("/v1/posts", json=payload)
            response.raise_for_status()

            result_data = response.json()

            return PublishResult(
                success=True,
                post_id=result_data.get("postId"),
                post_url=result_data.get("postUrl"),
                platform=optimized_content.platform,
                message=f"Post scheduled for {schedule_at.isoformat()}",
                metadata=result_data
            )

        except Exception as e:
            logger.error(f"Failed to schedule post for {content.platform}: {str(e)}")
            return PublishResult(
                success=False,
                platform=content.platform,
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )

    async def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """
        Get the current status of a post from Postiz.
        """
        try:
            response = await self.client.get(f"/v1/posts/{post_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get post status for {post_id}: {str(e)}")
            return {
                "error": str(e),
                "status": "unknown"
            }

    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a published post via Postiz.
        """
        try:
            response = await self.client.delete(f"/v1/posts/{post_id}")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete post {post_id}: {str(e)}")
            return False

    async def verify_account(self, account_id: str) -> bool:
        """
        Verify that a social account is properly configured in Postiz.
        """
        try:
            response = await self.client.get(f"/v1/accounts/{account_id}")
            response.raise_for_status()
            account_data = response.json()

            # Check if account is active and connected
            return account_data.get("status") == "active" and account_data.get("connected", False)
        except Exception as e:
            logger.error(f"Failed to verify account {account_id}: {str(e)}")
            return False

    async def publish_multi_platform(
        self,
        content: PostContent,
        account_ids: List[str]
    ) -> List[PublishResult]:
        """
        Publish the same content to multiple platforms simultaneously.

        This is useful for cross-platform campaigns where the same content
        should be published to TikTok, Instagram, YouTube, etc.
        """
        tasks = [
            self.publish(content, account_id)
            for account_id in account_ids
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to PublishResult objects
        publish_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                publish_results.append(PublishResult(
                    success=False,
                    platform=content.platform,
                    error=str(result),
                    metadata={"account_id": account_ids[i]}
                ))
            else:
                publish_results.append(result)

        return publish_results

    async def get_platform_limits(self, platform: str) -> Optional[PlatformLimits]:
        """
        Get content limits for a specific platform.
        """
        return PLATFORM_LIMITS.get(platform.lower())

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
