"""
Comprehensive tests for ALL database models in src/data/models.py

Tests every single model, field, relationship, and constraint.
Covers all models from src/data/models.py (main project models)
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.models import (
    Base,
    channel_authors,
    Workspace,
    Project,
    Channel,
    Author,
    Character,
    Asset,
    FilmProject,
    Presentation,
    FilmVariant,
    PublishHistory,
    ProjectAsset,
    ShotCharacter
)


# =============================================================================
# Multi-tenancy Models Tests
# =============================================================================

class TestWorkspaceModel:
    """Test Workspace model."""

    def test_workspace_creation(self):
        """Test creating a Workspace instance."""
        workspace = Workspace(
            id="ws-123",
            name="Acme Studios",
            slug="acme-studios",
            owner_id=42,
            storage_quota_gb=500,
            monthly_budget_usd=10000.0,
            settings={"theme": "dark", "notifications": True}
        )

        assert workspace.id == "ws-123"
        assert workspace.name == "Acme Studios"
        assert workspace.slug == "acme-studios"
        assert workspace.owner_id == 42
        assert workspace.storage_quota_gb == 500
        assert workspace.monthly_budget_usd == 10000.0
        assert workspace.settings["theme"] == "dark"
        assert workspace.settings["notifications"] is True

    def test_workspace_defaults(self):
        """Test Workspace default values."""
        workspace = Workspace(
            id="ws-default",
            name="Default Workspace",
            slug="default",
            owner_id=1
        )

        assert workspace.storage_quota_gb == 100
        assert workspace.monthly_budget_usd == 1000.0
        assert workspace.settings == {}

    def test_workspace_table_name(self):
        """Test Workspace table name."""
        assert Workspace.__tablename__ == "workspaces"

    def test_workspace_repr(self):
        """Test Workspace string representation."""
        workspace = Workspace(
            id="ws-test",
            name="Test Workspace",
            slug="test-workspace",
            owner_id=1
        )
        repr_str = repr(workspace)
        assert "Workspace" in repr_str
        assert "ws-test" in repr_str
        assert "Test Workspace" in repr_str
        assert "test-workspace" in repr_str

    def test_workspace_relationships(self):
        """Test Workspace has all relationships."""
        assert hasattr(Workspace, 'projects')
        assert hasattr(Workspace, 'film_projects')
        assert hasattr(Workspace, 'characters')
        assert hasattr(Workspace, 'assets')

    def test_workspace_timestamps(self):
        """Test Workspace has timestamp columns."""
        workspace = Workspace(id="ws-1", name="Test", slug="test", owner_id=1)
        assert hasattr(workspace, 'created_at')
        assert hasattr(workspace, 'updated_at')


class TestProjectModel:
    """Test Project model."""

    def test_project_creation(self):
        """Test creating a Project instance."""
        project = Project(
            id="proj-456",
            workspace_id="ws-789",
            name="Summer Campaign 2025",
            slug="summer-campaign-2025",
            type="campaign",
            parent_project_id="proj-parent-123",
            status="active",
            description="Q3 marketing campaign for product launch",
            metadata={"budget": 50000, "team_size": 5}
        )

        assert project.id == "proj-456"
        assert project.workspace_id == "ws-789"
        assert project.name == "Summer Campaign 2025"
        assert project.slug == "summer-campaign-2025"
        assert project.type == "campaign"
        assert project.parent_project_id == "proj-parent-123"
        assert project.status == "active"
        assert project.description == "Q3 marketing campaign for product launch"
        assert project.metadata["budget"] == 50000
        assert project.metadata["team_size"] == 5

    def test_project_defaults(self):
        """Test Project default values."""
        project = Project(
            id="proj-default",
            workspace_id="ws-1",
            name="Default Project",
            slug="default-project"
        )

        assert project.type == "campaign"
        assert project.status == "active"
        assert project.metadata == {}

    def test_project_types(self):
        """Test different project types."""
        types = ["campaign", "brand", "series", "folder"]
        for proj_type in types:
            project = Project(
                id=f"proj-{proj_type}",
                workspace_id="ws-1",
                name=f"Test {proj_type}",
                slug=f"test-{proj_type}",
                type=proj_type
            )
            assert project.type == proj_type

    def test_project_table_name(self):
        """Test Project table name."""
        assert Project.__tablename__ == "projects"

    def test_project_repr(self):
        """Test Project string representation."""
        project = Project(
            id="proj-test",
            workspace_id="ws-1",
            name="Test Project",
            slug="test",
            type="campaign"
        )
        repr_str = repr(project)
        assert "Project" in repr_str
        assert "proj-test" in repr_str
        assert "Test Project" in repr_str
        assert "campaign" in repr_str

    def test_project_relationships(self):
        """Test Project has all relationships."""
        assert hasattr(Project, 'workspace')
        assert hasattr(Project, 'parent')
        assert hasattr(Project, 'film_projects')
        assert hasattr(Project, 'assets')

    def test_project_indexes(self):
        """Test Project has proper indexes."""
        table = Project.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_projects_workspace' in index_names
        assert 'idx_projects_parent' in index_names
        assert 'idx_projects_type' in index_names

    def test_project_timestamps(self):
        """Test Project has timestamp columns."""
        project = Project(id="proj-1", workspace_id="ws-1", name="Test", slug="test")
        assert hasattr(project, 'created_at')
        assert hasattr(project, 'updated_at')


# =============================================================================
# Original YouTube Models Tests
# =============================================================================

class TestChannelModel:
    """Test Channel model."""

    def test_channel_creation(self):
        """Test creating a Channel instance."""
        channel = Channel(
            id=1,
            name="Tech Reviews Channel"
        )

        assert channel.id == 1
        assert channel.name == "Tech Reviews Channel"

    def test_channel_table_name(self):
        """Test Channel table name."""
        assert Channel.__tablename__ == "channels"

    def test_channel_relationships(self):
        """Test Channel has authors relationship."""
        assert hasattr(Channel, 'authors')


class TestAuthorModel:
    """Test Author model."""

    def test_author_creation(self):
        """Test creating an Author instance."""
        author = Author(
            id=1,
            name="Albert Einstein"
        )

        assert author.id == 1
        assert author.name == "Albert Einstein"

    def test_author_table_name(self):
        """Test Author table name."""
        assert Author.__tablename__ == "authors"

    def test_author_relationships(self):
        """Test Author has channels relationship."""
        assert hasattr(Author, 'channels')


class TestChannelAuthorsTable:
    """Test channel_authors association table."""

    def test_channel_authors_exists(self):
        """Test channel_authors table exists."""
        assert channel_authors is not None

    def test_channel_authors_columns(self):
        """Test channel_authors has correct columns."""
        columns = {col.name for col in channel_authors.columns}
        assert 'channel_id' in columns
        assert 'author_id' in columns

    def test_channel_authors_foreign_keys(self):
        """Test channel_authors has foreign keys."""
        fks = list(channel_authors.foreign_keys)
        assert len(fks) == 2


# =============================================================================
# Character & Asset Models Tests
# =============================================================================

class TestCharacterModel:
    """Test Character model."""

    def test_character_creation(self):
        """Test creating a Character instance."""
        character = Character(
            id="char-123",
            workspace_id="ws-456",
            name="Sarah the Explorer",
            description="Adventurous explorer with a knack for discovery",
            reference_images=["https://example.com/ref1.jpg", "https://example.com/ref2.jpg"],
            attributes={
                "age": 28,
                "gender": "female",
                "ethnicity": "mixed",
                "hair_color": "brown",
                "eye_color": "green"
            },
            consistency_prompt="A 28-year-old female explorer with brown hair and green eyes, wearing adventure gear"
        )

        assert character.id == "char-123"
        assert character.workspace_id == "ws-456"
        assert character.name == "Sarah the Explorer"
        assert character.description == "Adventurous explorer with a knack for discovery"
        assert len(character.reference_images) == 2
        assert character.attributes["age"] == 28
        assert character.attributes["gender"] == "female"
        assert "explorer" in character.consistency_prompt

    def test_character_table_name(self):
        """Test Character table name."""
        assert Character.__tablename__ == "characters"

    def test_character_relationships(self):
        """Test Character has all relationships."""
        assert hasattr(Character, 'workspace')
        assert hasattr(Character, 'shot_appearances')

    def test_character_indexes(self):
        """Test Character has proper indexes."""
        table = Character.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_characters_workspace' in index_names

    def test_character_timestamps(self):
        """Test Character has timestamp columns."""
        character = Character(
            id="char-1",
            workspace_id="ws-1",
            name="Test Character"
        )
        assert hasattr(character, 'created_at')
        assert hasattr(character, 'updated_at')


class TestAssetModel:
    """Test Asset model."""

    def test_asset_creation(self):
        """Test creating an Asset instance."""
        asset = Asset(
            id="asset-789",
            workspace_id="ws-123",
            name="Sunset Timelapse",
            type="video",
            url="https://cdn.example.com/sunset.mp4",
            file_path="/storage/videos/sunset.mp4",
            size=52428800,  # 50MB
            duration=30.5,
            thumbnail_url="https://cdn.example.com/sunset_thumb.jpg",
            tags=["sunset", "timelapse", "nature"],
            asset_metadata={
                "codec": "h264",
                "resolution": "1920x1080",
                "fps": 30
            },
            is_favorite=True,
            character_id="char-456",
            source="generation",
            generation_cost=3.75,
            generation_metadata={
                "provider": "minimax",
                "model": "video-01",
                "prompt": "Beautiful sunset timelapse over mountains",
                "seed": 42
            }
        )

        assert asset.id == "asset-789"
        assert asset.workspace_id == "ws-123"
        assert asset.name == "Sunset Timelapse"
        assert asset.type == "video"
        assert asset.url == "https://cdn.example.com/sunset.mp4"
        assert asset.file_path == "/storage/videos/sunset.mp4"
        assert asset.size == 52428800
        assert asset.duration == 30.5
        assert asset.thumbnail_url == "https://cdn.example.com/sunset_thumb.jpg"
        assert len(asset.tags) == 3
        assert "sunset" in asset.tags
        assert asset.asset_metadata["codec"] == "h264"
        assert asset.is_favorite is True
        assert asset.character_id == "char-456"
        assert asset.source == "generation"
        assert asset.generation_cost == 3.75
        assert asset.generation_metadata["provider"] == "minimax"

    def test_asset_types(self):
        """Test different asset types."""
        types = ["image", "video", "audio", "text", "script"]
        for asset_type in types:
            asset = Asset(
                id=f"asset-{asset_type}",
                workspace_id="ws-1",
                name=f"Test {asset_type}",
                type=asset_type,
                url=f"https://example.com/{asset_type}.file"
            )
            assert asset.type == asset_type

    def test_asset_source_types(self):
        """Test different asset source types."""
        sources = ["upload", "generation", "import"]
        for source_type in sources:
            asset = Asset(
                id=f"asset-{source_type}",
                workspace_id="ws-1",
                name="Test",
                type="image",
                url="https://example.com/test.jpg",
                source=source_type
            )
            assert asset.source == source_type

    def test_asset_defaults(self):
        """Test Asset default values."""
        asset = Asset(
            id="asset-default",
            workspace_id="ws-1",
            name="Default Asset",
            type="image",
            url="https://example.com/default.jpg"
        )

        assert asset.is_favorite is False
        assert asset.access_count == 0

    def test_asset_table_name(self):
        """Test Asset table name."""
        assert Asset.__tablename__ == "assets"

    def test_asset_relationships(self):
        """Test Asset has all relationships."""
        assert hasattr(Asset, 'workspace')
        assert hasattr(Asset, 'character')
        assert hasattr(Asset, 'project_associations')

    def test_asset_indexes(self):
        """Test Asset has proper indexes."""
        table = Asset.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_assets_workspace' in index_names
        assert 'idx_assets_type' in index_names
        assert 'idx_assets_character' in index_names
        assert 'idx_assets_source_type' in index_names
        assert 'idx_assets_source_asset' in index_names
        assert 'idx_assets_cache_key' in index_names
        assert 'idx_assets_expires_at' in index_names

    def test_asset_lineage_tracking(self):
        """Test asset lineage tracking with source_asset_id."""
        source_asset = Asset(
            id="asset-source",
            workspace_id="ws-1",
            name="Source Image",
            type="image",
            url="https://example.com/source.jpg"
        )

        derived_asset = Asset(
            id="asset-derived",
            workspace_id="ws-1",
            name="Derived Video",
            type="video",
            url="https://example.com/derived.mp4",
            source_asset_id="asset-source"
        )

        assert derived_asset.source_asset_id == "asset-source"

    def test_asset_cache_fields(self):
        """Test asset cache-related fields."""
        asset = Asset(
            id="asset-cache",
            workspace_id="ws-1",
            name="Cached Asset",
            type="image",
            url="https://example.com/cached.jpg",
            cache_key="sha256:abc123def456",
            expires_at=datetime(2025, 12, 31, 23, 59, 59),
            access_count=42
        )

        assert asset.cache_key == "sha256:abc123def456"
        assert asset.expires_at == datetime(2025, 12, 31, 23, 59, 59)
        assert asset.access_count == 42

    def test_asset_timestamps(self):
        """Test Asset has timestamp columns."""
        asset = Asset(
            id="asset-1",
            workspace_id="ws-1",
            name="Test",
            type="image",
            url="https://example.com/test.jpg"
        )
        assert hasattr(asset, 'created_at')
        assert hasattr(asset, 'updated_at')
        assert hasattr(asset, 'last_accessed_at')


# =============================================================================
# Film Project Models Tests
# =============================================================================

class TestFilmProjectModel:
    """Test FilmProject model."""

    def test_film_project_creation(self):
        """Test creating a FilmProject instance."""
        film = FilmProject(
            id="film-001",
            workspace_id="ws-123",
            project_id="proj-456",
            title="The Great Adventure",
            description="An epic tale of exploration and discovery",
            status="completed",
            shots_config=[
                {"shot": 1, "description": "Opening scene"},
                {"shot": 2, "description": "Hero introduction"}
            ],
            generated_shots=[
                {"shot": 1, "url": "https://example.com/shot1.mp4"},
                {"shot": 2, "url": "https://example.com/shot2.mp4"}
            ],
            video_provider="minimax",
            image_provider="fal",
            audio_provider="openai",
            total_cost=12.50,
            budget_limit=20.00,
            output_path="/storage/films/great_adventure.mp4",
            published_at=datetime(2025, 6, 15, 10, 30, 0),
            published_platforms=["youtube", "tiktok"]
        )

        assert film.id == "film-001"
        assert film.workspace_id == "ws-123"
        assert film.project_id == "proj-456"
        assert film.title == "The Great Adventure"
        assert film.status == "completed"
        assert len(film.shots_config) == 2
        assert len(film.generated_shots) == 2
        assert film.video_provider == "minimax"
        assert film.total_cost == 12.50
        assert film.budget_limit == 20.00
        assert len(film.published_platforms) == 2

    def test_film_project_defaults(self):
        """Test FilmProject default values."""
        film = FilmProject(
            id="film-default",
            workspace_id="ws-1",
            title="Default Film"
        )

        assert film.status == "pending"
        assert film.total_cost == 0.0
        assert film.published_platforms == []

    def test_film_project_statuses(self):
        """Test different film project statuses."""
        statuses = ["pending", "processing", "completed", "failed"]
        for status in statuses:
            film = FilmProject(
                id=f"film-{status}",
                workspace_id="ws-1",
                title=f"Film {status}",
                status=status
            )
            assert film.status == status

    def test_film_project_providers(self):
        """Test different provider combinations."""
        film = FilmProject(
            id="film-providers",
            workspace_id="ws-1",
            title="Provider Test",
            video_provider="runway",
            image_provider="replicate",
            audio_provider="elevenlabs"
        )

        assert film.video_provider == "runway"
        assert film.image_provider == "replicate"
        assert film.audio_provider == "elevenlabs"

    def test_film_project_variant_tracking(self):
        """Test film variant tracking fields."""
        base_film = FilmProject(
            id="film-base",
            workspace_id="ws-1",
            title="Base Film",
            variant_type=None
        )

        variant_film = FilmProject(
            id="film-variant",
            workspace_id="ws-1",
            title="Platform Variant",
            base_film_id="film-base",
            variant_type="platform_variant"
        )

        assert base_film.variant_type is None
        assert variant_film.base_film_id == "film-base"
        assert variant_film.variant_type == "platform_variant"

    def test_film_project_table_name(self):
        """Test FilmProject table name."""
        assert FilmProject.__tablename__ == "film_projects"

    def test_film_project_relationships(self):
        """Test FilmProject has all relationships."""
        assert hasattr(FilmProject, 'workspace')
        assert hasattr(FilmProject, 'project')
        assert hasattr(FilmProject, 'base_film')
        assert hasattr(FilmProject, 'platform_variants')
        assert hasattr(FilmProject, 'publish_history')
        assert hasattr(FilmProject, 'shot_characters')

    def test_film_project_indexes(self):
        """Test FilmProject has proper indexes."""
        table = FilmProject.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_film_projects_workspace' in index_names
        assert 'idx_film_projects_project' in index_names
        assert 'idx_film_projects_status' in index_names
        assert 'idx_film_projects_base' in index_names

    def test_film_project_timestamps(self):
        """Test FilmProject has timestamp columns."""
        film = FilmProject(id="film-1", workspace_id="ws-1", title="Test")
        assert hasattr(film, 'created_at')
        assert hasattr(film, 'updated_at')
        assert hasattr(film, 'completed_at')


class TestPresentationModel:
    """Test Presentation model."""

    def test_presentation_creation(self):
        """Test creating a Presentation instance."""
        pres = Presentation(
            id="pptx-001",
            title="Q3 Sales Review",
            topic="Quarterly Sales Performance",
            brief="Analysis of Q3 sales metrics and trends",
            content_source="ai",
            content_url=None,
            num_slides=15,
            tone="professional",
            target_audience="executives",
            model="gpt-4o",
            status="completed",
            outline=[
                {"slide": 1, "title": "Overview", "content": "Q3 highlights"},
                {"slide": 2, "title": "Metrics", "content": "Key performance indicators"}
            ],
            total_cost=0.75,
            budget_limit=2.00,
            output_path="/storage/presentations/q3_sales_review.pptx"
        )

        assert pres.id == "pptx-001"
        assert pres.title == "Q3 Sales Review"
        assert pres.topic == "Quarterly Sales Performance"
        assert pres.content_source == "ai"
        assert pres.num_slides == 15
        assert pres.tone == "professional"
        assert pres.model == "gpt-4o"
        assert pres.status == "completed"
        assert len(pres.outline) == 2
        assert pres.total_cost == 0.75

    def test_presentation_content_sources(self):
        """Test different content sources."""
        sources = ["ai", "youtube", "web", "file"]
        for source in sources:
            pres = Presentation(
                id=f"pptx-{source}",
                title=f"Test {source}",
                topic="Test",
                content_source=source
            )
            assert pres.content_source == source

    def test_presentation_defaults(self):
        """Test Presentation default values."""
        pres = Presentation(
            id="pptx-default",
            title="Default",
            topic="Default Topic",
            content_source="ai"
        )

        assert pres.num_slides == 10
        assert pres.tone == "professional"
        assert pres.model == "gpt-4o-mini"
        assert pres.status == "pending"
        assert pres.total_cost == 0.0

    def test_presentation_table_name(self):
        """Test Presentation table name."""
        assert Presentation.__tablename__ == "presentations"

    def test_presentation_timestamps(self):
        """Test Presentation has timestamp columns."""
        pres = Presentation(
            id="pptx-1",
            title="Test",
            topic="Test",
            content_source="ai"
        )
        assert hasattr(pres, 'created_at')
        assert hasattr(pres, 'updated_at')
        assert hasattr(pres, 'completed_at')


# =============================================================================
# Platform Variants & Publishing Models Tests
# =============================================================================

class TestFilmVariantModel:
    """Test FilmVariant model."""

    def test_film_variant_creation(self):
        """Test creating a FilmVariant instance."""
        variant = FilmVariant(
            id="variant-001",
            film_project_id="film-123",
            platform="tiktok",
            aspect_ratio="9:16",
            width=1080,
            height=1920,
            max_duration_seconds=60,
            output_path="/storage/variants/film123_tiktok.mp4",
            status="completed",
            generation_config={
                "crop_mode": "smart",
                "subtitle_size": "large"
            }
        )

        assert variant.id == "variant-001"
        assert variant.film_project_id == "film-123"
        assert variant.platform == "tiktok"
        assert variant.aspect_ratio == "9:16"
        assert variant.width == 1080
        assert variant.height == 1920
        assert variant.max_duration_seconds == 60
        assert variant.status == "completed"
        assert variant.generation_config["crop_mode"] == "smart"

    def test_film_variant_platforms(self):
        """Test different platform variants."""
        platforms = [
            ("youtube", "16:9", 1920, 1080),
            ("tiktok", "9:16", 1080, 1920),
            ("instagram_reels", "9:16", 1080, 1920),
            ("instagram_feed", "1:1", 1080, 1080)
        ]

        for platform, ratio, width, height in platforms:
            variant = FilmVariant(
                id=f"variant-{platform}",
                film_project_id="film-1",
                platform=platform,
                aspect_ratio=ratio,
                width=width,
                height=height
            )

            assert variant.platform == platform
            assert variant.aspect_ratio == ratio
            assert variant.width == width
            assert variant.height == height

    def test_film_variant_defaults(self):
        """Test FilmVariant default values."""
        variant = FilmVariant(
            id="variant-default",
            film_project_id="film-1",
            platform="youtube",
            aspect_ratio="16:9",
            width=1920,
            height=1080
        )

        assert variant.status == "pending"

    def test_film_variant_table_name(self):
        """Test FilmVariant table name."""
        assert FilmVariant.__tablename__ == "film_variants"

    def test_film_variant_relationships(self):
        """Test FilmVariant has all relationships."""
        assert hasattr(FilmVariant, 'film_project')
        assert hasattr(FilmVariant, 'publish_records')

    def test_film_variant_indexes(self):
        """Test FilmVariant has proper indexes."""
        table = FilmVariant.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_film_variants_project' in index_names
        assert 'idx_film_variants_platform' in index_names

    def test_film_variant_timestamps(self):
        """Test FilmVariant has timestamp columns."""
        variant = FilmVariant(
            id="variant-1",
            film_project_id="film-1",
            platform="youtube",
            aspect_ratio="16:9",
            width=1920,
            height=1080
        )
        assert hasattr(variant, 'created_at')
        assert hasattr(variant, 'updated_at')


class TestPublishHistoryModel:
    """Test PublishHistory model."""

    def test_publish_history_creation(self):
        """Test creating a PublishHistory instance."""
        history = PublishHistory(
            id="pub-001",
            film_variant_id="variant-123",
            film_project_id="film-456",
            account_id="account-789",
            platform="youtube",
            platform_post_id="YT-abc123",
            post_url="https://youtube.com/watch?v=abc123",
            title="Amazing Short Film",
            description="Watch this incredible short film!",
            published_at=datetime(2025, 6, 1, 14, 30, 0),
            status="published",
            metrics={
                "views": 10000,
                "likes": 500,
                "comments": 50,
                "shares": 25
            }
        )

        assert history.id == "pub-001"
        assert history.film_variant_id == "variant-123"
        assert history.film_project_id == "film-456"
        assert history.account_id == "account-789"
        assert history.platform == "youtube"
        assert history.platform_post_id == "YT-abc123"
        assert history.post_url == "https://youtube.com/watch?v=abc123"
        assert history.title == "Amazing Short Film"
        assert history.status == "published"
        assert history.metrics["views"] == 10000
        assert history.metrics["likes"] == 500

    def test_publish_history_platforms(self):
        """Test different publishing platforms."""
        platforms = ["youtube", "tiktok", "instagram", "facebook", "twitter"]
        for platform in platforms:
            history = PublishHistory(
                id=f"pub-{platform}",
                film_project_id="film-1",
                account_id="account-1",
                platform=platform,
                published_at=datetime.now()
            )
            assert history.platform == platform

    def test_publish_history_defaults(self):
        """Test PublishHistory default values."""
        history = PublishHistory(
            id="pub-default",
            film_project_id="film-1",
            account_id="account-1",
            platform="youtube",
            published_at=datetime.now()
        )

        assert history.status == "published"
        assert history.metrics == {}

    def test_publish_history_table_name(self):
        """Test PublishHistory table name."""
        assert PublishHistory.__tablename__ == "publish_history"

    def test_publish_history_relationships(self):
        """Test PublishHistory has all relationships."""
        assert hasattr(PublishHistory, 'film_variant')
        assert hasattr(PublishHistory, 'film_project')

    def test_publish_history_indexes(self):
        """Test PublishHistory has proper indexes."""
        table = PublishHistory.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_publish_history_variant' in index_names
        assert 'idx_publish_history_project' in index_names
        assert 'idx_publish_history_platform' in index_names
        assert 'idx_publish_history_published_at' in index_names

    def test_publish_history_timestamps(self):
        """Test PublishHistory has timestamp columns."""
        history = PublishHistory(
            id="pub-1",
            film_project_id="film-1",
            account_id="account-1",
            platform="youtube",
            published_at=datetime.now()
        )
        assert hasattr(history, 'created_at')
        assert hasattr(history, 'updated_at')


# =============================================================================
# Relationship Tables Tests
# =============================================================================

class TestProjectAssetModel:
    """Test ProjectAsset association model."""

    def test_project_asset_creation(self):
        """Test creating a ProjectAsset instance."""
        pa = ProjectAsset(
            project_id="proj-123",
            asset_id="asset-456",
            role="final",
            used_in_shots=["shot-001", "shot-003", "shot-007"]
        )

        assert pa.project_id == "proj-123"
        assert pa.asset_id == "asset-456"
        assert pa.role == "final"
        assert len(pa.used_in_shots) == 3
        assert "shot-001" in pa.used_in_shots

    def test_project_asset_roles(self):
        """Test different project asset roles."""
        roles = ["source", "generated", "intermediate", "final"]
        for role in roles:
            pa = ProjectAsset(
                project_id="proj-1",
                asset_id="asset-1",
                role=role
            )
            assert pa.role == role

    def test_project_asset_defaults(self):
        """Test ProjectAsset default values."""
        pa = ProjectAsset(
            project_id="proj-1",
            asset_id="asset-1",
            role="source"
        )

        assert pa.used_in_shots == []

    def test_project_asset_table_name(self):
        """Test ProjectAsset table name."""
        assert ProjectAsset.__tablename__ == "project_assets"

    def test_project_asset_relationships(self):
        """Test ProjectAsset has all relationships."""
        assert hasattr(ProjectAsset, 'project')
        assert hasattr(ProjectAsset, 'asset')

    def test_project_asset_indexes(self):
        """Test ProjectAsset has proper indexes."""
        table = ProjectAsset.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_project_assets_project' in index_names
        assert 'idx_project_assets_asset' in index_names

    def test_project_asset_timestamp(self):
        """Test ProjectAsset has created_at timestamp."""
        pa = ProjectAsset(
            project_id="proj-1",
            asset_id="asset-1",
            role="source"
        )
        assert hasattr(pa, 'created_at')


class TestShotCharacterModel:
    """Test ShotCharacter association model."""

    def test_shot_character_creation(self):
        """Test creating a ShotCharacter instance."""
        sc = ShotCharacter(
            film_project_id="film-123",
            shot_id="shot-005",
            character_id="char-789",
            shot_index=5,
            prominence="primary",
            screen_time_seconds=12.5
        )

        assert sc.film_project_id == "film-123"
        assert sc.shot_id == "shot-005"
        assert sc.character_id == "char-789"
        assert sc.shot_index == 5
        assert sc.prominence == "primary"
        assert sc.screen_time_seconds == 12.5

    def test_shot_character_prominence_levels(self):
        """Test different prominence levels."""
        prominence_levels = ["primary", "secondary", "background"]
        for prominence in prominence_levels:
            sc = ShotCharacter(
                film_project_id="film-1",
                shot_id="shot-1",
                character_id="char-1",
                shot_index=1,
                prominence=prominence
            )
            assert sc.prominence == prominence

    def test_shot_character_defaults(self):
        """Test ShotCharacter default values."""
        sc = ShotCharacter(
            film_project_id="film-1",
            shot_id="shot-1",
            character_id="char-1",
            shot_index=1
        )

        assert sc.prominence == "primary"

    def test_shot_character_table_name(self):
        """Test ShotCharacter table name."""
        assert ShotCharacter.__tablename__ == "shot_characters"

    def test_shot_character_relationships(self):
        """Test ShotCharacter has all relationships."""
        assert hasattr(ShotCharacter, 'film_project')
        assert hasattr(ShotCharacter, 'character')

    def test_shot_character_indexes(self):
        """Test ShotCharacter has proper indexes."""
        table = ShotCharacter.__table__
        index_names = [idx.name for idx in table.indexes]
        assert 'idx_shot_characters_film' in index_names
        assert 'idx_shot_characters_character' in index_names
        assert 'idx_shot_characters_shot' in index_names

    def test_shot_character_timestamp(self):
        """Test ShotCharacter has created_at timestamp."""
        sc = ShotCharacter(
            film_project_id="film-1",
            shot_id="shot-1",
            character_id="char-1",
            shot_index=1
        )
        assert hasattr(sc, 'created_at')


# =============================================================================
# Model Constraints and Validations Tests
# =============================================================================

class TestModelConstraints:
    """Test model constraints and validations."""

    def test_workspace_unique_slug(self):
        """Test Workspace slug is unique."""
        slug_col = Workspace.__table__.columns['slug']
        assert slug_col.unique is True

    def test_workspace_not_null_fields(self):
        """Test Workspace required fields."""
        assert Workspace.__table__.columns['name'].nullable is False
        assert Workspace.__table__.columns['slug'].nullable is False
        assert Workspace.__table__.columns['owner_id'].nullable is False

    def test_project_not_null_fields(self):
        """Test Project required fields."""
        assert Project.__table__.columns['workspace_id'].nullable is False
        assert Project.__table__.columns['name'].nullable is False
        assert Project.__table__.columns['slug'].nullable is False

    def test_character_not_null_fields(self):
        """Test Character required fields."""
        assert Character.__table__.columns['workspace_id'].nullable is False
        assert Character.__table__.columns['name'].nullable is False

    def test_asset_not_null_fields(self):
        """Test Asset required fields."""
        assert Asset.__table__.columns['workspace_id'].nullable is False
        assert Asset.__table__.columns['name'].nullable is False
        assert Asset.__table__.columns['type'].nullable is False
        assert Asset.__table__.columns['url'].nullable is False

    def test_film_project_not_null_fields(self):
        """Test FilmProject required fields."""
        assert FilmProject.__table__.columns['workspace_id'].nullable is False
        assert FilmProject.__table__.columns['title'].nullable is False


class TestModelCascadeDeletes:
    """Test cascade delete configurations."""

    def test_workspace_cascade_to_projects(self):
        """Test Workspace deletes cascade to Projects."""
        # Check foreign key ondelete
        fk = Project.__table__.columns['workspace_id'].foreign_keys
        fk_list = list(fk)
        assert len(fk_list) > 0
        assert fk_list[0].ondelete == 'CASCADE'

    def test_workspace_cascade_to_characters(self):
        """Test Workspace deletes cascade to Characters."""
        fk = Character.__table__.columns['workspace_id'].foreign_keys
        fk_list = list(fk)
        assert len(fk_list) > 0
        assert fk_list[0].ondelete == 'CASCADE'

    def test_workspace_cascade_to_assets(self):
        """Test Workspace deletes cascade to Assets."""
        fk = Asset.__table__.columns['workspace_id'].foreign_keys
        fk_list = list(fk)
        assert len(fk_list) > 0
        assert fk_list[0].ondelete == 'CASCADE'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
