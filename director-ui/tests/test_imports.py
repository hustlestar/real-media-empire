"""
Import tests for director-ui modules.

Tests that all modules can be imported without errors.
This catches basic syntax errors, missing dependencies, and import issues.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestImports:
    """Test that all modules can be imported."""

    def test_import_data_models(self):
        """Test importing database models."""
        from data.models import (
            Base,
            Channel,
            Author,
            Character,
            Asset,
            FilmProject,
            Presentation,
            AvatarVideo,
            SocialAccount,
            PublishingPost,
            PublishingAnalytics
        )

        # Verify models exist
        assert Base is not None
        assert Channel is not None
        assert Author is not None
        assert Character is not None
        assert Asset is not None
        assert FilmProject is not None
        assert Presentation is not None
        assert AvatarVideo is not None
        assert SocialAccount is not None
        assert PublishingPost is not None
        assert PublishingAnalytics is not None

    def test_import_film_providers(self):
        """Test importing film provider modules."""
        from film.base_provider import VideoProvider
        from film.providers.heygen import (
            HeyGenProvider,
            HeyGenConfig,
            HeyGenBackgroundConfig,
            HeyGenDimensionConfig,
            HeyGenVoiceConfig
        )

        # Verify classes exist
        assert VideoProvider is not None
        assert HeyGenProvider is not None
        assert HeyGenConfig is not None
        assert HeyGenBackgroundConfig is not None
        assert HeyGenDimensionConfig is not None
        assert HeyGenVoiceConfig is not None

    def test_import_social_publishers(self):
        """Test importing social publisher modules."""
        from social.base_publisher import (
            SocialPublisher,
            PublishResult,
            PostContent
        )
        from social.postiz_publisher import (
            PostizPublisher,
            PostizConfig,
            PlatformLimits,
            PLATFORM_LIMITS
        )

        # Verify classes exist
        assert SocialPublisher is not None
        assert PublishResult is not None
        assert PostContent is not None
        assert PostizPublisher is not None
        assert PostizConfig is not None
        assert PlatformLimits is not None
        assert PLATFORM_LIMITS is not None
        assert len(PLATFORM_LIMITS) > 0

    def test_import_api_routers(self):
        """Test importing API router modules."""
        from api.routers import heygen, postiz

        # Verify routers exist
        assert heygen is not None
        assert heygen.router is not None
        assert postiz is not None
        assert postiz.router is not None

    def test_platform_limits_structure(self):
        """Test that platform limits have expected structure."""
        from social.postiz_publisher import PLATFORM_LIMITS

        expected_platforms = ['tiktok', 'youtube', 'instagram', 'facebook', 'twitter', 'linkedin']

        for platform in expected_platforms:
            assert platform in PLATFORM_LIMITS, f"Platform {platform} not found in PLATFORM_LIMITS"

            limits = PLATFORM_LIMITS[platform]
            assert hasattr(limits, 'max_caption_length')
            assert hasattr(limits, 'max_hashtags')
            assert hasattr(limits, 'max_video_size_mb')
            assert hasattr(limits, 'max_image_size_mb')
            assert hasattr(limits, 'supported_formats')
            assert hasattr(limits, 'requires_approval')

            # Verify values are positive
            assert limits.max_caption_length > 0
            assert limits.max_hashtags > 0
            assert limits.max_video_size_mb > 0
            assert limits.max_image_size_mb > 0
            assert len(limits.supported_formats) > 0

    def test_heygen_aspect_ratios(self):
        """Test that HeyGen aspect ratios are properly configured."""
        from film.providers.heygen import HeyGenDimensionConfig

        aspect_ratios = ['9:16', '16:9', '1:1', '4:5']

        for ratio in aspect_ratios:
            config = HeyGenDimensionConfig.from_aspect_ratio(ratio)
            assert config is not None
            assert config.width > 0
            assert config.height > 0

            # Verify aspect ratio math
            if ratio == '9:16':
                assert config.width < config.height
            elif ratio == '16:9':
                assert config.width > config.height
            elif ratio == '1:1':
                assert config.width == config.height
            elif ratio == '4:5':
                assert config.width < config.height


class TestModuleStructure:
    """Test module structure and organization."""

    def test_film_module_structure(self):
        """Test that film module has expected structure."""
        import film
        from film import base_provider
        from film.providers import heygen

        assert film is not None
        assert base_provider is not None
        assert heygen is not None

    def test_social_module_structure(self):
        """Test that social module has expected structure."""
        import social
        from social import base_publisher, postiz_publisher

        assert social is not None
        assert base_publisher is not None
        assert postiz_publisher is not None

    def test_api_routers_registration(self):
        """Test that new routers are registered."""
        from api import app

        # Check that app has routes
        assert app.app is not None

        # Get all routes
        routes = [route.path for route in app.app.routes]

        # Check for HeyGen routes
        heygen_routes = [r for r in routes if '/heygen' in r]
        assert len(heygen_routes) > 0, "No HeyGen routes found"

        # Check for Postiz routes
        postiz_routes = [r for r in routes if '/postiz' in r]
        assert len(postiz_routes) > 0, "No Postiz routes found"


class TestModelInstantiation:
    """Test that models can be instantiated."""

    def test_avatar_video_model(self):
        """Test AvatarVideo model instantiation."""
        from data.models import AvatarVideo

        video = AvatarVideo(
            id="test-id",
            video_id="heygen-video-id",
            script="Test script",
            avatar_id="avatar-1",
            voice_id="voice-1"
        )

        assert video.id == "test-id"
        assert video.video_id == "heygen-video-id"
        assert video.script == "Test script"
        assert video.avatar_id == "avatar-1"
        assert video.voice_id == "voice-1"
        assert video.aspect_ratio == "9:16"  # Default
        assert video.status == "pending"  # Default

    def test_social_account_model(self):
        """Test SocialAccount model instantiation."""
        from data.models import SocialAccount

        account = SocialAccount(
            id="test-account-id",
            platform="tiktok",
            account_name="Test Account",
            account_handle="@testaccount"
        )

        assert account.id == "test-account-id"
        assert account.platform == "tiktok"
        assert account.account_name == "Test Account"
        assert account.account_handle == "@testaccount"
        assert account.is_active is True  # Default

    def test_publishing_post_model(self):
        """Test PublishingPost model instantiation."""
        from data.models import PublishingPost

        post = PublishingPost(
            id="test-post-id",
            social_account_id="account-123",
            content_type="video",
            content_url="https://example.com/video.mp4",
            caption="Test caption",
            platform="tiktok"
        )

        assert post.id == "test-post-id"
        assert post.social_account_id == "account-123"
        assert post.content_type == "video"
        assert post.content_url == "https://example.com/video.mp4"
        assert post.caption == "Test caption"
        assert post.platform == "tiktok"
        assert post.status == "draft"  # Default

    def test_publishing_analytics_model(self):
        """Test PublishingAnalytics model instantiation."""
        from data.models import PublishingAnalytics

        analytics = PublishingAnalytics(
            id="test-analytics-id",
            post_id="post-123"
        )

        assert analytics.id == "test-analytics-id"
        assert analytics.post_id == "post-123"
        assert analytics.views == 0  # Default
        assert analytics.likes == 0  # Default
        assert analytics.engagement_rate == 0.0  # Default
