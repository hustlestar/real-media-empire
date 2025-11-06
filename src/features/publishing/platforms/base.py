"""
Base platform interface for multi-platform publishing.

All social media platform publishers implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class VideoFormat(str, Enum):
    """Supported video formats"""
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    WEBM = "webm"


class PrivacyStatus(str, Enum):
    """Video privacy status"""
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class PublishStatus(str, Enum):
    """Publishing status"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class PublishConfig(BaseModel):
    """Configuration for publishing a video"""
    title: str
    description: str
    tags: List[str] = []
    privacy: PrivacyStatus = PrivacyStatus.PUBLIC
    schedule_time: Optional[datetime] = None
    platform_specific: Dict = {}  # Platform-specific options

    # Optional thumbnail
    thumbnail_path: Optional[str] = None

    # Category/type
    category: Optional[str] = None

    # Location/geographic data
    location: Optional[str] = None


class PlatformRequirements(BaseModel):
    """Platform-specific requirements for videos"""
    max_duration_seconds: int
    min_duration_seconds: int
    max_file_size_mb: int
    supported_formats: List[VideoFormat]
    max_title_length: int
    max_description_length: int
    aspect_ratios: List[str]  # e.g., ["9:16", "16:9", "1:1"]
    recommended_resolution: str  # e.g., "1080x1920"


class PublishResult(BaseModel):
    """Result from publishing operation"""
    success: bool
    video_id: Optional[str] = None
    url: Optional[str] = None
    platform: str
    status: PublishStatus
    error: Optional[str] = None
    warnings: List[str] = []
    metadata: Dict = {}  # Additional platform-specific data
    published_at: Optional[datetime] = None


class BasePlatform(ABC):
    """
    Base class for all social media platform publishers.

    All platform implementations must inherit from this class
    and implement the abstract methods.
    """

    def __init__(self, credentials: Dict):
        """
        Initialize platform with credentials.

        Args:
            credentials: Platform-specific authentication credentials
        """
        self.credentials = credentials
        self.platform_name = self.__class__.__name__.replace("Publisher", "")

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the platform.

        Returns:
            True if authentication successful, False otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    async def publish_video(
        self,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """
        Publish video to the platform.

        Args:
            video_path: Path to video file
            config: Publishing configuration

        Returns:
            PublishResult with status and details

        Raises:
            PublishError: If publishing fails
            ValidationError: If video doesn't meet requirements
        """
        pass

    @abstractmethod
    async def get_video_status(self, video_id: str) -> PublishStatus:
        """
        Check status of uploaded video.

        Args:
            video_id: Platform-specific video identifier

        Returns:
            Current publishing status
        """
        pass

    @abstractmethod
    def validate_video(self, video_path: str) -> Dict:
        """
        Validate video meets platform requirements.

        Args:
            video_path: Path to video file

        Returns:
            Dict with validation results:
                {
                    "valid": bool,
                    "errors": List[str],
                    "warnings": List[str],
                    "video_info": Dict
                }
        """
        pass

    @abstractmethod
    def get_requirements(self) -> PlatformRequirements:
        """
        Get platform-specific video requirements.

        Returns:
            PlatformRequirements object
        """
        pass

    @abstractmethod
    async def delete_video(self, video_id: str) -> bool:
        """
        Delete video from platform.

        Args:
            video_id: Platform-specific video identifier

        Returns:
            True if deletion successful
        """
        pass

    @abstractmethod
    async def update_video(
        self,
        video_id: str,
        config: PublishConfig
    ) -> PublishResult:
        """
        Update video metadata.

        Args:
            video_id: Platform-specific video identifier
            config: Updated configuration

        Returns:
            PublishResult with updated status
        """
        pass

    def supports_scheduling(self) -> bool:
        """
        Check if platform supports scheduled publishing.

        Returns:
            True if scheduling is supported
        """
        return False

    def supports_thumbnails(self) -> bool:
        """
        Check if platform supports custom thumbnails.

        Returns:
            True if custom thumbnails supported
        """
        return False

    def get_platform_name(self) -> str:
        """Get platform name."""
        return self.platform_name


# Custom exceptions

class PlatformError(Exception):
    """Base exception for platform errors"""
    pass


class AuthenticationError(PlatformError):
    """Authentication failed"""
    pass


class PublishError(PlatformError):
    """Publishing failed"""
    pass


class ValidationError(PlatformError):
    """Video validation failed"""
    pass


class RateLimitError(PlatformError):
    """Platform rate limit exceeded"""
    pass


class QuotaExceededError(PlatformError):
    """Platform quota exceeded"""
    pass
