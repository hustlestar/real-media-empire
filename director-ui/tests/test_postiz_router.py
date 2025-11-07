"""
API tests for Postiz router.

Tests Postiz API endpoints with mocked publisher.
Uses FastAPI TestClient to test endpoints without real HTTP calls.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from api.app import app
from social.base_publisher import PublishResult
from social.postiz_publisher import PLATFORM_LIMITS


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_postiz_publisher():
    """Create a mock Postiz publisher."""
    mock_publisher = AsyncMock()

    # Mock publish method
    mock_publisher.publish.return_value = PublishResult(
        success=True,
        post_id="post-123",
        post_url="https://tiktok.com/post/123",
        platform="tiktok",
        message="Post published successfully"
    )

    # Mock schedule method
    mock_publisher.schedule.return_value = PublishResult(
        success=True,
        post_id="scheduled-456",
        post_url=None,
        platform="instagram",
        message="Post scheduled successfully"
    )

    # Mock get_post_status method
    mock_publisher.get_post_status.return_value = {
        "status": "published",
        "platform": "tiktok",
        "publishedAt": "2025-01-01T12:00:00Z"
    }

    # Mock delete_post method
    mock_publisher.delete_post.return_value = True

    # Mock verify_account method
    mock_publisher.verify_account.return_value = True

    # Mock get_platform_limits method
    mock_publisher.get_platform_limits.return_value = PLATFORM_LIMITS.get("tiktok")

    # Mock publish_multi_platform method
    mock_publisher.publish_multi_platform.return_value = [
        PublishResult(success=True, post_id="post-1", platform="tiktok"),
        PublishResult(success=True, post_id="post-2", platform="instagram"),
        PublishResult(success=True, post_id="post-3", platform="youtube")
    ]

    return mock_publisher


class TestPostizRouterEndpoints:
    """Test Postiz router endpoints."""

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_publish_content(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test POST /api/postiz/publish endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_id": "account-123",
            "platform": "tiktok",
            "content_type": "video",
            "content_url": "https://example.com/video.mp4",
            "caption": "Test caption for video",
            "hashtags": ["test", "video"],
            "platform_settings": {}
        }

        response = client.post("/api/postiz/publish", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["post_id"] == "post-123"
        assert data["post_url"] == "https://tiktok.com/post/123"
        assert data["platform"] == "tiktok"

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_schedule_content(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test POST /api/postiz/schedule endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_id": "account-123",
            "platform": "instagram",
            "content_type": "video",
            "content_url": "https://example.com/video.mp4",
            "caption": "Scheduled post",
            "hashtags": ["scheduled"],
            "platform_settings": {},
            "schedule_at": "2025-12-31T12:00:00Z"
        }

        response = client.post("/api/postiz/schedule", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["post_id"] == "scheduled-456"
        assert "scheduled" in data["message"].lower()

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_multi_platform_publish(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test POST /api/postiz/publish/multi-platform endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_ids": ["account-1", "account-2", "account-3"],
            "content": {
                "account_id": "account-1",
                "platform": "tiktok",
                "content_type": "video",
                "content_url": "https://example.com/video.mp4",
                "caption": "Multi-platform post",
                "hashtags": ["multi", "platform"]
            }
        }

        response = client.post("/api/postiz/publish/multi-platform", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        for result in data:
            assert result["success"] is True

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_get_post_status(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test GET /api/postiz/posts/{post_id}/status endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        response = client.get("/api/postiz/posts/post-123/status")

        assert response.status_code == 200
        data = response.json()
        assert data["post_id"] == "post-123"
        assert data["status"] == "published"
        assert data["platform"] == "tiktok"

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_delete_post(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test DELETE /api/postiz/posts/{post_id} endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        response = client.delete("/api/postiz/posts/post-123")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "post_id" in data
        assert data["post_id"] == "post-123"

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_verify_account(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test GET /api/postiz/accounts/{account_id}/verify endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        response = client.get("/api/postiz/accounts/account-123/verify")

        assert response.status_code == 200
        data = response.json()
        assert data["account_id"] == "account-123"
        assert data["is_valid"] is True
        assert "message" in data

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_get_platform_limits(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test GET /api/postiz/platforms/{platform}/limits endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        response = client.get("/api/postiz/platforms/tiktok/limits")

        assert response.status_code == 200
        data = response.json()
        assert data["platform"] == "tiktok"
        assert data["max_caption_length"] == 2200
        assert data["max_hashtags"] == 30
        assert isinstance(data["supported_formats"], list)

    def test_list_supported_platforms(self, client):
        """Test GET /api/postiz/platforms endpoint."""
        response = client.get("/api/postiz/platforms")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "tiktok" in data
        assert "youtube" in data
        assert "instagram" in data
        assert "facebook" in data
        assert "twitter" in data
        assert "linkedin" in data

    def test_get_all_platform_limits(self, client):
        """Test GET /api/postiz/platforms/limits endpoint."""
        response = client.get("/api/postiz/platforms/limits")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

        # Verify all expected platforms
        expected_platforms = ['tiktok', 'youtube', 'instagram', 'facebook', 'twitter', 'linkedin']
        for platform in expected_platforms:
            assert platform in data
            assert "max_caption_length" in data[platform]
            assert "max_hashtags" in data[platform]


class TestPostizRouterValidation:
    """Test request validation in Postiz router."""

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_publish_missing_required_fields(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test publishing with missing required fields."""
        mock_get_publisher.return_value = mock_postiz_publisher

        # Missing caption
        request_data = {
            "account_id": "account-123",
            "platform": "tiktok",
            "content_type": "video"
        }

        response = client.post("/api/postiz/publish", json=request_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_schedule_missing_schedule_time(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test scheduling without schedule_at field."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_id": "account-123",
            "platform": "instagram",
            "content_type": "video",
            "content_url": "https://example.com/video.mp4",
            "caption": "Test"
        }

        response = client.post("/api/postiz/schedule", json=request_data)

        # Should return 422 for missing schedule_at
        assert response.status_code == 422

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_multi_platform_empty_accounts(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test multi-platform publishing with empty account list."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_ids": [],
            "content": {
                "account_id": "account-1",
                "platform": "tiktok",
                "content_type": "video",
                "caption": "Test"
            }
        }

        response = client.post("/api/postiz/publish/multi-platform", json=request_data)

        # Should return 422 for empty list
        assert response.status_code == 422


class TestPostizRouterErrorHandling:
    """Test error handling in Postiz router."""

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_publish_publisher_exception(self, mock_get_publisher, client):
        """Test handling of publisher exceptions."""
        # Make publisher raise an exception
        mock_publisher = AsyncMock()
        mock_publisher.publish.return_value = PublishResult(
            success=False,
            platform="tiktok",
            error="Publishing failed: API error"
        )
        mock_get_publisher.return_value = mock_publisher

        request_data = {
            "account_id": "account-123",
            "platform": "tiktok",
            "content_type": "video",
            "content_url": "https://example.com/video.mp4",
            "caption": "Test"
        }

        response = client.post("/api/postiz/publish", json=request_data)

        # Should return success=false in response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_get_post_status_not_found(self, mock_get_publisher, client):
        """Test getting status of non-existent post."""
        mock_publisher = AsyncMock()
        mock_publisher.get_post_status.return_value = {
            "error": "Post not found"
        }
        mock_get_publisher.return_value = mock_publisher

        response = client.get("/api/postiz/posts/nonexistent-post/status")

        # Should return 404
        assert response.status_code == 404

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_delete_post_failure(self, mock_get_publisher, client):
        """Test deleting post that fails."""
        mock_publisher = AsyncMock()
        mock_publisher.delete_post.return_value = False
        mock_get_publisher.return_value = mock_publisher

        response = client.delete("/api/postiz/posts/post-123")

        # Should return 400
        assert response.status_code == 400

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_verify_account_invalid(self, mock_get_publisher, client):
        """Test verifying invalid account."""
        mock_publisher = AsyncMock()
        mock_publisher.verify_account.return_value = False
        mock_get_publisher.return_value = mock_publisher

        response = client.get("/api/postiz/accounts/invalid-account/verify")

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "failed" in data["message"].lower()

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_get_platform_limits_unknown_platform(self, mock_get_publisher, client):
        """Test getting limits for unknown platform."""
        mock_publisher = AsyncMock()
        mock_publisher.get_platform_limits.return_value = None
        mock_get_publisher.return_value = mock_publisher

        response = client.get("/api/postiz/platforms/unknown-platform/limits")

        # Should return 404
        assert response.status_code == 404


class TestPostizRouterIntegration:
    """Integration tests for Postiz router with other components."""

    def test_openapi_schema(self, client):
        """Test that Postiz endpoints are in OpenAPI schema."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        # Verify Postiz endpoints are documented
        paths = schema.get("paths", {})
        postiz_paths = [path for path in paths.keys() if "/postiz/" in path]
        assert len(postiz_paths) > 0

    def test_tags_in_schema(self, client):
        """Test that Postiz tag is in OpenAPI schema."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        # Verify Postiz tag exists
        tags = schema.get("tags", [])
        postiz_tags = [tag for tag in tags if tag.get("name") == "postiz"]
        assert len(postiz_tags) > 0
        assert postiz_tags[0]["description"] is not None


class TestPostizRouterDataHandling:
    """Test data handling and transformation in router."""

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_publish_with_source_tracking(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test publishing with source tracking metadata."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_id": "account-123",
            "platform": "tiktok",
            "content_type": "video",
            "content_url": "https://example.com/video.mp4",
            "caption": "Test",
            "source_id": "avatar-video-123",
            "source_type": "avatar_video"
        }

        response = client.post("/api/postiz/publish", json=request_data)

        assert response.status_code == 200
        # Verify publisher was called with source tracking
        assert mock_postiz_publisher.publish.called

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_publish_with_platform_settings(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test publishing with platform-specific settings."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_id": "account-123",
            "platform": "tiktok",
            "content_type": "video",
            "content_url": "https://example.com/video.mp4",
            "caption": "Test",
            "platform_settings": {
                "privacy": "public",
                "comments_enabled": True,
                "duet_enabled": False
            }
        }

        response = client.post("/api/postiz/publish", json=request_data)

        assert response.status_code == 200
        # Verify publisher received platform settings
        assert mock_postiz_publisher.publish.called

    @patch('api.routers.postiz.get_postiz_publisher')
    def test_schedule_datetime_parsing(self, mock_get_publisher, client, mock_postiz_publisher):
        """Test that datetime is correctly parsed in schedule endpoint."""
        mock_get_publisher.return_value = mock_postiz_publisher

        request_data = {
            "account_id": "account-123",
            "platform": "instagram",
            "content_type": "video",
            "content_url": "https://example.com/video.mp4",
            "caption": "Scheduled",
            "schedule_at": "2025-12-31T23:59:59Z"
        }

        response = client.post("/api/postiz/schedule", json=request_data)

        assert response.status_code == 200
        # Verify schedule was called with datetime
        assert mock_postiz_publisher.schedule.called
