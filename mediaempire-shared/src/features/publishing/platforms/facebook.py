"""
Facebook publisher implementation.
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
from ..adapters.upload_post import UploadPostClient, FacebookHelper

logger = logging.getLogger(__name__)


class FacebookPublisher(BasePlatform):
    """Facebook video publisher for Pages and Profiles."""

    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.api_key = credentials.get('api_key')
        self.user = credentials.get('user')
        self.page_id = credentials.get('page_id')  # Required for page posts

        if not self.api_key or not self.user:
            raise ValueError("Facebook publisher requires 'api_key' and 'user'")

        self.client = UploadPostClient(self.api_key)

    async def authenticate(self) -> bool:
        """Verify Facebook connection."""
        try:
            user_info = await self.client.get_user_info(self.user)
            if not user_info.get('success'):
                return False

            accounts = user_info.get('connected_accounts', {})
            if 'facebook' not in accounts:
                logger.error("Facebook account not connected")
                return False

            logger.info("Facebook authentication successful")
            return True
        except Exception as e:
            logger.error(f"Facebook auth error: {e}")
            return False

    async def publish_video(self, video_path: str, config: PublishConfig) -> PublishResult:
        """Publish to Facebook."""
        try:
            validation = self.validate_video(video_path)
            if not validation['valid']:
                return PublishResult(
                    success=False,
                    platform="Facebook",
                    status=PublishStatus.FAILED,
                    error=f"Validation failed: {', '.join(validation['errors'])}"
                )

            # Build Facebook options
            page_id = config.platform_specific.get('page_id', self.page_id)
            if not page_id:
                return PublishResult(
                    success=False,
                    platform="Facebook",
                    status=PublishStatus.FAILED,
                    error="page_id required for Facebook publishing"
                )

            facebook_options = FacebookHelper.build_options(
                page_id=page_id,
                privacy=config.privacy.value,
                scheduled=config.schedule_time.isoformat() if config.schedule_time else None
            )

            logger.info(f"Uploading to Facebook Page {page_id}: {config.title}")
            result = await self.client.upload_video(
                video_path=video_path,
                title=config.title,
                platforms=['facebook'],
                user=self.user,
                description=config.description,
                **facebook_options
            )

            if result.get('success'):
                upload_data = result.get('data', {})
                return PublishResult(
                    success=True,
                    video_id=upload_data.get('id'),
                    url=upload_data.get('url'),
                    platform="Facebook",
                    status=PublishStatus.PUBLISHED,
                    metadata=upload_data
                )
            else:
                return PublishResult(
                    success=False,
                    platform="Facebook",
                    status=PublishStatus.FAILED,
                    error=result.get('error', 'Unknown error')
                )

        except Exception as e:
            logger.error(f"Facebook publish error: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform="Facebook",
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
            logger.error(f"Facebook status error: {e}")
            return PublishStatus.FAILED

    def validate_video(self, video_path: str) -> Dict:
        """Validate video for Facebook."""
        errors = []
        warnings = []

        try:
            if not Path(video_path).exists():
                errors.append("Video file not found")
                return {'valid': False, 'errors': errors, 'warnings': warnings}

            # Max 4GB
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            if file_size_mb > 4096:
                errors.append(f"File too large: {file_size_mb:.1f}MB (max 4GB)")

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
        """Get Facebook requirements."""
        return PlatformRequirements(
            max_duration_seconds=7200,  # 120 minutes
            min_duration_seconds=1,
            max_file_size_mb=4096,
            supported_formats=[VideoFormat.MP4, VideoFormat.MOV],
            max_title_length=255,
            max_description_length=63206,
            aspect_ratios=["16:9", "9:16", "1:1", "4:5"],
            recommended_resolution="1080x1920"
        )

    async def delete_video(self, video_id: str) -> bool:
        return False

    async def update_video(self, video_id: str, config: PublishConfig) -> PublishResult:
        return PublishResult(
            success=False,
            platform="Facebook",
            status=PublishStatus.FAILED,
            error="Update not supported"
        )

    def supports_scheduling(self) -> bool:
        return True

    def supports_thumbnails(self) -> bool:
        return True
