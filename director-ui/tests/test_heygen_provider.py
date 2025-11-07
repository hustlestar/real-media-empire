"""
Mock tests for HeyGen provider.

Tests the HeyGen avatar video generation provider with mocked HTTP calls.
No real API calls are made.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from film.providers.heygen import (
    HeyGenProvider,
    HeyGenConfig,
    HeyGenBackgroundConfig,
    HeyGenDimensionConfig,
    HeyGenVoiceConfig,
    VideoGenerationResult
)


@pytest.fixture
def heygen_config():
    """Create a test HeyGen configuration."""
    return HeyGenConfig(
        api_key="test-api-key",
        base_url="https://api.heygen.com",
        max_retries=1,
        poll_interval=1,
        max_wait_time=10
    )


@pytest.fixture
def heygen_provider(heygen_config):
    """Create a HeyGen provider with test configuration."""
    return HeyGenProvider(heygen_config)


@pytest.fixture
def mock_http_client():
    """Create a mock httpx AsyncClient."""
    mock_client = AsyncMock()
    return mock_client


class TestHeyGenConfig:
    """Test HeyGen configuration."""

    def test_config_creation(self):
        """Test creating a HeyGen configuration."""
        config = HeyGenConfig(
            api_key="test-key",
            base_url="https://test.com",
            max_retries=3,
            poll_interval=5,
            max_wait_time=300
        )

        assert config.api_key == "test-key"
        assert config.base_url == "https://test.com"
        assert config.max_retries == 3
        assert config.poll_interval == 5
        assert config.max_wait_time == 300

    def test_config_defaults(self):
        """Test default configuration values."""
        config = HeyGenConfig(api_key="test-key")

        assert config.base_url == "https://api.heygen.com"
        assert config.max_retries == 3
        assert config.poll_interval == 10
        assert config.max_wait_time == 300


class TestHeyGenDimensionConfig:
    """Test HeyGen dimension configurations."""

    def test_vertical_aspect_ratio(self):
        """Test 9:16 vertical aspect ratio."""
        config = HeyGenDimensionConfig.from_aspect_ratio("9:16")

        assert config.width == 720
        assert config.height == 1280

    def test_landscape_aspect_ratio(self):
        """Test 16:9 landscape aspect ratio."""
        config = HeyGenDimensionConfig.from_aspect_ratio("16:9")

        assert config.width == 1280
        assert config.height == 720

    def test_square_aspect_ratio(self):
        """Test 1:1 square aspect ratio."""
        config = HeyGenDimensionConfig.from_aspect_ratio("1:1")

        assert config.width == 1080
        assert config.height == 1080

    def test_portrait_aspect_ratio(self):
        """Test 4:5 portrait aspect ratio."""
        config = HeyGenDimensionConfig.from_aspect_ratio("4:5")

        assert config.width == 1080
        assert config.height == 1350

    def test_all_aspect_ratios(self):
        """Test all supported aspect ratios."""
        ratios = ["9:16", "16:9", "1:1", "4:5"]

        for ratio in ratios:
            config = HeyGenDimensionConfig.from_aspect_ratio(ratio)
            assert config is not None
            assert config.width > 0
            assert config.height > 0


class TestHeyGenBackgroundConfig:
    """Test HeyGen background configurations."""

    def test_color_background(self):
        """Test color background configuration."""
        config = HeyGenBackgroundConfig(
            type="color",
            value="#FF0000"
        )

        assert config.type == "color"
        assert config.value == "#FF0000"

    def test_image_background(self):
        """Test image background configuration."""
        config = HeyGenBackgroundConfig(
            type="image",
            value="https://example.com/bg.jpg"
        )

        assert config.type == "image"
        assert config.value == "https://example.com/bg.jpg"

    def test_video_background(self):
        """Test video background configuration."""
        config = HeyGenBackgroundConfig(
            type="video",
            value="https://example.com/bg.mp4"
        )

        assert config.type == "video"
        assert config.value == "https://example.com/bg.mp4"


class TestHeyGenVoiceConfig:
    """Test HeyGen voice configurations."""

    def test_voice_config_defaults(self):
        """Test default voice configuration."""
        config = HeyGenVoiceConfig(
            voice_id="test-voice-id"
        )

        assert config.voice_id == "test-voice-id"
        assert config.speed == 1.1
        assert config.pitch == 50
        assert config.emotion == "Excited"

    def test_voice_config_custom(self):
        """Test custom voice configuration."""
        config = HeyGenVoiceConfig(
            voice_id="test-voice-id",
            speed=1.5,
            pitch=75,
            emotion="Calm"
        )

        assert config.voice_id == "test-voice-id"
        assert config.speed == 1.5
        assert config.pitch == 75
        assert config.emotion == "Calm"


class TestHeyGenProvider:
    """Test HeyGen provider functionality."""

    def test_provider_initialization(self, heygen_provider, heygen_config):
        """Test provider initialization."""
        assert heygen_provider is not None
        assert heygen_provider.config == heygen_config

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, heygen_provider):
        """Test video generation with mocked HTTP client."""
        # Mock the HTTP client
        mock_client = AsyncMock()

        # Mock generate response
        mock_generate_response = MagicMock()
        mock_generate_response.json.return_value = {
            "code": 100,
            "data": {
                "video_id": "test-video-id-123"
            }
        }

        # Mock status polling responses (pending -> completed)
        mock_status_pending = MagicMock()
        mock_status_pending.json.return_value = {
            "code": 100,
            "data": {
                "status": "pending",
                "video_id": "test-video-id-123"
            }
        }

        mock_status_completed = MagicMock()
        mock_status_completed.json.return_value = {
            "code": 100,
            "data": {
                "status": "completed",
                "video_id": "test-video-id-123",
                "video_url": "https://example.com/video.mp4",
                "duration": 30.5
            }
        }

        # Setup mock responses
        mock_client.post.return_value = mock_generate_response
        mock_client.get.side_effect = [mock_status_pending, mock_status_completed]

        # Replace the provider's client
        heygen_provider.client = mock_client

        # Test generate
        result = await heygen_provider.generate(
            script="Test script for video generation",
            avatar_id="avatar-123",
            voice_id="voice-456"
        )

        # Verify result
        assert result is not None
        assert isinstance(result, VideoGenerationResult)
        assert result.video_id == "test-video-id-123"
        assert result.video_url == "https://example.com/video.mp4"
        assert result.status == "completed"
        assert result.duration == 30.5

        # Verify HTTP calls
        assert mock_client.post.called
        assert mock_client.get.call_count == 2  # Two status checks

    @pytest.mark.asyncio
    async def test_list_avatars_mock(self, heygen_provider):
        """Test listing avatars with mocked response."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 100,
            "data": {
                "avatars": [
                    {
                        "avatar_id": "avatar-1",
                        "avatar_name": "John Doe",
                        "preview_image_url": "https://example.com/avatar1.jpg",
                        "gender": "male"
                    },
                    {
                        "avatar_id": "avatar-2",
                        "avatar_name": "Jane Smith",
                        "preview_image_url": "https://example.com/avatar2.jpg",
                        "gender": "female"
                    }
                ]
            }
        }

        mock_client.get.return_value = mock_response
        heygen_provider.client = mock_client

        # Test list avatars
        avatars = await heygen_provider.list_avatars()

        # Verify results
        assert len(avatars) == 2
        assert avatars[0]["avatar_id"] == "avatar-1"
        assert avatars[0]["avatar_name"] == "John Doe"
        assert avatars[1]["avatar_id"] == "avatar-2"
        assert avatars[1]["avatar_name"] == "Jane Smith"

        # Verify HTTP call
        assert mock_client.get.called

    @pytest.mark.asyncio
    async def test_list_voices_mock(self, heygen_provider):
        """Test listing voices with mocked response."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 100,
            "data": {
                "voices": [
                    {
                        "voice_id": "voice-1",
                        "name": "English Male",
                        "language": "English",
                        "gender": "male"
                    },
                    {
                        "voice_id": "voice-2",
                        "name": "Spanish Female",
                        "language": "Spanish",
                        "gender": "female"
                    }
                ]
            }
        }

        mock_client.get.return_value = mock_response
        heygen_provider.client = mock_client

        # Test list voices
        voices = await heygen_provider.list_voices()

        # Verify results
        assert len(voices) == 2
        assert voices[0]["voice_id"] == "voice-1"
        assert voices[0]["name"] == "English Male"
        assert voices[1]["voice_id"] == "voice-2"
        assert voices[1]["language"] == "Spanish"

        # Verify HTTP call
        assert mock_client.get.called

    @pytest.mark.asyncio
    async def test_generate_with_all_options(self, heygen_provider):
        """Test video generation with all configuration options."""
        mock_client = AsyncMock()

        mock_generate_response = MagicMock()
        mock_generate_response.json.return_value = {
            "code": 100,
            "data": {"video_id": "test-video-id"}
        }

        mock_status_completed = MagicMock()
        mock_status_completed.json.return_value = {
            "code": 100,
            "data": {
                "status": "completed",
                "video_id": "test-video-id",
                "video_url": "https://example.com/video.mp4",
                "duration": 45.0
            }
        }

        mock_client.post.return_value = mock_generate_response
        mock_client.get.return_value = mock_status_completed
        heygen_provider.client = mock_client

        # Test with all options
        result = await heygen_provider.generate(
            script="Full test script",
            avatar_id="avatar-123",
            voice_id="voice-456",
            background=HeyGenBackgroundConfig(type="color", value="#00FF00"),
            dimension=HeyGenDimensionConfig.from_aspect_ratio("16:9"),
            voice_config=HeyGenVoiceConfig(voice_id="voice-456", speed=1.2, pitch=60, emotion="Calm"),
            title="Test Video",
            test=True,
            caption=True
        )

        # Verify result
        assert result.video_id == "test-video-id"
        assert result.video_url == "https://example.com/video.mp4"

        # Verify request was made with all parameters
        assert mock_client.post.called
        call_kwargs = mock_client.post.call_args[1]
        assert "json" in call_kwargs
        request_data = call_kwargs["json"]

        # Verify video inputs structure
        assert "video_inputs" in request_data
        assert len(request_data["video_inputs"]) > 0


class TestVideoGenerationResult:
    """Test VideoGenerationResult model."""

    def test_result_creation(self):
        """Test creating a VideoGenerationResult."""
        result = VideoGenerationResult(
            video_id="test-id",
            video_url="https://example.com/video.mp4",
            status="completed",
            duration=60.0,
            cost=1.50,
            metadata={"test": "data"}
        )

        assert result.video_id == "test-id"
        assert result.video_url == "https://example.com/video.mp4"
        assert result.status == "completed"
        assert result.duration == 60.0
        assert result.cost == 1.50
        assert result.metadata == {"test": "data"}

    def test_result_defaults(self):
        """Test default values in VideoGenerationResult."""
        result = VideoGenerationResult(
            video_id="test-id",
            status="pending"
        )

        assert result.video_id == "test-id"
        assert result.video_url is None
        assert result.status == "pending"
        assert result.duration == 0.0
        assert result.cost == 0.0
        assert result.metadata == {}
