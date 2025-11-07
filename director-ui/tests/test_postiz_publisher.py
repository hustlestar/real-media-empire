"""
Mock tests for Postiz publisher.

Tests the Postiz social media publisher with mocked HTTP calls.
No real API calls are made.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from social.postiz_publisher import (
    PostizPublisher,
    PostizConfig,
    PlatformLimits,
    PLATFORM_LIMITS
)
from social.base_publisher import PostContent, PublishResult


@pytest.fixture
def postiz_config():
    """Create a test Postiz configuration."""
    return PostizConfig(
        api_key="test-api-key",
        base_url="https://api.postiz.com",
        timeout=30,
        max_retries=1
    )


@pytest.fixture
def postiz_publisher(postiz_config):
    """Create a Postiz publisher with test configuration."""
    return PostizPublisher(postiz_config)


@pytest.fixture
def test_post_content():
    """Create test post content."""
    return PostContent(
        platform="tiktok",
        content_type="video",
        content_url="https://example.com/video.mp4",
        caption="Test caption for video post",
        hashtags=["test", "video", "content"],
        platform_settings={},
        source_id="test-source-123",
        source_type="avatar_video"
    )


class TestPostizConfig:
    """Test Postiz configuration."""

    def test_config_creation(self):
        """Test creating a Postiz configuration."""
        config = PostizConfig(
            api_key="test-key",
            base_url="https://test.com",
            timeout=60,
            max_retries=5
        )

        assert config.api_key == "test-key"
        assert config.base_url == "https://test.com"
        assert config.timeout == 60
        assert config.max_retries == 5

    def test_config_defaults(self):
        """Test default configuration values."""
        config = PostizConfig(api_key="test-key")

        assert config.base_url == "https://api.postiz.com"
        assert config.timeout == 30
        assert config.max_retries == 3


class TestPlatformLimits:
    """Test platform limits configuration."""

    def test_all_platforms_exist(self):
        """Test that all expected platforms have limits."""
        expected_platforms = ['tiktok', 'youtube', 'instagram', 'facebook', 'twitter', 'linkedin']

        for platform in expected_platforms:
            assert platform in PLATFORM_LIMITS
            limits = PLATFORM_LIMITS[platform]
            assert isinstance(limits, PlatformLimits)

    def test_tiktok_limits(self):
        """Test TikTok platform limits."""
        limits = PLATFORM_LIMITS['tiktok']

        assert limits.max_caption_length == 2200
        assert limits.max_hashtags == 30
        assert limits.max_video_size_mb == 287
        assert limits.max_image_size_mb == 10
        assert 'mp4' in limits.supported_formats
        assert limits.requires_approval is False

    def test_youtube_limits(self):
        """Test YouTube platform limits."""
        limits = PLATFORM_LIMITS['youtube']

        assert limits.max_caption_length == 5000
        assert limits.max_hashtags == 15
        assert limits.max_video_size_mb == 256000
        assert 'mp4' in limits.supported_formats

    def test_twitter_limits(self):
        """Test Twitter platform limits."""
        limits = PLATFORM_LIMITS['twitter']

        assert limits.max_caption_length == 280
        assert limits.max_hashtags == 10
        assert limits.max_video_size_mb == 512

    def test_instagram_limits(self):
        """Test Instagram platform limits."""
        limits = PLATFORM_LIMITS['instagram']

        assert limits.max_caption_length == 2200
        assert limits.max_hashtags == 30
        assert limits.max_video_size_mb == 100

    def test_facebook_limits(self):
        """Test Facebook platform limits."""
        limits = PLATFORM_LIMITS['facebook']

        assert limits.max_caption_length == 63206
        assert limits.max_hashtags == 30
        assert limits.max_video_size_mb == 10240

    def test_linkedin_limits(self):
        """Test LinkedIn platform limits."""
        limits = PLATFORM_LIMITS['linkedin']

        assert limits.max_caption_length == 3000
        assert limits.max_hashtags == 30
        assert limits.max_video_size_mb == 5120


class TestPostContent:
    """Test PostContent model."""

    def test_post_content_creation(self):
        """Test creating PostContent."""
        content = PostContent(
            platform="tiktok",
            content_type="video",
            content_url="https://example.com/video.mp4",
            caption="Test caption",
            hashtags=["test", "video"]
        )

        assert content.platform == "tiktok"
        assert content.content_type == "video"
        assert content.content_url == "https://example.com/video.mp4"
        assert content.caption == "Test caption"
        assert len(content.hashtags) == 2

    def test_post_content_defaults(self):
        """Test default values in PostContent."""
        content = PostContent(
            platform="tiktok",
            content_type="video",
            caption="Test"
        )

        assert content.hashtags == []
        assert content.platform_settings == {}
        assert content.schedule_at is None
        assert content.source_id is None


class TestPostizPublisher:
    """Test Postiz publisher functionality."""

    def test_publisher_initialization(self, postiz_publisher, postiz_config):
        """Test publisher initialization."""
        assert postiz_publisher is not None
        assert postiz_publisher.config == postiz_config

    @pytest.mark.asyncio
    async def test_content_optimization_caption_truncation(self, postiz_publisher, test_post_content):
        """Test that long captions are truncated."""
        # Create content with very long caption
        long_caption = "A" * 3000
        test_post_content.caption = long_caption
        test_post_content.platform = "twitter"  # Twitter has 280 char limit

        optimized = await postiz_publisher._optimize_content(test_post_content)

        # Should be truncated to 280 chars (277 + "...")
        assert len(optimized.caption) <= 280
        assert optimized.caption.endswith("...")

    @pytest.mark.asyncio
    async def test_content_optimization_hashtag_limit(self, postiz_publisher, test_post_content):
        """Test that excess hashtags are removed."""
        # Add too many hashtags
        test_post_content.hashtags = [f"tag{i}" for i in range(50)]
        test_post_content.platform = "twitter"  # Twitter has 10 hashtag limit

        optimized = await postiz_publisher._optimize_content(test_post_content)

        # Should be limited to 10 hashtags
        assert len(optimized.hashtags) <= 10

    @pytest.mark.asyncio
    async def test_hashtag_formatting(self, postiz_publisher):
        """Test hashtag formatting."""
        hashtags = ["test", "#video", "content"]
        formatted = postiz_publisher._format_hashtags(hashtags)

        assert "#test" in formatted
        assert "#video" in formatted
        assert "#content" in formatted

    @pytest.mark.asyncio
    async def test_publish_with_mock(self, postiz_publisher, test_post_content):
        """Test publishing with mocked HTTP client."""
        # Mock the HTTP client
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "postId": "post-123",
            "postUrl": "https://tiktok.com/post/123",
            "status": "published"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        postiz_publisher.client = mock_client

        # Test publish
        result = await postiz_publisher.publish(test_post_content, "account-456")

        # Verify result
        assert result.success is True
        assert result.post_id == "post-123"
        assert result.post_url == "https://tiktok.com/post/123"
        assert result.platform == "tiktok"

        # Verify HTTP call
        assert mock_client.post.called
        call_kwargs = mock_client.post.call_args[1]
        assert "json" in call_kwargs

    @pytest.mark.asyncio
    async def test_schedule_with_mock(self, postiz_publisher, test_post_content):
        """Test scheduling with mocked HTTP client."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "postId": "scheduled-123",
            "postUrl": None,
            "status": "scheduled"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        postiz_publisher.client = mock_client

        # Test schedule
        schedule_time = datetime(2025, 12, 31, 12, 0, 0)
        result = await postiz_publisher.schedule(test_post_content, "account-456", schedule_time)

        # Verify result
        assert result.success is True
        assert result.post_id == "scheduled-123"
        assert "scheduled" in result.message.lower()

        # Verify HTTP call included schedule time
        assert mock_client.post.called

    @pytest.mark.asyncio
    async def test_get_post_status_with_mock(self, postiz_publisher):
        """Test getting post status with mocked HTTP client."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "postId": "post-123",
            "status": "published",
            "platform": "tiktok",
            "publishedAt": "2025-01-01T12:00:00Z"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.get.return_value = mock_response
        postiz_publisher.client = mock_client

        # Test get status
        status = await postiz_publisher.get_post_status("post-123")

        # Verify result
        assert status["status"] == "published"
        assert status["platform"] == "tiktok"

        # Verify HTTP call
        assert mock_client.get.called

    @pytest.mark.asyncio
    async def test_delete_post_with_mock(self, postiz_publisher):
        """Test deleting post with mocked HTTP client."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        mock_client.delete.return_value = mock_response
        postiz_publisher.client = mock_client

        # Test delete
        result = await postiz_publisher.delete_post("post-123")

        # Verify result
        assert result is True

        # Verify HTTP call
        assert mock_client.delete.called

    @pytest.mark.asyncio
    async def test_verify_account_with_mock(self, postiz_publisher):
        """Test verifying account with mocked HTTP client."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "active",
            "connected": True,
            "accountId": "account-123"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.get.return_value = mock_response
        postiz_publisher.client = mock_client

        # Test verify
        result = await postiz_publisher.verify_account("account-123")

        # Verify result
        assert result is True

        # Verify HTTP call
        assert mock_client.get.called

    @pytest.mark.asyncio
    async def test_multi_platform_publish(self, postiz_publisher, test_post_content):
        """Test publishing to multiple platforms."""
        mock_client = AsyncMock()

        # Mock successful response for all accounts
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "postId": "post-123",
            "postUrl": "https://example.com/post/123",
            "status": "published"
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        postiz_publisher.client = mock_client

        # Test multi-platform publish
        account_ids = ["account-1", "account-2", "account-3"]
        results = await postiz_publisher.publish_multi_platform(test_post_content, account_ids)

        # Verify results
        assert len(results) == 3
        for result in results:
            assert result.success is True
            assert result.post_id == "post-123"

        # Verify HTTP calls (one per account)
        assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_get_platform_limits(self, postiz_publisher):
        """Test getting platform limits."""
        limits = await postiz_publisher.get_platform_limits("tiktok")

        assert limits is not None
        assert limits.max_caption_length == 2200
        assert limits.max_hashtags == 30

    @pytest.mark.asyncio
    async def test_get_platform_limits_unknown(self, postiz_publisher):
        """Test getting limits for unknown platform."""
        limits = await postiz_publisher.get_platform_limits("unknown-platform")

        assert limits is None


class TestPublishResult:
    """Test PublishResult model."""

    def test_publish_result_success(self):
        """Test successful PublishResult."""
        result = PublishResult(
            success=True,
            post_id="post-123",
            post_url="https://example.com/post/123",
            platform="tiktok",
            message="Post published successfully"
        )

        assert result.success is True
        assert result.post_id == "post-123"
        assert result.post_url == "https://example.com/post/123"
        assert result.platform == "tiktok"
        assert result.error is None

    def test_publish_result_failure(self):
        """Test failed PublishResult."""
        result = PublishResult(
            success=False,
            platform="tiktok",
            error="Failed to publish: API error"
        )

        assert result.success is False
        assert result.post_id is None
        assert result.post_url is None
        assert result.error == "Failed to publish: API error"


class TestContentOptimization:
    """Test content optimization for different platforms."""

    @pytest.mark.asyncio
    async def test_twitter_caption_optimization(self, postiz_publisher):
        """Test Twitter caption optimization."""
        content = PostContent(
            platform="twitter",
            content_type="text",
            caption="A" * 300,  # Exceeds 280 limit
            hashtags=[f"tag{i}" for i in range(15)]  # Exceeds 10 limit
        )

        optimized = await postiz_publisher._optimize_content(content)

        assert len(optimized.caption) <= 280
        assert len(optimized.hashtags) <= 10

    @pytest.mark.asyncio
    async def test_tiktok_hashtag_formatting(self, postiz_publisher):
        """Test TikTok hashtag formatting."""
        content = PostContent(
            platform="tiktok",
            content_type="video",
            caption="Test caption",
            hashtags=["test", "video", "content"]
        )

        optimized = await postiz_publisher._optimize_content(content)

        # TikTok hashtags should start with #
        for tag in optimized.hashtags:
            assert tag.startswith("#")

    @pytest.mark.asyncio
    async def test_no_optimization_needed(self, postiz_publisher):
        """Test content that doesn't need optimization."""
        content = PostContent(
            platform="youtube",
            content_type="video",
            caption="Short caption",
            hashtags=["test"]
        )

        optimized = await postiz_publisher._optimize_content(content)

        # Should remain unchanged
        assert optimized.caption == "Short caption"
        assert len(optimized.hashtags) == 1
