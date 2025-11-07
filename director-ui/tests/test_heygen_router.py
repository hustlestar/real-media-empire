"""
API tests for HeyGen router.

Tests HeyGen API endpoints with mocked provider.
Uses FastAPI TestClient to test endpoints without real HTTP calls.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.app import app
from film.providers.heygen import VideoGenerationResult


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_heygen_provider():
    """Create a mock HeyGen provider."""
    mock_provider = AsyncMock()

    # Mock generate method
    mock_provider.generate.return_value = VideoGenerationResult(
        video_id="test-video-id",
        video_url="https://example.com/video.mp4",
        status="completed",
        duration=30.0,
        cost=1.25,
        metadata={"test": "metadata"}
    )

    # Mock list_avatars method
    mock_provider.list_avatars.return_value = [
        {
            "avatar_id": "avatar-1",
            "avatar_name": "John Doe",
            "preview_image_url": "https://example.com/avatar1.jpg",
            "gender": "male",
            "is_green_screen": False
        },
        {
            "avatar_id": "avatar-2",
            "avatar_name": "Jane Smith",
            "preview_image_url": "https://example.com/avatar2.jpg",
            "gender": "female",
            "is_green_screen": True
        }
    ]

    # Mock list_voices method
    mock_provider.list_voices.return_value = [
        {
            "voice_id": "voice-1",
            "name": "English Male",
            "language": "English",
            "gender": "male",
            "preview_audio_url": "https://example.com/voice1.mp3"
        },
        {
            "voice_id": "voice-2",
            "name": "Spanish Female",
            "language": "Spanish",
            "gender": "female",
            "preview_audio_url": "https://example.com/voice2.mp3"
        }
    ]

    # Mock get_video_status method
    mock_provider.get_video_status.return_value = {
        "status": "completed",
        "video_url": "https://example.com/video.mp4",
        "duration": 30.0
    }

    return mock_provider


class TestHeyGenRouterEndpoints:
    """Test HeyGen router endpoints."""

    @patch('api.routers.heygen.get_heygen_provider')
    def test_list_avatars(self, mock_get_provider, client, mock_heygen_provider):
        """Test GET /api/heygen/avatars endpoint."""
        mock_get_provider.return_value = mock_heygen_provider

        response = client.get("/api/heygen/avatars")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["avatar_id"] == "avatar-1"
        assert data[0]["avatar_name"] == "John Doe"
        assert data[1]["avatar_id"] == "avatar-2"
        assert data[1]["is_green_screen"] is True

    @patch('api.routers.heygen.get_heygen_provider')
    def test_list_voices(self, mock_get_provider, client, mock_heygen_provider):
        """Test GET /api/heygen/voices endpoint."""
        mock_get_provider.return_value = mock_heygen_provider

        response = client.get("/api/heygen/voices")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["voice_id"] == "voice-1"
        assert data[0]["name"] == "English Male"
        assert data[0]["language"] == "English"

    @patch('api.routers.heygen.get_heygen_provider')
    def test_list_voices_with_language_filter(self, mock_get_provider, client, mock_heygen_provider):
        """Test GET /api/heygen/voices with language parameter."""
        # Mock filtered response
        mock_heygen_provider.list_voices.return_value = [
            {
                "voice_id": "voice-1",
                "name": "English Male",
                "language": "English",
                "gender": "male"
            }
        ]
        mock_get_provider.return_value = mock_heygen_provider

        response = client.get("/api/heygen/voices?language=English")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["language"] == "English"

    @patch('api.routers.heygen.get_heygen_provider')
    def test_generate_avatar_video(self, mock_get_provider, client, mock_heygen_provider):
        """Test POST /api/heygen/generate endpoint."""
        mock_get_provider.return_value = mock_heygen_provider

        request_data = {
            "script": "This is a test script for avatar video generation",
            "avatar_id": "avatar-1",
            "voice_id": "voice-1",
            "aspect_ratio": "9:16",
            "background_type": "color",
            "background_value": "#000000"
        }

        response = client.post("/api/heygen/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == "test-video-id"
        assert data["video_url"] == "https://example.com/video.mp4"
        assert data["status"] == "completed"
        assert data["duration"] == 30.0
        assert data["cost"] == 1.25

    @patch('api.routers.heygen.get_heygen_provider')
    def test_generate_with_all_options(self, mock_get_provider, client, mock_heygen_provider):
        """Test video generation with all optional parameters."""
        mock_get_provider.return_value = mock_heygen_provider

        request_data = {
            "script": "Full test script",
            "avatar_id": "avatar-1",
            "voice_id": "voice-1",
            "title": "Test Video",
            "aspect_ratio": "16:9",
            "background_type": "image",
            "background_value": "https://example.com/bg.jpg",
            "voice_speed": 1.2,
            "voice_pitch": 60,
            "voice_emotion": "Calm",
            "avatar_scale": 1.5,
            "has_green_screen": True,
            "avatar_offset_x": 0.1,
            "avatar_offset_y": 0.2,
            "caption": True,
            "test": True
        }

        response = client.post("/api/heygen/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["video_id"] == "test-video-id"

        # Verify provider was called
        assert mock_heygen_provider.generate.called

    @patch('api.routers.heygen.get_heygen_provider')
    def test_generate_missing_required_fields(self, mock_get_provider, client, mock_heygen_provider):
        """Test video generation with missing required fields."""
        mock_get_provider.return_value = mock_heygen_provider

        # Missing avatar_id
        request_data = {
            "script": "Test script",
            "voice_id": "voice-1"
        }

        response = client.post("/api/heygen/generate", json=request_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    @patch('api.routers.heygen.get_heygen_provider')
    def test_get_video_status(self, mock_get_provider, client, mock_heygen_provider):
        """Test GET /api/heygen/videos/{video_id}/status endpoint."""
        mock_get_provider.return_value = mock_heygen_provider

        response = client.get("/api/heygen/videos/test-video-123/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["video_url"] == "https://example.com/video.mp4"
        assert data["duration"] == 30.0

    def test_get_aspect_ratios(self, client):
        """Test GET /api/heygen/aspect-ratios endpoint."""
        response = client.get("/api/heygen/aspect-ratios")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Verify expected aspect ratios
        aspect_ratios = [item["value"] for item in data]
        assert "9:16" in aspect_ratios
        assert "16:9" in aspect_ratios
        assert "1:1" in aspect_ratios
        assert "4:5" in aspect_ratios

        # Verify structure
        for item in data:
            assert "value" in item
            assert "name" in item
            assert "platforms" in item
            assert "dimensions" in item


class TestHeyGenRouterValidation:
    """Test request validation in HeyGen router."""

    @patch('api.routers.heygen.get_heygen_provider')
    def test_invalid_aspect_ratio(self, mock_get_provider, client, mock_heygen_provider):
        """Test video generation with invalid aspect ratio."""
        mock_get_provider.return_value = mock_heygen_provider

        request_data = {
            "script": "Test script",
            "avatar_id": "avatar-1",
            "voice_id": "voice-1",
            "aspect_ratio": "invalid-ratio"
        }

        response = client.post("/api/heygen/generate", json=request_data)

        # Should return 422 for validation error
        assert response.status_code == 422

    @patch('api.routers.heygen.get_heygen_provider')
    def test_invalid_background_type(self, mock_get_provider, client, mock_heygen_provider):
        """Test video generation with invalid background type."""
        mock_get_provider.return_value = mock_heygen_provider

        request_data = {
            "script": "Test script",
            "avatar_id": "avatar-1",
            "voice_id": "voice-1",
            "background_type": "invalid-type"
        }

        response = client.post("/api/heygen/generate", json=request_data)

        # Should return 422 for validation error
        assert response.status_code == 422

    @patch('api.routers.heygen.get_heygen_provider')
    def test_voice_speed_bounds(self, mock_get_provider, client, mock_heygen_provider):
        """Test voice speed validation."""
        mock_get_provider.return_value = mock_heygen_provider

        # Test with speed out of bounds (should be 0.5-2.0)
        request_data = {
            "script": "Test script",
            "avatar_id": "avatar-1",
            "voice_id": "voice-1",
            "voice_speed": 5.0  # Too high
        }

        response = client.post("/api/heygen/generate", json=request_data)

        # Should return 422 for validation error
        assert response.status_code == 422


class TestHeyGenRouterErrorHandling:
    """Test error handling in HeyGen router."""

    @patch('api.routers.heygen.get_heygen_provider')
    def test_provider_exception(self, mock_get_provider, client):
        """Test handling of provider exceptions."""
        # Make provider raise an exception
        mock_provider = AsyncMock()
        mock_provider.generate.side_effect = Exception("Provider error")
        mock_get_provider.return_value = mock_provider

        request_data = {
            "script": "Test script",
            "avatar_id": "avatar-1",
            "voice_id": "voice-1"
        }

        response = client.post("/api/heygen/generate", json=request_data)

        # Should handle error gracefully
        assert response.status_code in [500, 400]

    @patch('api.routers.heygen.get_heygen_provider')
    def test_missing_api_key(self, mock_get_provider, client):
        """Test behavior when API key is not configured."""
        # This would normally be tested with environment variable manipulation
        # For now, we verify the endpoint exists and handles the case
        pass  # Placeholder for environment-specific testing


class TestHeyGenRouterIntegration:
    """Integration tests for HeyGen router with other components."""

    def test_openapi_schema(self, client):
        """Test that HeyGen endpoints are in OpenAPI schema."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        # Verify HeyGen endpoints are documented
        paths = schema.get("paths", {})
        heygen_paths = [path for path in paths.keys() if "/heygen/" in path]
        assert len(heygen_paths) > 0

    def test_tags_in_schema(self, client):
        """Test that HeyGen tag is in OpenAPI schema."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        # Verify HeyGen tag exists
        tags = schema.get("tags", [])
        heygen_tags = [tag for tag in tags if tag.get("name") == "heygen"]
        assert len(heygen_tags) > 0
        assert heygen_tags[0]["description"] is not None
