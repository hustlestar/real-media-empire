"""
upload-post.com API adapter for multi-platform publishing.

This adapter provides a unified interface for publishing to multiple platforms
through the upload-post.com service.

Supports: TikTok, Instagram, Facebook, LinkedIn, YouTube
"""

import aiohttp
import asyncio
from typing import Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class UploadPostClient:
    """
    Client for upload-post.com API.

    This service provides a unified API for publishing videos to multiple platforms.
    Sign up at: https://upload-post.com
    """

    BASE_URL = "https://api.upload-post.com/api"

    def __init__(self, api_key: str):
        """
        Initialize client with API key.

        Args:
            api_key: API key from upload-post.com dashboard
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Apikey {api_key}"
        }

    async def upload_video(
        self,
        video_path: str,
        title: str,
        platforms: list[str],
        user: str,
        description: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Upload video to one or more platforms.

        Args:
            video_path: Path to video file
            title: Video title
            platforms: List of platform names (e.g., ["tiktok", "instagram"])
            user: User identifier from upload-post.com
            description: Optional video description
            **kwargs: Platform-specific options

        Returns:
            Dict with upload results

        Platforms supported:
            - "tiktok"
            - "instagram"
            - "facebook"
            - "linkedin"
            - "youtube"
        """
        url = f"{self.BASE_URL}/upload"

        # Build form data
        form_data = aiohttp.FormData()

        # Add video file
        video_file = open(video_path, 'rb')
        form_data.add_field(
            'video',
            video_file,
            filename=Path(video_path).name,
            content_type='video/mp4'
        )

        # Add metadata
        form_data.add_field('title', title)
        form_data.add_field('user', user)

        if description:
            form_data.add_field('description', description)

        # Add platforms (multi-value field)
        for platform in platforms:
            form_data.add_field('platform[]', platform)

        # Add platform-specific options
        for key, value in kwargs.items():
            form_data.add_field(key, str(value))

        # Upload
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(url, data=form_data) as response:
                    video_file.close()

                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully uploaded to {', '.join(platforms)}")
                        return {
                            "success": True,
                            "data": result,
                            "platforms": platforms
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Upload failed: {error_text}")
                        return {
                            "success": False,
                            "error": error_text,
                            "status_code": response.status
                        }

        except Exception as e:
            logger.error(f"Upload exception: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_upload_status(self, upload_id: str) -> Dict:
        """
        Check status of an upload.

        Args:
            upload_id: Upload identifier from upload response

        Returns:
            Dict with status information
        """
        url = f"{self.BASE_URL}/status/{upload_id}"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            "success": False,
                            "error": await response.text()
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_user_info(self, user: str) -> Dict:
        """
        Get user account information.

        Args:
            user: User identifier

        Returns:
            Dict with user information including connected accounts
        """
        url = f"{self.BASE_URL}/user/{user}"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            "success": False,
                            "error": await response.text()
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def list_connected_accounts(self, user: str) -> Dict:
        """
        List all connected social media accounts for user.

        Args:
            user: User identifier

        Returns:
            Dict with list of connected accounts per platform
        """
        user_info = await self.get_user_info(user)
        if user_info.get("success"):
            return {
                "success": True,
                "accounts": user_info.get("connected_accounts", {})
            }
        return user_info


# Platform-specific helpers

class TikTokHelper:
    """Helper methods for TikTok-specific options"""

    @staticmethod
    def build_options(
        allow_duet: bool = True,
        allow_stitch: bool = True,
        privacy: str = "public"
    ) -> Dict:
        """Build TikTok-specific options"""
        return {
            "tiktok_allow_duet": allow_duet,
            "tiktok_allow_stitch": allow_stitch,
            "tiktok_privacy": privacy
        }


class InstagramHelper:
    """Helper methods for Instagram-specific options"""

    @staticmethod
    def build_options(
        post_type: str = "reel",  # "reel", "story", "post"
        location: Optional[str] = None,
        tag_users: Optional[list[str]] = None
    ) -> Dict:
        """Build Instagram-specific options"""
        options = {
            "instagram_type": post_type
        }
        if location:
            options["instagram_location"] = location
        if tag_users:
            options["instagram_tags"] = ",".join(tag_users)
        return options


class FacebookHelper:
    """Helper methods for Facebook-specific options"""

    @staticmethod
    def build_options(
        page_id: str,
        privacy: str = "public",
        scheduled: Optional[str] = None
    ) -> Dict:
        """Build Facebook-specific options"""
        options = {
            "facebook_page_id": page_id,
            "facebook_privacy": privacy
        }
        if scheduled:
            options["facebook_scheduled"] = scheduled
        return options


class LinkedInHelper:
    """Helper methods for LinkedIn-specific options"""

    @staticmethod
    def build_options(
        visibility: str = "public",  # "public", "connections"
        commentary: Optional[str] = None
    ) -> Dict:
        """Build LinkedIn-specific options"""
        options = {
            "linkedin_visibility": visibility
        }
        if commentary:
            options["linkedin_commentary"] = commentary
        return options


class YouTubeHelper:
    """Helper methods for YouTube-specific options"""

    @staticmethod
    def build_options(
        privacy: str = "public",
        category: str = "22",  # People & Blogs
        made_for_kids: bool = False,
        tags: Optional[list[str]] = None
    ) -> Dict:
        """Build YouTube-specific options"""
        options = {
            "youtube_privacy": privacy,
            "youtube_category": category,
            "youtube_made_for_kids": made_for_kids
        }
        if tags:
            options["youtube_tags"] = ",".join(tags)
        return options
