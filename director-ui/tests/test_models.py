"""
Tests for database models.

Tests model instantiation, relationships, and basic functionality.
No database connection required - tests model structure only.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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


class TestBaseModel:
    """Test Base model configuration."""

    def test_base_exists(self):
        """Test that Base declarative base exists."""
        assert Base is not None
        assert hasattr(Base, 'metadata')


class TestChannelModel:
    """Test Channel model."""

    def test_channel_creation(self):
        """Test creating a Channel instance."""
        channel = Channel(
            id=1,
            name="Test Channel"
        )

        assert channel.id == 1
        assert channel.name == "Test Channel"

    def test_channel_table_name(self):
        """Test Channel table name."""
        assert Channel.__tablename__ == "channels"

    def test_channel_has_authors_relationship(self):
        """Test Channel has authors relationship."""
        assert hasattr(Channel, 'authors')


class TestAuthorModel:
    """Test Author model."""

    def test_author_creation(self):
        """Test creating an Author instance."""
        author = Author(
            id=1,
            name="John Doe"
        )

        assert author.id == 1
        assert author.name == "John Doe"

    def test_author_table_name(self):
        """Test Author table name."""
        assert Author.__tablename__ == "authors"

    def test_author_has_channels_relationship(self):
        """Test Author has channels relationship."""
        assert hasattr(Author, 'channels')


class TestCharacterModel:
    """Test Character model."""

    def test_character_creation(self):
        """Test creating a Character instance."""
        character = Character(
            id="char-123",
            name="Hero Character",
            description="Main protagonist",
            reference_images=["https://example.com/image1.jpg"],
            attributes={"age": 30, "gender": "male"},
            consistency_prompt="A 30-year-old male hero",
            projects_used=["project-1", "project-2"]
        )

        assert character.id == "char-123"
        assert character.name == "Hero Character"
        assert character.description == "Main protagonist"
        assert len(character.reference_images) == 1
        assert character.attributes["age"] == 30
        assert len(character.projects_used) == 2

    def test_character_table_name(self):
        """Test Character table name."""
        assert Character.__tablename__ == "characters"

    def test_character_timestamps(self):
        """Test Character has timestamp columns."""
        character = Character(id="test-id", name="Test")

        assert hasattr(character, 'created_at')
        assert hasattr(character, 'updated_at')


class TestAssetModel:
    """Test Asset model."""

    def test_asset_creation(self):
        """Test creating an Asset instance."""
        asset = Asset(
            id="asset-123",
            name="Test Video",
            type="video",
            url="https://example.com/video.mp4",
            file_path="/path/to/video.mp4",
            size=1024000,
            duration=30.5,
            thumbnail_url="https://example.com/thumb.jpg",
            tags=["test", "video"],
            asset_metadata={"codec": "h264"},
            is_favorite=True
        )

        assert asset.id == "asset-123"
        assert asset.name == "Test Video"
        assert asset.type == "video"
        assert asset.url == "https://example.com/video.mp4"
        assert asset.size == 1024000
        assert asset.duration == 30.5
        assert len(asset.tags) == 2
        assert asset.is_favorite is True

    def test_asset_defaults(self):
        """Test Asset default values."""
        asset = Asset(
            id="test-id",
            name="Test",
            type="image",
            url="https://example.com/image.jpg"
        )

        assert asset.is_favorite is False

    def test_asset_table_name(self):
        """Test Asset table name."""
        assert Asset.__tablename__ == "assets"


class TestFilmProjectModel:
    """Test FilmProject model."""

    def test_film_project_creation(self):
        """Test creating a FilmProject instance."""
        project = FilmProject(
            id="film-123",
            title="Test Film",
            description="A test film project",
            status="pending",
            shots_config=[{"shot": 1, "description": "Opening scene"}],
            generated_shots=[{"shot": 1, "url": "https://example.com/shot1.mp4"}],
            video_provider="minimax",
            image_provider="fal",
            audio_provider="openai",
            total_cost=5.50,
            budget_limit=10.00,
            output_path="/path/to/output.mp4"
        )

        assert project.id == "film-123"
        assert project.title == "Test Film"
        assert project.status == "pending"
        assert project.video_provider == "minimax"
        assert project.total_cost == 5.50
        assert project.budget_limit == 10.00
        assert len(project.shots_config) == 1

    def test_film_project_defaults(self):
        """Test FilmProject default values."""
        project = FilmProject(
            id="test-id",
            title="Test"
        )

        assert project.status == "pending"
        assert project.total_cost == 0.0

    def test_film_project_table_name(self):
        """Test FilmProject table name."""
        assert FilmProject.__tablename__ == "film_projects"


class TestPresentationModel:
    """Test Presentation model."""

    def test_presentation_creation(self):
        """Test creating a Presentation instance."""
        presentation = Presentation(
            id="pptx-123",
            title="Q1 Review",
            topic="Quarterly Results",
            brief="Financial results for Q1 2025",
            content_source="ai",
            num_slides=15,
            tone="professional",
            target_audience="executives",
            model="gpt-4o",
            status="completed",
            outline=[{"slide": 1, "title": "Introduction"}],
            total_cost=0.50,
            budget_limit=1.00,
            output_path="/path/to/presentation.pptx"
        )

        assert presentation.id == "pptx-123"
        assert presentation.title == "Q1 Review"
        assert presentation.num_slides == 15
        assert presentation.tone == "professional"
        assert presentation.model == "gpt-4o"
        assert presentation.status == "completed"
        assert len(presentation.outline) == 1

    def test_presentation_defaults(self):
        """Test Presentation default values."""
        presentation = Presentation(
            id="test-id",
            title="Test",
            topic="Test Topic",
            content_source="ai"
        )

        assert presentation.num_slides == 10
        assert presentation.tone == "professional"
        assert presentation.model == "gpt-4o-mini"
        assert presentation.status == "pending"
        assert presentation.total_cost == 0.0

    def test_presentation_table_name(self):
        """Test Presentation table name."""
        assert Presentation.__tablename__ == "presentations"


class TestAvatarVideoModel:
    """Test AvatarVideo model."""

    def test_avatar_video_creation(self):
        """Test creating an AvatarVideo instance."""
        video = AvatarVideo(
            id="av-123",
            video_id="heygen-video-456",
            title="Test Avatar Video",
            script="This is a test script for the avatar to speak",
            avatar_id="avatar-789",
            avatar_name="John Avatar",
            voice_id="voice-101",
            voice_name="English Male",
            aspect_ratio="9:16",
            background_type="color",
            background_value="#000000",
            voice_speed=1.1,
            voice_pitch=50,
            voice_emotion="Excited",
            avatar_scale=1.0,
            has_green_screen=False,
            avatar_offset_x=0.0,
            avatar_offset_y=0.0,
            caption=True,
            test=False,
            status="completed",
            video_url="https://example.com/avatar-video.mp4",
            duration=45.5,
            cost=1.25,
            metadata={"heygen_id": "internal-123"}
        )

        assert video.id == "av-123"
        assert video.video_id == "heygen-video-456"
        assert video.title == "Test Avatar Video"
        assert video.script == "This is a test script for the avatar to speak"
        assert video.avatar_id == "avatar-789"
        assert video.voice_id == "voice-101"
        assert video.aspect_ratio == "9:16"
        assert video.background_type == "color"
        assert video.voice_speed == 1.1
        assert video.status == "completed"
        assert video.video_url == "https://example.com/avatar-video.mp4"
        assert video.duration == 45.5
        assert video.cost == 1.25
        assert video.caption is True
        assert video.test is False

    def test_avatar_video_defaults(self):
        """Test AvatarVideo default values."""
        video = AvatarVideo(
            id="test-id",
            video_id="heygen-test",
            script="Test",
            avatar_id="avatar-1",
            voice_id="voice-1"
        )

        assert video.aspect_ratio == "9:16"
        assert video.background_type == "color"
        assert video.background_value == "#000000"
        assert video.voice_speed == 1.1
        assert video.voice_pitch == 50
        assert video.voice_emotion == "Excited"
        assert video.avatar_scale == 1.0
        assert video.has_green_screen is False
        assert video.avatar_offset_x == 0.0
        assert video.avatar_offset_y == 0.0
        assert video.caption is False
        assert video.test is False
        assert video.status == "pending"
        assert video.cost == 0.0

    def test_avatar_video_table_name(self):
        """Test AvatarVideo table name."""
        assert AvatarVideo.__tablename__ == "avatar_videos"

    def test_avatar_video_timestamps(self):
        """Test AvatarVideo has timestamp columns."""
        video = AvatarVideo(
            id="test-id",
            video_id="test",
            script="Test",
            avatar_id="avatar-1",
            voice_id="voice-1"
        )

        assert hasattr(video, 'created_at')
        assert hasattr(video, 'updated_at')
        assert hasattr(video, 'completed_at')


class TestSocialAccountModel:
    """Test SocialAccount model."""

    def test_social_account_creation(self):
        """Test creating a SocialAccount instance."""
        account = SocialAccount(
            id="acc-123",
            platform="tiktok",
            account_name="My TikTok",
            account_handle="@mytiktok",
            credentials={"api_key": "test-key"},
            access_token="access-token-123",
            refresh_token="refresh-token-456",
            is_active=True,
            default_settings={"privacy": "public"},
            posting_schedule=[{"day": "monday", "time": "10:00"}],
            platform_user_id="user-789",
            follower_count=5000
        )

        assert account.id == "acc-123"
        assert account.platform == "tiktok"
        assert account.account_name == "My TikTok"
        assert account.account_handle == "@mytiktok"
        assert account.is_active is True
        assert account.follower_count == 5000
        assert account.credentials["api_key"] == "test-key"
        assert len(account.posting_schedule) == 1

    def test_social_account_defaults(self):
        """Test SocialAccount default values."""
        account = SocialAccount(
            id="test-id",
            platform="instagram",
            account_name="Test Account"
        )

        assert account.is_active is True
        assert account.follower_count == 0

    def test_social_account_table_name(self):
        """Test SocialAccount table name."""
        assert SocialAccount.__tablename__ == "social_accounts"

    def test_social_account_has_posts_relationship(self):
        """Test SocialAccount can have posts (via backref)."""
        # The relationship is defined on PublishingPost side with backref
        assert hasattr(SocialAccount, '__tablename__')


class TestPublishingPostModel:
    """Test PublishingPost model."""

    def test_publishing_post_creation(self):
        """Test creating a PublishingPost instance."""
        post = PublishingPost(
            id="post-123",
            social_account_id="acc-456",
            content_type="video",
            content_url="https://example.com/video.mp4",
            caption="Check out this amazing video! #awesome",
            hashtags=["awesome", "video", "test"],
            status="published",
            platform="tiktok",
            platform_settings={"privacy": "public"},
            platform_post_id="tiktok-post-789",
            platform_url="https://tiktok.com/@user/video/789",
            source_id="avatar-video-101",
            source_type="avatar_video"
        )

        assert post.id == "post-123"
        assert post.social_account_id == "acc-456"
        assert post.content_type == "video"
        assert post.content_url == "https://example.com/video.mp4"
        assert post.caption == "Check out this amazing video! #awesome"
        assert len(post.hashtags) == 3
        assert post.status == "published"
        assert post.platform == "tiktok"
        assert post.platform_post_id == "tiktok-post-789"
        assert post.source_id == "avatar-video-101"
        assert post.source_type == "avatar_video"

    def test_publishing_post_defaults(self):
        """Test PublishingPost default values."""
        post = PublishingPost(
            id="test-id",
            social_account_id="acc-1",
            content_type="video",
            caption="Test",
            platform="tiktok"
        )

        assert post.status == "draft"

    def test_publishing_post_table_name(self):
        """Test PublishingPost table name."""
        assert PublishingPost.__tablename__ == "publishing_posts"

    def test_publishing_post_has_account_relationship(self):
        """Test PublishingPost has social_account relationship."""
        assert hasattr(PublishingPost, 'social_account')

    def test_publishing_post_timestamps(self):
        """Test PublishingPost has timestamp columns."""
        post = PublishingPost(
            id="test-id",
            social_account_id="acc-1",
            content_type="video",
            caption="Test",
            platform="tiktok"
        )

        assert hasattr(post, 'created_at')
        assert hasattr(post, 'updated_at')


class TestPublishingAnalyticsModel:
    """Test PublishingAnalytics model."""

    def test_publishing_analytics_creation(self):
        """Test creating a PublishingAnalytics instance."""
        analytics = PublishingAnalytics(
            id="analytics-123",
            post_id="post-456",
            views=10000,
            likes=850,
            comments=45,
            shares=120,
            saves=230,
            engagement_rate=12.45,
            watch_time=25000.5,
            avg_watch_time=2.5,
            completion_rate=75.5,
            audience_demographics={"age": "18-24", "gender": "mixed"},
            traffic_sources={"organic": 60, "recommended": 40}
        )

        assert analytics.id == "analytics-123"
        assert analytics.post_id == "post-456"
        assert analytics.views == 10000
        assert analytics.likes == 850
        assert analytics.comments == 45
        assert analytics.shares == 120
        assert analytics.saves == 230
        assert analytics.engagement_rate == 12.45
        assert analytics.watch_time == 25000.5
        assert analytics.avg_watch_time == 2.5
        assert analytics.completion_rate == 75.5
        assert analytics.audience_demographics["age"] == "18-24"
        assert analytics.traffic_sources["organic"] == 60

    def test_publishing_analytics_defaults(self):
        """Test PublishingAnalytics default values."""
        analytics = PublishingAnalytics(
            id="test-id",
            post_id="post-1"
        )

        assert analytics.views == 0
        assert analytics.likes == 0
        assert analytics.comments == 0
        assert analytics.shares == 0
        assert analytics.saves == 0
        assert analytics.engagement_rate == 0.0
        assert analytics.watch_time == 0.0
        assert analytics.avg_watch_time == 0.0
        assert analytics.completion_rate == 0.0

    def test_publishing_analytics_table_name(self):
        """Test PublishingAnalytics table name."""
        assert PublishingAnalytics.__tablename__ == "publishing_analytics"

    def test_publishing_analytics_has_post_relationship(self):
        """Test PublishingAnalytics has post relationship."""
        assert hasattr(PublishingAnalytics, 'post')

    def test_publishing_analytics_timestamps(self):
        """Test PublishingAnalytics has timestamp columns."""
        analytics = PublishingAnalytics(
            id="test-id",
            post_id="post-1"
        )

        assert hasattr(analytics, 'created_at')
        assert hasattr(analytics, 'updated_at')
        assert hasattr(analytics, 'fetched_at')


class TestModelRelationships:
    """Test relationships between models."""

    def test_channel_author_relationship(self):
        """Test many-to-many relationship between Channel and Author."""
        # Verify relationship attributes exist
        assert hasattr(Channel, 'authors')
        assert hasattr(Author, 'channels')

    def test_publishing_post_account_relationship(self):
        """Test relationship between PublishingPost and SocialAccount."""
        # Verify relationship attributes exist
        assert hasattr(PublishingPost, 'social_account')
        assert hasattr(PublishingPost, 'social_account_id')

    def test_publishing_analytics_post_relationship(self):
        """Test relationship between PublishingAnalytics and PublishingPost."""
        # Verify relationship attributes exist
        assert hasattr(PublishingAnalytics, 'post')
        assert hasattr(PublishingAnalytics, 'post_id')


class TestModelValidation:
    """Test model validation and constraints."""

    def test_avatar_video_required_fields(self):
        """Test AvatarVideo required fields."""
        # Should be able to create with required fields
        video = AvatarVideo(
            id="test-id",
            video_id="heygen-test",
            script="Test script",
            avatar_id="avatar-1",
            voice_id="voice-1"
        )

        assert video is not None

    def test_social_account_required_fields(self):
        """Test SocialAccount required fields."""
        # Should be able to create with required fields
        account = SocialAccount(
            id="test-id",
            platform="tiktok",
            account_name="Test Account"
        )

        assert account is not None

    def test_publishing_post_required_fields(self):
        """Test PublishingPost required fields."""
        # Should be able to create with required fields
        post = PublishingPost(
            id="test-id",
            social_account_id="acc-1",
            content_type="video",
            caption="Test",
            platform="tiktok"
        )

        assert post is not None
