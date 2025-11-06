"""
TikTok publisher implementation using upload-post.com API.
"""

import logging
from typing import Dict, Optional
from pathlib import Path
import asyncio

from .base import (
    BasePlatform,
    PublishConfig,
    PublishResult,
    PublishStatus,
    PlatformRequirements,
    VideoFormat,
    ValidationError
)
from ..adapters.upload_post import UploadPostClient, TikTokHelper

logger = logging.getLogger(__name__)


class TikTokPublisher(BasePlatform):
    """
    TikTok video publisher using upload-post.com API.

    Requirements:
    - Max duration: 10 minutes (600 seconds)
    - Recommended: 15-60 seconds for best engagement
    - Format: MP4, MOV
    - Aspect ratio: 9:16 (vertical) preferred, 16:9 supported
    - Resolution: 1080x1920 recommended
    """

    def __init__(self, credentials: Dict):
        """
        Initialize TikTok publisher.

        Args:
            credentials: Must contain:
                - api_key: upload-post.com API key
                - user: upload-post.com user identifier
        """
        super().__init__(credentials)

        self.api_key = credentials.get('api_key')
        self.user = credentials.get('user')

        if not self.api_key or not self.user:
            raise ValueError("TikTok publisher requires 'api_key' and 'user' in credentials")

        self.client = UploadPostClient(self.api_key)

    async def authenticate(self) -> bool:
        """Verify credentials and connection."""
        try:
            user_info = await self.client.get_user_info(self.user)

            if not user_info.get('success'):
                logger.error(f"TikTok authentication failed: {user_info.get('error')}")
                return False

            # Check if TikTok is connected
            accounts = user_info.get('connected_accounts', {})
            if 'tiktok' not in accounts:
                logger.error("TikTok account not connected in upload-post.com")
                return False

            logger.info("TikTok authentication successful")
            return True

        except Exception as e:
            logger.error(f"TikTok authentication error: {e}")
            return False

    async def publish_video(
        self,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """
        Publish video to TikTok.

        Args:
            video_path: Path to video file
            config: Publishing configuration

        Returns:
            PublishResult with status and details
        """
        try:
            # Validate video
            validation = self.validate_video(video_path)
            if not validation['valid']:
                return PublishResult(
                    success=False,
                    platform="TikTok",
                    status=PublishStatus.FAILED,
                    error=f"Validation failed: {', '.join(validation['errors'])}"
                )

            # Build TikTok-specific options
            tiktok_options = TikTokHelper.build_options(
                allow_duet=config.platform_specific.get('allow_duet', True),
                allow_stitch=config.platform_specific.get('allow_stitch', True),
                privacy=config.privacy.value
            )

            # Upload via API
            logger.info(f"Uploading to TikTok: {config.title}")
            result = await self.client.upload_video(
                video_path=video_path,
                title=config.title,
                platforms=['tiktok'],
                user=self.user,
                description=config.description,
                **tiktok_options
            )

            if result.get('success'):
                upload_data = result.get('data', {})

                return PublishResult(
                    success=True,
                    video_id=upload_data.get('id'),
                    url=upload_data.get('url'),
                    platform="TikTok",
                    status=PublishStatus.PUBLISHED,
                    metadata=upload_data
                )
            else:
                return PublishResult(
                    success=False,
                    platform="TikTok",
                    status=PublishStatus.FAILED,
                    error=result.get('error', 'Unknown error')
                )

        except Exception as e:
            logger.error(f"TikTok publish error: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform="TikTok",
                status=PublishStatus.FAILED,
                error=str(e)
            )

    async def get_video_status(self, video_id: str) -> PublishStatus:
        """Check status of uploaded video."""
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
            logger.error(f"TikTok status check error: {e}")
            return PublishStatus.FAILED

    def validate_video(self, video_path: str) -> Dict:
        """
        Validate video meets TikTok requirements.

        Returns:
            Dict with validation results
        """
        errors = []
        warnings = []

        try:
            import cv2
            from pathlib import Path

            # Check file exists
            if not Path(video_path).exists():
                errors.append("Video file not found")
                return {'valid': False, 'errors': errors, 'warnings': warnings}

            # Check file size (max 287MB for TikTok)
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            if file_size_mb > 287:
                errors.append(f"File too large: {file_size_mb:.1f}MB (max 287MB)")

            # Check video properties
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                errors.append("Could not open video file")
                return {'valid': False, 'errors': errors, 'warnings': warnings}

            # Get video info
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            cap.release()

            # Check duration (max 10 minutes)
            if duration > 600:
                errors.append(f"Video too long: {duration:.1f}s (max 600s)")
            elif duration > 60:
                warnings.append(f"Video longer than 60s may have lower engagement")

            # Check aspect ratio (prefer 9:16 vertical)
            aspect_ratio = width / height
            if not (0.5 < aspect_ratio < 2.0):
                warnings.append(f"Unusual aspect ratio: {width}x{height}")

            if aspect_ratio > 1.0:
                warnings.append("Horizontal video - vertical (9:16) recommended for TikTok")

            # Check resolution
            if height < 720:
                warnings.append(f"Low resolution: {width}x{height} (1080x1920 recommended)")

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
            warnings.append("OpenCV not available - skipping detailed validation")
            return {
                'valid': True,
                'errors': errors,
                'warnings': warnings,
                'video_info': {}
            }

        except Exception as e:
            logger.error(f"Validation error: {e}")
            errors.append(f"Validation error: {str(e)}")
            return {'valid': False, 'errors': errors, 'warnings': warnings}

    def get_requirements(self) -> PlatformRequirements:
        """Get TikTok platform requirements."""
        return PlatformRequirements(
            max_duration_seconds=600,
            min_duration_seconds=1,
            max_file_size_mb=287,
            supported_formats=[VideoFormat.MP4, VideoFormat.MOV],
            max_title_length=150,
            max_description_length=2200,
            aspect_ratios=["9:16", "16:9", "1:1"],
            recommended_resolution="1080x1920"
        )

    async def delete_video(self, video_id: str) -> bool:
        """Delete video from TikTok."""
        logger.warning("TikTok video deletion not supported via upload-post.com")
        return False

    async def update_video(
        self,
        video_id: str,
        config: PublishConfig
    ) -> PublishResult:
        """Update video metadata."""
        logger.warning("TikTok video update not supported via upload-post.com")
        return PublishResult(
            success=False,
            platform="TikTok",
            status=PublishStatus.FAILED,
            error="Update not supported"
        )

    def supports_scheduling(self) -> bool:
        """TikTok supports scheduled publishing."""
        return True

    def supports_thumbnails(self) -> bool:
        """TikTok does not support custom thumbnails."""
        return False
