"""
Instagram publisher implementation using upload-post.com API.
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
from ..adapters.upload_post import UploadPostClient, InstagramHelper

logger = logging.getLogger(__name__)


class InstagramPublisher(BasePlatform):
    """
    Instagram video publisher (Reels, Stories, Feed Posts).

    Requirements:
    - Reels: 15-90 seconds, 9:16 vertical
    - Stories: 15 seconds max, 9:16 vertical
    - Feed: Up to 60 seconds, 1:1 or 4:5 preferred
    """

    def __init__(self, credentials: Dict):
        super().__init__(credentials)

        self.api_key = credentials.get('api_key')
        self.user = credentials.get('user')

        if not self.api_key or not self.user:
            raise ValueError("Instagram publisher requires 'api_key' and 'user'")

        self.client = UploadPostClient(self.api_key)

    async def authenticate(self) -> bool:
        """Verify Instagram connection."""
        try:
            user_info = await self.client.get_user_info(self.user)

            if not user_info.get('success'):
                return False

            accounts = user_info.get('connected_accounts', {})
            if 'instagram' not in accounts:
                logger.error("Instagram account not connected")
                return False

            logger.info("Instagram authentication successful")
            return True

        except Exception as e:
            logger.error(f"Instagram auth error: {e}")
            return False

    async def publish_video(
        self,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """Publish video to Instagram."""
        try:
            # Validate
            validation = self.validate_video(video_path)
            if not validation['valid']:
                return PublishResult(
                    success=False,
                    platform="Instagram",
                    status=PublishStatus.FAILED,
                    error=f"Validation failed: {', '.join(validation['errors'])}"
                )

            # Determine post type
            post_type = config.platform_specific.get('post_type', 'reel')

            # Build Instagram options
            instagram_options = InstagramHelper.build_options(
                post_type=post_type,
                location=config.location,
                tag_users=config.platform_specific.get('tag_users')
            )

            # Upload
            logger.info(f"Uploading to Instagram as {post_type}: {config.title}")
            result = await self.client.upload_video(
                video_path=video_path,
                title=config.title,
                platforms=['instagram'],
                user=self.user,
                description=config.description,
                **instagram_options
            )

            if result.get('success'):
                upload_data = result.get('data', {})

                return PublishResult(
                    success=True,
                    video_id=upload_data.get('id'),
                    url=upload_data.get('url'),
                    platform="Instagram",
                    status=PublishStatus.PUBLISHED,
                    metadata=upload_data
                )
            else:
                return PublishResult(
                    success=False,
                    platform="Instagram",
                    status=PublishStatus.FAILED,
                    error=result.get('error', 'Unknown error')
                )

        except Exception as e:
            logger.error(f"Instagram publish error: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform="Instagram",
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
            logger.error(f"Instagram status error: {e}")
            return PublishStatus.FAILED

    def validate_video(self, video_path: str) -> Dict:
        """Validate video for Instagram."""
        errors = []
        warnings = []

        try:
            import cv2
            from pathlib import Path

            if not Path(video_path).exists():
                errors.append("Video file not found")
                return {'valid': False, 'errors': errors, 'warnings': warnings}

            # Max 100MB
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            if file_size_mb > 100:
                errors.append(f"File too large: {file_size_mb:.1f}MB (max 100MB)")

            # Check video properties
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                errors.append("Could not open video")
                return {'valid': False, 'errors': errors, 'warnings': warnings}

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            cap.release()

            # Reels: 15-90 seconds
            if duration < 3:
                errors.append(f"Video too short: {duration:.1f}s (min 3s)")
            elif duration > 90:
                warnings.append(f"Video over 90s - will be posted as feed video, not Reel")

            # Prefer vertical (9:16)
            aspect_ratio = width / height
            if aspect_ratio > 1.0:
                warnings.append("Horizontal video - vertical (9:16) recommended for Reels")

            video_info = {
                'width': width,
                'height': height,
                'fps': fps,
                'duration': duration,
                'file_size_mb': file_size_mb
            }

            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'video_info': video_info
            }

        except ImportError:
            warnings.append("OpenCV not available - skipping validation")
            return {'valid': True, 'errors': errors, 'warnings': warnings}

        except Exception as e:
            logger.error(f"Validation error: {e}")
            errors.append(str(e))
            return {'valid': False, 'errors': errors, 'warnings': warnings}

    def get_requirements(self) -> PlatformRequirements:
        """Get Instagram requirements."""
        return PlatformRequirements(
            max_duration_seconds=90,
            min_duration_seconds=3,
            max_file_size_mb=100,
            supported_formats=[VideoFormat.MP4, VideoFormat.MOV],
            max_title_length=150,
            max_description_length=2200,
            aspect_ratios=["9:16", "4:5", "1:1"],
            recommended_resolution="1080x1920"
        )

    async def delete_video(self, video_id: str) -> bool:
        """Delete not supported."""
        return False

    async def update_video(self, video_id: str, config: PublishConfig) -> PublishResult:
        """Update not supported."""
        return PublishResult(
            success=False,
            platform="Instagram",
            status=PublishStatus.FAILED,
            error="Update not supported"
        )

    def supports_scheduling(self) -> bool:
        return True

    def supports_thumbnails(self) -> bool:
        return True
