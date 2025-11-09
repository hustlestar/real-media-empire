"""
Base Publisher - Abstract interface for social media publishing
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class PublishResult(BaseModel):
    """Result of a publishing operation."""
    success: bool
    post_id: Optional[str] = None  # Platform-specific post ID
    post_url: Optional[str] = None  # Direct URL to post
    platform: str
    message: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class PostContent(BaseModel):
    """Content to be published."""
    platform: str  # tiktok, youtube, instagram, facebook, twitter, linkedin
    content_type: str  # video, image, text, carousel
    content_url: Optional[str] = None  # URL to video/image asset
    caption: str
    hashtags: List[str] = []

    # Platform-specific settings
    platform_settings: Dict[str, Any] = {}

    # Scheduling
    schedule_at: Optional[datetime] = None

    # Source tracking
    source_id: Optional[str] = None
    source_type: Optional[str] = None


class SocialPublisher(ABC):
    """Abstract base class for social media publishing."""

    @abstractmethod
    async def publish(self, content: PostContent, account_id: str) -> PublishResult:
        """
        Publish content to a social media platform.

        Args:
            content: Content to publish
            account_id: ID of the social account to publish to

        Returns:
            PublishResult with status and details
        """
        pass

    @abstractmethod
    async def schedule(self, content: PostContent, account_id: str, schedule_at: datetime) -> PublishResult:
        """
        Schedule content for future publishing.

        Args:
            content: Content to publish
            account_id: ID of the social account
            schedule_at: When to publish

        Returns:
            PublishResult with scheduling status
        """
        pass

    @abstractmethod
    async def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """
        Get the current status of a post.

        Args:
            post_id: Platform-specific post ID

        Returns:
            Dictionary with post status and metadata
        """
        pass

    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a published post.

        Args:
            post_id: Platform-specific post ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def verify_account(self, account_id: str) -> bool:
        """
        Verify that an account is properly configured and accessible.

        Args:
            account_id: ID of the social account

        Returns:
            True if account is valid and accessible
        """
        pass
