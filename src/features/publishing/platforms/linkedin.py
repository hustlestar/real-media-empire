"""
LinkedIn publisher implementation.
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
from ..adapters.upload_post import UploadPostClient, LinkedInHelper

logger = logging.getLogger(__name__)


class LinkedInPublisher(BasePlatform):
    """LinkedIn video publisher for professional content."""

    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.api_key = credentials.get('api_key')
        self.user = credentials.get('user')

        if not self.api_key or not self.user:
            raise ValueError("LinkedIn publisher requires 'api_key' and 'user'")

        self.client = UploadPostClient(self.api_key)

    async def authenticate(self) -> bool:
        """Verify LinkedIn connection."""
        try:
            user_info = await self.client.get_user_info(self.user)
            if not user_info.get('success'):
                return False

            accounts = user_info.get('connected_accounts', {})
            if 'linkedin' not in accounts:
                logger.error("LinkedIn account not connected")
                return False

            logger.info("LinkedIn authentication successful")
            return True
        except Exception as e:
            logger.error(f"LinkedIn auth error: {e}")
            return False

    async def publish_video(self, video_path: str, config: PublishConfig) -> PublishResult:
        """Publish to LinkedIn."""
        try:
            validation = self.validate_video(video_path)
            if not validation['valid']:
                return PublishResult(
                    success=False,
                    platform="LinkedIn",
                    status=PublishStatus.FAILED,
                    error=f"Validation failed: {', '.join(validation['errors'])}"
                )

            # Build LinkedIn options
            linkedin_options = LinkedInHelper.build_options(
                visibility=config.platform_specific.get('visibility', 'public'),
                commentary=config.description
            )

            logger.info(f"Uploading to LinkedIn: {config.title}")
            result = await self.client.upload_video(
                video_path=video_path,
                title=config.title,
                platforms=['linkedin'],
                user=self.user,
                description=config.description,
                **linkedin_options
            )

            if result.get('success'):
                upload_data = result.get('data', {})
                return PublishResult(
                    success=True,
                    video_id=upload_data.get('id'),
                    url=upload_data.get('url'),
                    platform="LinkedIn",
                    status=PublishStatus.PUBLISHED,
                    metadata=upload_data
                )
            else:
                return PublishResult(
                    success=False,
                    platform="LinkedIn",
                    status=PublishStatus.FAILED,
                    error=result.get('error', 'Unknown error')
                )

        except Exception as e:
            logger.error(f"LinkedIn publish error: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform="LinkedIn",
                status=PublishStatus.FAILED,
                error=str(e)
            )

    async def get_video_status(self, video_id: str) -> PublishStatus:
        """Check video status."""
        try:
            status = await self.client.get_upload_status(video_id)
            if status.get('success'):
                state = status.get('status', 'unknown').lower()
                status_map = {
                    'pending': PublishStatus.PENDING,
                    'uploading': PublishStatus.UPLOADING,
                    'processing': PublishStatus.PROCESSING,
                    'published': PublishStatus.PUBLISHED,
                    'failed': PublishStatus.FAILED
                }
                return status_map.get(state, PublishStatus.PENDING)
            return PublishStatus.FAILED
        except Exception as e:
            logger.error(f"LinkedIn status error: {e}")
            return PublishStatus.FAILED

    def validate_video(self, video_path: str) -> Dict:
        """Validate video for LinkedIn."""
        errors = []
        warnings = []

        try:
            if not Path(video_path).exists():
                errors.append("Video file not found")
                return {'valid': False, 'errors': errors, 'warnings': warnings}

            # Max 5GB
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            if file_size_mb > 5120:
                errors.append(f"File too large: {file_size_mb:.1f}MB (max 5GB)")

            # LinkedIn prefers professional, longer-form content
            if file_size_mb < 1:
                warnings.append("Very short video - LinkedIn favors substantive content")

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'video_info': {'file_size_mb': file_size_mb}
            }

        except Exception as e:
            errors.append(str(e))
            return {'valid': False, 'errors': errors, 'warnings': warnings}

    def get_requirements(self) -> PlatformRequirements:
        """Get LinkedIn requirements."""
        return PlatformRequirements(
            max_duration_seconds=600,  # 10 minutes
            min_duration_seconds=3,
            max_file_size_mb=5120,
            supported_formats=[VideoFormat.MP4],
            max_title_length=200,
            max_description_length=3000,
            aspect_ratios=["16:9", "9:16", "1:1"],
            recommended_resolution="1920x1080"
        )

    async def delete_video(self, video_id: str) -> bool:
        return False

    async def update_video(self, video_id: str, config: PublishConfig) -> PublishResult:
        return PublishResult(
            success=False,
            platform="LinkedIn",
            status=PublishStatus.FAILED,
            error="Update not supported"
        )

    def supports_scheduling(self) -> bool:
        return False  # LinkedIn doesn't support scheduled posts via API

    def supports_thumbnails(self) -> bool:
        return True
