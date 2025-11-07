"""
Tests for VEED.io talking avatar provider.

All tests use mocks - no real API calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.film.providers.veed import VEEDProvider, VEEDConfig, VideoGenerationResult


@pytest.fixture
def veed_config():
    """Create VEED config for testing."""
    return VEEDConfig(
        fal_api_key="test_fal_key",
        poll_interval=1,  # Shorter for tests
        max_wait_time=10
    )


@pytest.fixture
def veed_provider(veed_config):
    """Create VEED provider instance."""
    return VEEDProvider(veed_config)


class TestVEEDConfig:
    """Test VEED configuration."""

    def test_config_creation(self):
        """Test creating VEED config."""
        config = VEEDConfig(fal_api_key="test_key")
        assert config.fal_api_key == "test_key"
        assert config.base_url == "https://queue.fal.run"
        assert config.poll_interval == 10
        assert config.max_wait_time == 600

    def test_config_custom_values(self):
        """Test config with custom values."""
        config = VEEDConfig(
            fal_api_key="key",
            base_url="https://custom.url",
            poll_interval=5,
            max_wait_time=300
        )
        assert config.base_url == "https://custom.url"
        assert config.poll_interval == 5
        assert config.max_wait_time == 300


class TestVEEDProvider:
    """Test VEED provider."""

    def test_provider_initialization(self, veed_provider, veed_config):
        """Test provider initialization."""
        assert veed_provider.config == veed_config
        assert veed_provider.client is not None

    @pytest.mark.asyncio
    async def test_generate_talking_avatar_success(self, veed_provider):
        """Test successful talking avatar generation."""
        # Mock HTTP client
        mock_client = AsyncMock()

        # Mock generation request response
        mock_gen_response = MagicMock()
        mock_gen_response.json.return_value = {
            "request_id": "veed-123"
        }
        mock_gen_response.raise_for_status = MagicMock()

        # Mock status check response (completed)
        mock_status_response = MagicMock()
        mock_status_response.json.return_value = {
            "status": "COMPLETED",
            "video": {
                "url": "https://example.com/veed-video.mp4"
            }
        }
        mock_status_response.raise_for_status = MagicMock()

        # Setup mock client
        mock_client.post.return_value = mock_gen_response
        mock_client.get.return_value = mock_status_response

        veed_provider.client = mock_client

        # Test generation
        result = await veed_provider.generate_talking_avatar(
            image_url="https://example.com/photo.jpg",
            audio_url="https://example.com/audio.mp3",
            resolution="720p"
        )

        # Verify result
        assert isinstance(result, VideoGenerationResult)
        assert result.metadata["request_id"] == "veed-123"
        assert result.video_url == "https://example.com/veed-video.mp4"
        assert result.provider == "veed"
        assert result.cost == 0.10
        assert result.metadata["resolution"] == "720p"

        # Verify API calls
        mock_client.post.assert_called_once()
        mock_client.get.assert_called()

    @pytest.mark.asyncio
    async def test_generate_different_resolutions(self, veed_provider):
        """Test generation with different resolutions."""
        mock_client = AsyncMock()
        mock_gen_response = MagicMock()
        mock_gen_response.json.return_value = {"request_id": "test-id"}
        mock_gen_response.raise_for_status = MagicMock()

        mock_status_response = MagicMock()
        mock_status_response.json.return_value = {
            "status": "COMPLETED",
            "video": {"url": "https://example.com/video.mp4"}
        }
        mock_status_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_gen_response
        mock_client.get.return_value = mock_status_response
        veed_provider.client = mock_client

        # Test different resolutions
        for resolution in ["480p", "720p", "1080p"]:
            result = await veed_provider.generate_talking_avatar(
                image_url="https://example.com/photo.jpg",
                audio_url="https://example.com/audio.mp3",
                resolution=resolution
            )
            assert result.metadata["resolution"] == resolution

    @pytest.mark.asyncio
    async def test_poll_status_pending_then_complete(self, veed_provider):
        """Test polling that goes from pending to complete."""
        mock_client = AsyncMock()

        # First call: pending
        pending_response = MagicMock()
        pending_response.json.return_value = {"status": "PENDING"}
        pending_response.raise_for_status = MagicMock()

        # Second call: in_progress
        progress_response = MagicMock()
        progress_response.json.return_value = {"status": "IN_PROGRESS"}
        progress_response.raise_for_status = MagicMock()

        # Third call: completed
        complete_response = MagicMock()
        complete_response.json.return_value = {
            "status": "COMPLETED",
            "video": {"url": "https://example.com/final.mp4"}
        }
        complete_response.raise_for_status = MagicMock()

        mock_client.get.side_effect = [
            pending_response,
            progress_response,
            complete_response
        ]

        veed_provider.client = mock_client

        # Test polling
        video_url = await veed_provider._poll_status("test-request-id")

        assert video_url == "https://example.com/final.mp4"
        assert mock_client.get.call_count == 3

    @pytest.mark.asyncio
    async def test_poll_status_failed(self, veed_provider):
        """Test polling when generation fails."""
        mock_client = AsyncMock()

        failed_response = MagicMock()
        failed_response.json.return_value = {
            "status": "FAILED",
            "error": "Invalid image format"
        }
        failed_response.raise_for_status = MagicMock()

        mock_client.get.return_value = failed_response
        veed_provider.client = mock_client

        # Test polling fails
        with pytest.raises(Exception) as exc_info:
            await veed_provider._poll_status("test-request-id")

        assert "VEED generation failed" in str(exc_info.value)
        assert "Invalid image format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_poll_status_timeout(self, veed_provider):
        """Test polling timeout."""
        # Set very short timeout for test
        veed_provider.config.max_wait_time = 0.1

        mock_client = AsyncMock()

        # Always return pending (will timeout)
        pending_response = MagicMock()
        pending_response.json.return_value = {"status": "PENDING"}
        pending_response.raise_for_status = MagicMock()

        mock_client.get.return_value = pending_response
        veed_provider.client = mock_client

        # Test timeout
        with pytest.raises(TimeoutError) as exc_info:
            await veed_provider._poll_status("test-request-id")

        assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_method_routes_to_talking_avatar(self, veed_provider):
        """Test that generate() routes to generate_talking_avatar()."""
        mock_client = AsyncMock()

        mock_gen_response = MagicMock()
        mock_gen_response.json.return_value = {"request_id": "test-123"}
        mock_gen_response.raise_for_status = MagicMock()

        mock_status_response = MagicMock()
        mock_status_response.json.return_value = {
            "status": "COMPLETED",
            "video": {"url": "https://example.com/video.mp4"}
        }
        mock_status_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_gen_response
        mock_client.get.return_value = mock_status_response
        veed_provider.client = mock_client

        # Call generate (should route to generate_talking_avatar)
        result = await veed_provider.generate(
            image_url="https://example.com/photo.jpg",
            audio_url="https://example.com/audio.mp3"
        )

        assert isinstance(result, VideoGenerationResult)
        assert result.provider == "veed"

    @pytest.mark.asyncio
    async def test_close_client(self, veed_provider):
        """Test closing HTTP client."""
        mock_client = AsyncMock()
        veed_provider.client = mock_client

        await veed_provider.close()

        mock_client.aclose.assert_called_once()


class TestVEEDProviderEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_no_request_id_in_response(self, veed_provider):
        """Test handling response without request_id."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {}  # No request_id
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        veed_provider.client = mock_client

        with pytest.raises(Exception) as exc_info:
            await veed_provider.generate_talking_avatar(
                image_url="https://example.com/photo.jpg",
                audio_url="https://example.com/audio.mp3"
            )

        assert "No request_id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_no_video_url_in_completed_response(self, veed_provider):
        """Test handling completed response without video URL."""
        mock_client = AsyncMock()

        mock_gen_response = MagicMock()
        mock_gen_response.json.return_value = {"request_id": "test-123"}
        mock_gen_response.raise_for_status = MagicMock()

        mock_status_response = MagicMock()
        mock_status_response.json.return_value = {
            "status": "COMPLETED",
            "video": {}  # No url
        }
        mock_status_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_gen_response
        mock_client.get.return_value = mock_status_response
        veed_provider.client = mock_client

        with pytest.raises(Exception) as exc_info:
            await veed_provider.generate_talking_avatar(
                image_url="https://example.com/photo.jpg",
                audio_url="https://example.com/audio.mp3"
            )

        assert "No video URL" in str(exc_info.value)
