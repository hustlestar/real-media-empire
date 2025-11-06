"""
YouTube publisher implementation.
Wraps existing YouTubeUploader for platform interface.
"""

import logging
from typing import Dict
from pathlib import Path

from .base import (
    BasePlatform,
    PublishConfig,
    PublishResult,
    PublishStatus,
    PlatformRequirements,
    VideoFormat
)

# Import existing YouTube uploader
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from social.you_tube import YouTubeUploader

logger = logging.getLogger(__name__)


class YouTubePublisher(BasePlatform):
    """YouTube video publisher using existing YouTubeUploader."""

    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.client_secrets_file = credentials.get('client_secrets_file')
        self.channel_name = credentials.get('channel_name')
        self.channel_id = credentials.get('channel_id')
        self.oauth_storage_dir = credentials.get('oauth_storage_dir')

        if not all([self.client_secrets_file, self.channel_name, self.channel_id]):
            raise ValueError("YouTube publisher requires 'client_secrets_file', 'channel_name', and 'channel_id'")

        # Create YouTubeUploader instance
        self.uploader = YouTubeUploader(
            client_secrets_file=self.client_secrets_file,
            channel_name=self.channel_name,
            channel_id=self.channel_id,
            oath_storage_dir=self.oauth_storage_dir if self.oauth_storage_dir else None
        )

    async def authenticate(self) -> bool:
        """Authenticate with YouTube."""
        try:
            self.uploader.authenticate()
            logger.info(f"YouTube authentication successful for {self.channel_name}")
            return True
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False

    async def publish_video(self, video_path: str, config: PublishConfig) -> PublishResult:
        """Publish video to YouTube."""
        try:
            # Validate video
            validation = self.validate_video(video_path)
            if not validation['valid']:
                return PublishResult(
                    success=False,
                    platform="YouTube",
                    status=PublishStatus.FAILED,
                    error=f"Validation failed: {', '.join(validation['errors'])}"
                )

            # Extract YouTube-specific options
            youtube_opts = config.platform_specific.get('youtube', {})
            category = youtube_opts.get('category', '22')  # Default: People & Blogs
            privacy_status = youtube_opts.get('privacy_status', 'private')

            # Prepare tags
            tags = config.tags if config.tags else []

            logger.info(f"Uploading to YouTube: {config.title}")

            # Upload video
            video_id = self.uploader.upload_video(
                file_path=video_path,
                title=config.title,
                description=config.description or "",
                category=category,
                tags=tags,
                privacy_status=privacy_status
            )

            # Upload thumbnail if provided
            thumbnail_url = None
            if config.thumbnail_path and Path(config.thumbnail_path).exists():
                logger.info(f"Uploading thumbnail: {config.thumbnail_path}")
                thumbnail_url = self.uploader.upload_thumbnail(
                    file_path=config.thumbnail_path,
                    video_id=video_id
                )

            return PublishResult(
                success=True,
                video_id=video_id,
                url=f"https://www.youtube.com/watch?v={video_id}",
                platform="YouTube",
                status=PublishStatus.PUBLISHED,
                metadata={
                    'video_id': video_id,
                    'channel_id': self.channel_id,
                    'channel_name': self.channel_name,
                    'thumbnail_url': thumbnail_url,
                    'privacy_status': privacy_status
                }
            )

        except Exception as e:
            logger.error(f"YouTube publish error: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform="YouTube",
                status=PublishStatus.FAILED,
                error=str(e)
            )

    async def get_video_status(self, video_id: str) -> PublishStatus:
        """Check YouTube video status."""
        try:
            # YouTube videos are immediately published after upload
            # Could add API call to check processing status if needed
            return PublishStatus.PUBLISHED
        except Exception as e:
            logger.error(f"YouTube status check error: {e}")
            return PublishStatus.FAILED

    def validate_video(self, video_path: str) -> Dict:
        """Validate video for YouTube."""
        errors = []
        warnings = []

        try:
            if not Path(video_path).exists():
                errors.append("Video file not found")
                return {'valid': False, 'errors': errors, 'warnings': warnings}

            # Max 256GB (but practically much less)
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            if file_size_mb > 256 * 1024:  # 256GB
                errors.append(f"File too large: {file_size_mb:.1f}MB (max 256GB)")

            # YouTube recommends certain specs
            if file_size_mb > 128 * 1024:  # 128GB
                warnings.append("Very large file - upload may take a long time")

            # Check file extension
            video_ext = Path(video_path).suffix.lower()
            recommended_formats = ['.mp4', '.mov', '.avi', '.flv', '.wmv']
            if video_ext not in recommended_formats:
                warnings.append(f"Format {video_ext} may not be optimal. Recommended: {', '.join(recommended_formats)}")

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'video_info': {
                    'file_size_mb': file_size_mb,
                    'format': video_ext
                }
            }

        except Exception as e:
            errors.append(str(e))
            return {'valid': False, 'errors': errors, 'warnings': warnings}

    def get_requirements(self) -> PlatformRequirements:
        """Get YouTube requirements."""
        return PlatformRequirements(
            max_duration_seconds=43200,  # 12 hours for verified accounts
            min_duration_seconds=1,
            max_file_size_mb=256 * 1024,  # 256GB
            supported_formats=[
                VideoFormat.MP4,
                VideoFormat.MOV,
                VideoFormat.AVI,
                VideoFormat.FLV,
                VideoFormat.WMV
            ],
            max_title_length=100,
            max_description_length=5000,
            aspect_ratios=["16:9", "9:16", "1:1", "4:3", "21:9"],
            recommended_resolution="1920x1080"
        )

    async def delete_video(self, video_id: str) -> bool:
        """
        Delete video from YouTube.
        Note: Requires implementation of delete in YouTubeUploader.
        """
        # Not implemented in current YouTubeUploader
        logger.warning("YouTube video deletion not implemented")
        return False

    async def update_video(self, video_id: str, config: PublishConfig) -> PublishResult:
        """
        Update video metadata on YouTube.
        Note: Requires implementation of update in YouTubeUploader.
        """
        # Not implemented in current YouTubeUploader
        return PublishResult(
            success=False,
            platform="YouTube",
            status=PublishStatus.FAILED,
            error="Update not implemented"
        )

    def supports_scheduling(self) -> bool:
        """YouTube supports scheduled publishing."""
        return True

    def supports_thumbnails(self) -> bool:
        """YouTube supports custom thumbnails."""
        return True

    def supports_playlists(self) -> bool:
        """YouTube supports playlists."""
        return True

    async def add_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """
        Add video to YouTube playlist.
        Note: Requires implementation in YouTubeUploader.
        """
        logger.warning("YouTube playlist addition not implemented")
        return False

    async def add_comment(self, video_id: str, comment_text: str) -> bool:
        """Add comment to YouTube video."""
        try:
            self.uploader.insert_comment(video_id=video_id, comment_text=comment_text)
            logger.info(f"Comment added to video {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return False
