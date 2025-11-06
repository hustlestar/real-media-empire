"""
Publishing Manager - Centralized coordination of all platform publishers.
Supports multi-platform publishing, batch operations, and error handling.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .platforms.base import (
    BasePlatform,
    PublishConfig,
    PublishResult,
    PublishStatus
)
from .platforms.tiktok import TikTokPublisher
from .platforms.instagram import InstagramPublisher
from .platforms.facebook import FacebookPublisher
from .platforms.linkedin import LinkedInPublisher
from .platforms.youtube import YouTubePublisher

logger = logging.getLogger(__name__)


class PublishingManager:
    """Centralized manager for multi-platform video publishing."""

    def __init__(self):
        self.platforms: Dict[str, BasePlatform] = {}
        self.accounts: Dict[str, Dict[str, BasePlatform]] = {}  # account_id -> {platform: publisher}

    def add_account(
        self,
        account_id: str,
        platform: str,
        credentials: Dict
    ) -> None:
        """
        Add a new account for a specific platform.

        Args:
            account_id: Unique identifier for this account
            platform: Platform name (tiktok, instagram, facebook, linkedin, youtube)
            credentials: Platform-specific credentials
        """
        platform_lower = platform.lower()

        # Create publisher instance
        publisher = self._create_publisher(platform_lower, credentials)

        if account_id not in self.accounts:
            self.accounts[account_id] = {}

        self.accounts[account_id][platform_lower] = publisher
        logger.info(f"Added {platform} account: {account_id}")

    def _create_publisher(self, platform: str, credentials: Dict) -> BasePlatform:
        """Create publisher instance for platform."""
        publishers = {
            'tiktok': TikTokPublisher,
            'instagram': InstagramPublisher,
            'facebook': FacebookPublisher,
            'linkedin': LinkedInPublisher,
            'youtube': YouTubePublisher,
        }

        if platform not in publishers:
            raise ValueError(f"Unsupported platform: {platform}")

        return publishers[platform](credentials)

    async def authenticate_account(
        self,
        account_id: str,
        platform: str
    ) -> bool:
        """
        Authenticate a specific account.

        Args:
            account_id: Account identifier
            platform: Platform name

        Returns:
            True if authentication successful
        """
        if account_id not in self.accounts:
            raise ValueError(f"Account not found: {account_id}")

        platform_lower = platform.lower()
        if platform_lower not in self.accounts[account_id]:
            raise ValueError(f"Platform {platform} not configured for account {account_id}")

        publisher = self.accounts[account_id][platform_lower]
        return await publisher.authenticate()

    async def publish_to_platform(
        self,
        account_id: str,
        platform: str,
        video_path: str,
        config: PublishConfig
    ) -> PublishResult:
        """
        Publish video to a single platform for specific account.

        Args:
            account_id: Account identifier
            platform: Platform to publish to
            video_path: Path to video file
            config: Publishing configuration

        Returns:
            PublishResult with status and details
        """
        if not Path(video_path).exists():
            return PublishResult(
                success=False,
                platform=platform,
                status=PublishStatus.FAILED,
                error="Video file not found"
            )

        if account_id not in self.accounts:
            return PublishResult(
                success=False,
                platform=platform,
                status=PublishStatus.FAILED,
                error=f"Account not found: {account_id}"
            )

        platform_lower = platform.lower()
        if platform_lower not in self.accounts[account_id]:
            return PublishResult(
                success=False,
                platform=platform,
                status=PublishStatus.FAILED,
                error=f"Platform {platform} not configured for account {account_id}"
            )

        publisher = self.accounts[account_id][platform_lower]

        try:
            # Authenticate if needed
            if not await publisher.authenticate():
                return PublishResult(
                    success=False,
                    platform=platform,
                    status=PublishStatus.FAILED,
                    error="Authentication failed"
                )

            # Publish video
            logger.info(f"Publishing to {platform} for account {account_id}: {config.title}")
            result = await publisher.publish_video(video_path, config)

            return result

        except Exception as e:
            logger.error(f"Error publishing to {platform} for {account_id}: {e}", exc_info=True)
            return PublishResult(
                success=False,
                platform=platform,
                status=PublishStatus.FAILED,
                error=str(e)
            )

    async def publish_multi_platform(
        self,
        account_id: str,
        platforms: List[str],
        video_path: str,
        config: PublishConfig
    ) -> Dict[str, PublishResult]:
        """
        Publish video to multiple platforms simultaneously.

        Args:
            account_id: Account identifier
            platforms: List of platform names
            video_path: Path to video file
            config: Publishing configuration (same for all platforms)

        Returns:
            Dictionary mapping platform name to PublishResult
        """
        logger.info(f"Multi-platform publish for {account_id}: {platforms}")

        # Create tasks for parallel publishing
        tasks = []
        platform_names = []

        for platform in platforms:
            tasks.append(self.publish_to_platform(account_id, platform, video_path, config))
            platform_names.append(platform)

        # Execute all publishes in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results to platforms
        result_map = {}
        for platform, result in zip(platform_names, results):
            if isinstance(result, Exception):
                result_map[platform] = PublishResult(
                    success=False,
                    platform=platform,
                    status=PublishStatus.FAILED,
                    error=str(result)
                )
            else:
                result_map[platform] = result

        # Log summary
        successes = sum(1 for r in result_map.values() if r.success)
        logger.info(f"Multi-platform publish complete: {successes}/{len(platforms)} successful")

        return result_map

    async def publish_batch(
        self,
        batch: List[Dict]
    ) -> List[Dict[str, PublishResult]]:
        """
        Publish multiple videos to multiple platforms in batch.

        Args:
            batch: List of publish specifications, each containing:
                - account_id: Account identifier
                - platforms: List of platform names
                - video_path: Path to video file
                - config: PublishConfig instance

        Returns:
            List of result dictionaries (one per video)
        """
        logger.info(f"Batch publish: {len(batch)} videos")

        tasks = []
        for spec in batch:
            task = self.publish_multi_platform(
                account_id=spec['account_id'],
                platforms=spec['platforms'],
                video_path=spec['video_path'],
                config=spec['config']
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Log batch summary
        total_publishes = sum(len(r) for r in results)
        total_successes = sum(
            sum(1 for pub in r.values() if pub.success)
            for r in results
        )
        logger.info(f"Batch publish complete: {total_successes}/{total_publishes} successful")

        return results

    async def check_video_status(
        self,
        account_id: str,
        platform: str,
        video_id: str
    ) -> PublishStatus:
        """
        Check status of uploaded video.

        Args:
            account_id: Account identifier
            platform: Platform name
            video_id: Video identifier on platform

        Returns:
            PublishStatus enum
        """
        if account_id not in self.accounts:
            return PublishStatus.FAILED

        platform_lower = platform.lower()
        if platform_lower not in self.accounts[account_id]:
            return PublishStatus.FAILED

        publisher = self.accounts[account_id][platform_lower]
        return await publisher.get_video_status(video_id)

    def validate_video_for_platforms(
        self,
        video_path: str,
        platforms: List[str]
    ) -> Dict[str, Dict]:
        """
        Validate video against requirements for multiple platforms.

        Args:
            video_path: Path to video file
            platforms: List of platform names to validate against

        Returns:
            Dictionary mapping platform name to validation results
        """
        results = {}

        for platform in platforms:
            platform_lower = platform.lower()

            # Get any publisher for this platform (requirements are platform-wide)
            publisher = None
            for account_publishers in self.accounts.values():
                if platform_lower in account_publishers:
                    publisher = account_publishers[platform_lower]
                    break

            if publisher is None:
                # Create temporary publisher just for validation
                try:
                    publisher = self._create_publisher(platform_lower, {})
                except ValueError:
                    results[platform] = {
                        'valid': False,
                        'errors': [f'Unsupported platform: {platform}'],
                        'warnings': []
                    }
                    continue

            validation = publisher.validate_video(video_path)
            results[platform] = validation

        return results

    def get_account_platforms(self, account_id: str) -> List[str]:
        """Get list of platforms configured for an account."""
        if account_id not in self.accounts:
            return []
        return list(self.accounts[account_id].keys())

    def list_all_accounts(self) -> List[Dict]:
        """List all configured accounts with their platforms."""
        accounts = []
        for account_id, platforms in self.accounts.items():
            accounts.append({
                'account_id': account_id,
                'platforms': list(platforms.keys())
            })
        return accounts

    async def delete_video(
        self,
        account_id: str,
        platform: str,
        video_id: str
    ) -> bool:
        """
        Delete video from platform.

        Args:
            account_id: Account identifier
            platform: Platform name
            video_id: Video identifier on platform

        Returns:
            True if deletion successful
        """
        if account_id not in self.accounts:
            return False

        platform_lower = platform.lower()
        if platform_lower not in self.accounts[account_id]:
            return False

        publisher = self.accounts[account_id][platform_lower]
        return await publisher.delete_video(video_id)

    async def update_video(
        self,
        account_id: str,
        platform: str,
        video_id: str,
        config: PublishConfig
    ) -> PublishResult:
        """
        Update video metadata on platform.

        Args:
            account_id: Account identifier
            platform: Platform name
            video_id: Video identifier on platform
            config: New configuration

        Returns:
            PublishResult with update status
        """
        if account_id not in self.accounts:
            return PublishResult(
                success=False,
                platform=platform,
                status=PublishStatus.FAILED,
                error=f"Account not found: {account_id}"
            )

        platform_lower = platform.lower()
        if platform_lower not in self.accounts[account_id]:
            return PublishResult(
                success=False,
                platform=platform,
                status=PublishStatus.FAILED,
                error=f"Platform {platform} not configured for account {account_id}"
            )

        publisher = self.accounts[account_id][platform_lower]
        return await publisher.update_video(video_id, config)
