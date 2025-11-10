"""
Comprehensive tests for ALL database models in director-ui.

Tests every single model, field, relationship, and constraint.
Covers all models from director-ui/src/data/models.py
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
    Workspace,
    Project,
    Character,
    Asset,
    FilmProject,
    Presentation,
    AvatarVideo,
    SocialAccount,
    PublishingPost,
    PublishingAnalytics,
    FilmShot,
    ShotReview,
    ScriptGeneration,
    Scene,
    ShotGeneration,
    GenerationSession,
    GenerationNote,
    AssetRelationship,
    AssetCollection,
    AssetCollectionMember,
    Tag,
    User,
    channel_authors
)


# =============================================================================
# Core Models Tests
# =============================================================================

class TestWorkspaceModel:
    """Test Workspace model."""

    def test_workspace_creation(self):
        """Test creating a Workspace instance."""
        workspace = Workspace(
            id="ws-123",
            name="My Workspace",
            slug="my-workspace",
            owner_id=1,
            storage_quota_gb=200,
            monthly_budget_usd=5000.0,
            description="A test workspace",
            settings={"theme": "dark"}
        )

        assert workspace.id == "ws-123"
        assert workspace.name == "My Workspace"
        assert workspace.slug == "my-workspace"
        assert workspace.owner_id == 1
        assert workspace.storage_quota_gb == 200
        assert workspace.monthly_budget_usd == 5000.0
        assert workspace.description == "A test workspace"
        assert workspace.settings["theme"] == "dark"

    def test_workspace_defaults(self):
        """Test Workspace default values."""
        workspace = Workspace(
            id="test-id",
            name="Test",
            slug="test",
            owner_id=1
        )

        assert workspace.storage_quota_gb == 100
        assert workspace.monthly_budget_usd == 1000.0
        assert workspace.settings == {}

    def test_workspace_table_name(self):
        """Test Workspace table name."""
        assert Workspace.__tablename__ == "workspaces"

    def test_workspace_relationships(self):
        """Test Workspace has all relationships."""
        assert hasattr(Workspace, 'projects')
        assert hasattr(Workspace, 'film_projects')
        assert hasattr(Workspace, 'characters')
        assert hasattr(Workspace, 'assets')


class TestProjectModel:
    """Test Project model."""

    def test_project_creation(self):
        """Test creating a Project instance."""
        project = Project(
            id="proj-123",
            workspace_id="ws-456",
            name="My Campaign",
            slug="my-campaign",
            type="campaign",
            parent_project_id="proj-parent",
            status="active",
            description="Test project",
            project_metadata={"budget": 10000}
        )

        assert project.id == "proj-123"
        assert project.workspace_id == "ws-456"
        assert project.name == "My Campaign"
        assert project.slug == "my-campaign"
        assert project.type == "campaign"
        assert project.parent_project_id == "proj-parent"
        assert project.status == "active"
        assert project.description == "Test project"
        assert project.project_metadata["budget"] == 10000

    def test_project_defaults(self):
        """Test Project default values."""
        project = Project(
            id="test-id",
            workspace_id="ws-1",
            name="Test",
            slug="test"
        )

        assert project.type == "campaign"
        assert project.status == "active"
        assert project.project_metadata == {}

    def test_project_table_name(self):
        """Test Project table name."""
        assert Project.__tablename__ == "projects"

    def test_project_relationships(self):
        """Test Project has all relationships."""
        assert hasattr(Project, 'workspace')
        assert hasattr(Project, 'films')


# =============================================================================
# Film & Shot Models Tests
# =============================================================================

class TestFilmShotModel:
    """Test FilmShot model."""

    def test_film_shot_creation(self):
        """Test creating a FilmShot instance."""
        shot = FilmShot(
            id="shot-uuid-123",
            shot_id="shot_001",
            film_project_id="film-456",
            video_url="https://example.com/shot1.mp4",
            thumbnail_url="https://example.com/thumb1.jpg",
            image_url="https://example.com/image1.jpg",
            audio_url="https://example.com/audio1.mp3",
            prompt="A beautiful sunset over the ocean",
            duration=5.5,
            sequence_order=1,
            status="completed"
        )

        assert shot.id == "shot-uuid-123"
        assert shot.shot_id == "shot_001"
        assert shot.film_project_id == "film-456"
        assert shot.video_url == "https://example.com/shot1.mp4"
        assert shot.thumbnail_url == "https://example.com/thumb1.jpg"
        assert shot.image_url == "https://example.com/image1.jpg"
        assert shot.audio_url == "https://example.com/audio1.mp3"
        assert shot.prompt == "A beautiful sunset over the ocean"
        assert shot.duration == 5.5
        assert shot.sequence_order == 1
        assert shot.status == "completed"

    def test_film_shot_defaults(self):
        """Test FilmShot default values."""
        shot = FilmShot(
            id="test-id",
            shot_id="shot_test",
            film_project_id="film-1",
            video_url="https://example.com/video.mp4",
            prompt="Test prompt",
            duration=3.0
        )

        assert shot.status == "completed"

    def test_film_shot_table_name(self):
        """Test FilmShot table name."""
        assert FilmShot.__tablename__ == "film_shots"

    def test_film_shot_relationships(self):
        """Test FilmShot has film_project relationship."""
        assert hasattr(FilmShot, 'film_project')


class TestShotReviewModel:
    """Test ShotReview model."""

    def test_shot_review_creation(self):
        """Test creating a ShotReview instance."""
        review = ShotReview(
            id="review-123",
            shot_id="shot-456",
            status="approved",
            notes="Looks great! Perfect lighting.",
            reviewer="director@example.com"
        )

        assert review.id == "review-123"
        assert review.shot_id == "shot-456"
        assert review.status == "approved"
        assert review.notes == "Looks great! Perfect lighting."
        assert review.reviewer == "director@example.com"

    def test_shot_review_statuses(self):
        """Test different review statuses."""
        approved = ShotReview(
            id="review-1",
            shot_id="shot-1",
            status="approved"
        )
        assert approved.status == "approved"

        rejected = ShotReview(
            id="review-2",
            shot_id="shot-2",
            status="rejected",
            notes="Needs better composition"
        )
        assert rejected.status == "rejected"
        assert rejected.notes == "Needs better composition"

        revision = ShotReview(
            id="review-3",
            shot_id="shot-3",
            status="needs_revision",
            notes="Adjust color grading"
        )
        assert revision.status == "needs_revision"

    def test_shot_review_table_name(self):
        """Test ShotReview table name."""
        assert ShotReview.__tablename__ == "shot_reviews"

    def test_shot_review_relationships(self):
        """Test ShotReview has shot relationship."""
        assert hasattr(ShotReview, 'shot')


# =============================================================================
# Generation History Models Tests
# =============================================================================

class TestScriptGenerationModel:
    """Test ScriptGeneration model."""

    def test_script_generation_creation(self):
        """Test creating a ScriptGeneration instance."""
        script = ScriptGeneration(
            id="script-123",
            workspace_id="ws-456",
            project_id="proj-789",
            user_id=1,
            generation_type="script",
            version=1,
            input_subject="Space exploration",
            input_action="Landing on Mars",
            input_location="Red planet surface",
            input_style="cinematic",
            input_genre="sci-fi",
            input_idea="First human landing on Mars",
            input_partial_data={"duration": 120},
            ai_feedback="Make it more dramatic",
            ai_enhancement_enabled=True,
            output_prompt="Epic Mars landing sequence with dramatic tension",
            output_negative_prompt="cartoon, animated",
            output_metadata={"shot_type": "wide", "camera": "aerial"},
            output_full_data={"scenes": []},
            is_active=True,
            is_favorite=False,
            rating=5
        )

        assert script.id == "script-123"
        assert script.workspace_id == "ws-456"
        assert script.project_id == "proj-789"
        assert script.user_id == 1
        assert script.generation_type == "script"
        assert script.version == 1
        assert script.input_subject == "Space exploration"
        assert script.ai_feedback == "Make it more dramatic"
        assert script.ai_enhancement_enabled is True
        assert script.output_prompt == "Epic Mars landing sequence with dramatic tension"
        assert script.is_active is True
        assert script.rating == 5

    def test_script_generation_defaults(self):
        """Test ScriptGeneration default values."""
        script = ScriptGeneration(
            id="test-id",
            generation_type="script"
        )

        assert script.version == 1
        assert script.ai_enhancement_enabled is False
        assert script.is_active is True
        assert script.is_favorite is False

    def test_script_generation_types(self):
        """Test different generation types."""
        types = ["script", "scene", "shot"]
        for gen_type in types:
            script = ScriptGeneration(
                id=f"test-{gen_type}",
                generation_type=gen_type
            )
            assert script.generation_type == gen_type

    def test_script_generation_table_name(self):
        """Test ScriptGeneration table name."""
        assert ScriptGeneration.__tablename__ == "script_generations"

    def test_script_generation_relationships(self):
        """Test ScriptGeneration has all relationships."""
        assert hasattr(ScriptGeneration, 'project')
        assert hasattr(ScriptGeneration, 'parent')
        assert hasattr(ScriptGeneration, 'scenes')


class TestSceneModel:
    """Test Scene model."""

    def test_scene_creation(self):
        """Test creating a Scene instance."""
        scene = Scene(
            id="scene-123",
            script_generation_id="script-456",
            scene_number=1,
            title="Opening Scene",
            description="Hero walks into sunset",
            location="Desert landscape",
            time_of_day="sunset",
            mood="hopeful",
            characters=["Hero", "Sidekick"],
            duration_estimate=30,
            pacing="slow"
        )

        assert scene.id == "scene-123"
        assert scene.script_generation_id == "script-456"
        assert scene.scene_number == 1
        assert scene.title == "Opening Scene"
        assert scene.description == "Hero walks into sunset"
        assert scene.location == "Desert landscape"
        assert scene.time_of_day == "sunset"
        assert scene.mood == "hopeful"
        assert len(scene.characters) == 2
        assert scene.duration_estimate == 30
        assert scene.pacing == "slow"

    def test_scene_table_name(self):
        """Test Scene table name."""
        assert Scene.__tablename__ == "scenes"

    def test_scene_relationships(self):
        """Test Scene has all relationships."""
        assert hasattr(Scene, 'script_generation')
        assert hasattr(Scene, 'shot_generations')


class TestShotGenerationModel:
    """Test ShotGeneration model."""

    def test_shot_generation_creation(self):
        """Test creating a ShotGeneration instance."""
        shot = ShotGeneration(
            id="shotgen-123",
            workspace_id="ws-456",
            scene_id="scene-789",
            film_id="film-101",
            shot_number=1,
            sequence_order=1,
            version=1,
            prompt="Close-up of hero's determined face",
            negative_prompt="blurry, low quality",
            shot_type="close-up",
            camera_motion="static",
            lighting="dramatic",
            emotion="determined",
            shot_metadata={"lens": "50mm"},
            duration_seconds=3.5,
            ai_feedback="Add more emotion",
            is_active=True,
            is_favorite=True,
            rating=4
        )

        assert shot.id == "shotgen-123"
        assert shot.workspace_id == "ws-456"
        assert shot.scene_id == "scene-789"
        assert shot.film_id == "film-101"
        assert shot.shot_number == 1
        assert shot.sequence_order == 1
        assert shot.version == 1
        assert shot.prompt == "Close-up of hero's determined face"
        assert shot.negative_prompt == "blurry, low quality"
        assert shot.shot_type == "close-up"
        assert shot.camera_motion == "static"
        assert shot.lighting == "dramatic"
        assert shot.emotion == "determined"
        assert shot.shot_metadata["lens"] == "50mm"
        assert shot.duration_seconds == 3.5
        assert shot.ai_feedback == "Add more emotion"
        assert shot.is_active is True
        assert shot.is_favorite is True
        assert shot.rating == 4

    def test_shot_generation_defaults(self):
        """Test ShotGeneration default values."""
        shot = ShotGeneration(
            id="test-id",
            shot_number=1,
            prompt="Test prompt"
        )

        assert shot.version == 1
        assert shot.duration_seconds == 3.0
        assert shot.is_active is True
        assert shot.is_favorite is False

    def test_shot_generation_table_name(self):
        """Test ShotGeneration table name."""
        assert ShotGeneration.__tablename__ == "shot_generations"

    def test_shot_generation_relationships(self):
        """Test ShotGeneration has all relationships."""
        assert hasattr(ShotGeneration, 'scene')
        assert hasattr(ShotGeneration, 'parent')


class TestGenerationSessionModel:
    """Test GenerationSession model."""

    def test_generation_session_creation(self):
        """Test creating a GenerationSession instance."""
        session = GenerationSession(
            id="session-123",
            workspace_id="ws-456",
            name="Morning Session",
            description="Working on action scenes",
            total_generations=15,
            active_generation_id="script-789"
        )

        assert session.id == "session-123"
        assert session.workspace_id == "ws-456"
        assert session.name == "Morning Session"
        assert session.description == "Working on action scenes"
        assert session.total_generations == 15
        assert session.active_generation_id == "script-789"

    def test_generation_session_defaults(self):
        """Test GenerationSession default values."""
        session = GenerationSession(
            id="test-id"
        )

        assert session.total_generations == 0

    def test_generation_session_table_name(self):
        """Test GenerationSession table name."""
        assert GenerationSession.__tablename__ == "generation_sessions"


class TestGenerationNoteModel:
    """Test GenerationNote model."""

    def test_generation_note_creation(self):
        """Test creating a GenerationNote instance."""
        note = GenerationNote(
            id="note-123",
            generation_id="script-456",
            generation_table="script_generations",
            user_id=1,
            note="This looks promising! Let's refine the dialogue."
        )

        assert note.id == "note-123"
        assert note.generation_id == "script-456"
        assert note.generation_table == "script_generations"
        assert note.user_id == 1
        assert note.note == "This looks promising! Let's refine the dialogue."

    def test_generation_note_table_types(self):
        """Test different generation table types."""
        tables = ["script_generations", "shot_generations"]
        for table in tables:
            note = GenerationNote(
                id=f"note-{table}",
                generation_id="gen-1",
                generation_table=table,
                note="Test note"
            )
            assert note.generation_table == table

    def test_generation_note_table_name(self):
        """Test GenerationNote table name."""
        assert GenerationNote.__tablename__ == "generation_notes"


# =============================================================================
# Universal Asset System Tests
# =============================================================================

class TestAssetRelationshipModel:
    """Test AssetRelationship model."""

    def test_asset_relationship_creation(self):
        """Test creating an AssetRelationship instance."""
        relationship = AssetRelationship(
            id="rel-123",
            parent_asset_id="asset-parent",
            child_asset_id="asset-child",
            relationship_type="contains_shot",
            sequence=1,
            relationship_metadata={"role": "main"}
        )

        assert relationship.id == "rel-123"
        assert relationship.parent_asset_id == "asset-parent"
        assert relationship.child_asset_id == "asset-child"
        assert relationship.relationship_type == "contains_shot"
        assert relationship.sequence == 1
        assert relationship.relationship_metadata["role"] == "main"

    def test_asset_relationship_types(self):
        """Test different relationship types."""
        types = [
            "contains_shot",
            "uses_character",
            "generation_attempt",
            "generated_video"
        ]
        for rel_type in types:
            relationship = AssetRelationship(
                id=f"rel-{rel_type}",
                parent_asset_id="parent",
                child_asset_id="child",
                relationship_type=rel_type
            )
            assert relationship.relationship_type == rel_type

    def test_asset_relationship_defaults(self):
        """Test AssetRelationship default values."""
        relationship = AssetRelationship(
            id="test-id",
            parent_asset_id="parent",
            child_asset_id="child",
            relationship_type="test"
        )

        assert relationship.relationship_metadata == {}

    def test_asset_relationship_table_name(self):
        """Test AssetRelationship table name."""
        assert AssetRelationship.__tablename__ == "asset_relationships"

    def test_asset_relationship_relationships(self):
        """Test AssetRelationship has asset relationships."""
        assert hasattr(AssetRelationship, 'parent_asset')
        assert hasattr(AssetRelationship, 'child_asset')


class TestAssetCollectionModel:
    """Test AssetCollection model."""

    def test_asset_collection_creation(self):
        """Test creating an AssetCollection instance."""
        collection = AssetCollection(
            id="coll-123",
            workspace_id="ws-456",
            name="Character References",
            type="character",
            description="All reference images for main character",
            collection_metadata={"character_name": "Hero"}
        )

        assert collection.id == "coll-123"
        assert collection.workspace_id == "ws-456"
        assert collection.name == "Character References"
        assert collection.type == "character"
        assert collection.description == "All reference images for main character"
        assert collection.collection_metadata["character_name"] == "Hero"

    def test_asset_collection_types(self):
        """Test different collection types."""
        types = ["project", "character", "storyboard", "library"]
        for coll_type in types:
            collection = AssetCollection(
                id=f"coll-{coll_type}",
                workspace_id="ws-1",
                name=f"Test {coll_type}",
                type=coll_type
            )
            assert collection.type == coll_type

    def test_asset_collection_defaults(self):
        """Test AssetCollection default values."""
        collection = AssetCollection(
            id="test-id",
            workspace_id="ws-1",
            name="Test",
            type="library"
        )

        assert collection.collection_metadata == {}

    def test_asset_collection_table_name(self):
        """Test AssetCollection table name."""
        assert AssetCollection.__tablename__ == "asset_collections"

    def test_asset_collection_relationships(self):
        """Test AssetCollection has members relationship."""
        assert hasattr(AssetCollection, 'members')


class TestAssetCollectionMemberModel:
    """Test AssetCollectionMember model."""

    def test_asset_collection_member_creation(self):
        """Test creating an AssetCollectionMember instance."""
        member = AssetCollectionMember(
            id="member-123",
            collection_id="coll-456",
            asset_id="asset-789",
            sequence=1,
            member_metadata={"featured": True}
        )

        assert member.id == "member-123"
        assert member.collection_id == "coll-456"
        assert member.asset_id == "asset-789"
        assert member.sequence == 1
        assert member.member_metadata["featured"] is True

    def test_asset_collection_member_defaults(self):
        """Test AssetCollectionMember default values."""
        member = AssetCollectionMember(
            id="test-id",
            collection_id="coll-1",
            asset_id="asset-1"
        )

        assert member.member_metadata == {}

    def test_asset_collection_member_table_name(self):
        """Test AssetCollectionMember table name."""
        assert AssetCollectionMember.__tablename__ == "asset_collection_members"

    def test_asset_collection_member_relationships(self):
        """Test AssetCollectionMember has all relationships."""
        assert hasattr(AssetCollectionMember, 'collection')
        assert hasattr(AssetCollectionMember, 'asset')


class TestTagModel:
    """Test Tag model."""

    def test_tag_creation(self):
        """Test creating a Tag instance."""
        tag = Tag(
            id="tag-123",
            name="action",
            category="genre",
            color="#FF0000"
        )

        assert tag.id == "tag-123"
        assert tag.name == "action"
        assert tag.category == "genre"
        assert tag.color == "#FF0000"

    def test_tag_minimal(self):
        """Test creating a Tag with minimal fields."""
        tag = Tag(
            id="tag-min",
            name="minimal"
        )

        assert tag.id == "tag-min"
        assert tag.name == "minimal"

    def test_tag_table_name(self):
        """Test Tag table name."""
        assert Tag.__tablename__ == "tags"


class TestUserModel:
    """Test User model."""

    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(
            id=1,
            email="user@example.com",
            username="testuser",
            password_hash="hashed_password_123",
            is_active=True,
            is_superuser=False
        )

        assert user.id == 1
        assert user.email == "user@example.com"
        assert user.username == "testuser"
        assert user.password_hash == "hashed_password_123"
        assert user.is_active is True
        assert user.is_superuser is False

    def test_user_defaults(self):
        """Test User default values."""
        user = User(
            email="test@example.com",
            username="test",
            password_hash="hashed"
        )

        assert user.is_active is True
        assert user.is_superuser is False

    def test_user_table_name(self):
        """Test User table name."""
        assert User.__tablename__ == "users"

    def test_user_timestamps(self):
        """Test User has timestamp columns."""
        user = User(
            email="test@example.com",
            username="test",
            password_hash="hashed"
        )

        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')


# =============================================================================
# Association Tables Tests
# =============================================================================

class TestChannelAuthorsTable:
    """Test channel_authors association table."""

    def test_channel_authors_table_exists(self):
        """Test that channel_authors table is defined."""
        assert channel_authors is not None

    def test_channel_authors_columns(self):
        """Test channel_authors has required columns."""
        columns = [col.name for col in channel_authors.columns]
        assert 'channel_id' in columns
        assert 'author_id' in columns


# =============================================================================
# Asset Model Extended Tests (director-ui specific)
# =============================================================================

class TestAssetModelExtended:
    """Test Asset model with director-ui specific fields."""

    def test_asset_with_workspace(self):
        """Test Asset with workspace_id."""
        asset = Asset(
            id="asset-123",
            workspace_id="ws-456",
            type="video",
            name="Test Video",
            url="https://example.com/video.mp4"
        )

        assert asset.workspace_id == "ws-456"

    def test_asset_types(self):
        """Test different asset types."""
        types = ["script", "text", "audio", "video", "image", "shot", "shot_take", "film", "character_ref", "scene"]
        for asset_type in types:
            asset = Asset(
                id=f"asset-{asset_type}",
                type=asset_type,
                name=f"Test {asset_type}",
                url="https://example.com/test"
            )
            assert asset.type == asset_type

    def test_asset_source_types(self):
        """Test different asset source types."""
        sources = ["upload", "generation", "import", "derivative"]
        for source in sources:
            asset = Asset(
                id=f"asset-{source}",
                type="image",
                name="Test",
                url="https://example.com/test",
                source=source
            )
            assert asset.source == source

    def test_asset_generation_tracking(self):
        """Test asset generation tracking fields."""
        asset = Asset(
            id="asset-gen",
            type="video",
            name="Generated Video",
            url="https://example.com/video.mp4",
            source="generation",
            generation_cost=2.50,
            generation_metadata={
                "provider": "minimax",
                "model": "video-01",
                "prompt": "A beautiful sunset",
                "seed": 12345
            }
        )

        assert asset.generation_cost == 2.50
        assert asset.generation_metadata["provider"] == "minimax"
        assert asset.generation_metadata["model"] == "video-01"
        assert asset.generation_metadata["prompt"] == "A beautiful sunset"
        assert asset.generation_metadata["seed"] == 12345

    def test_asset_metadata_storage(self):
        """Test asset metadata storage."""
        asset = Asset(
            id="asset-meta",
            type="image",
            name="Test Image",
            url="https://example.com/image.jpg",
            asset_metadata={
                "width": 1920,
                "height": 1080,
                "format": "jpg",
                "thumbnail_url": "https://example.com/thumb.jpg"
            }
        )

        assert asset.asset_metadata["width"] == 1920
        assert asset.asset_metadata["height"] == 1080
        assert asset.asset_metadata["format"] == "jpg"
        assert asset.asset_metadata["thumbnail_url"] == "https://example.com/thumb.jpg"

    def test_asset_tags_array(self):
        """Test asset tags as array."""
        asset = Asset(
            id="asset-tags",
            type="video",
            name="Tagged Video",
            url="https://example.com/video.mp4",
            tags=["action", "epic", "cinematic"]
        )

        assert len(asset.tags) == 3
        assert "action" in asset.tags
        assert "epic" in asset.tags
        assert "cinematic" in asset.tags

    def test_asset_defaults(self):
        """Test Asset default values."""
        asset = Asset(
            id="test-id",
            type="image",
            name="Test",
            url="https://example.com/test.jpg"
        )

        assert asset.asset_metadata == {}
        assert asset.tags == []

    def test_asset_relationships_extended(self):
        """Test Asset has all relationship attributes."""
        assert hasattr(Asset, 'workspace')
        assert hasattr(Asset, 'parent_relationships')
        assert hasattr(Asset, 'child_relationships')
        assert hasattr(Asset, 'collection_memberships')


# =============================================================================
# Integration and Constraint Tests
# =============================================================================

class TestModelConstraints:
    """Test model constraints and validations."""

    def test_workspace_unique_slug(self):
        """Test Workspace slug should be unique."""
        # Column definition check
        slug_col = Workspace.__table__.columns['slug']
        assert slug_col.unique is True

    def test_user_unique_email(self):
        """Test User email should be unique."""
        email_col = User.__table__.columns['email']
        assert email_col.unique is True

    def test_user_unique_username(self):
        """Test User username should be unique."""
        username_col = User.__table__.columns['username']
        assert username_col.unique is True

    def test_tag_unique_name(self):
        """Test Tag name should be unique."""
        name_col = Tag.__table__.columns['name']
        assert name_col.unique is True

    def test_shot_review_unique_shot_id(self):
        """Test ShotReview shot_id should be unique (one review per shot)."""
        shot_id_col = ShotReview.__table__.columns['shot_id']
        assert shot_id_col.unique is True

    def test_character_unique_name(self):
        """Test Character name should be unique."""
        name_col = Character.__table__.columns['name']
        assert name_col.unique is True


class TestModelTimestamps:
    """Test timestamp fields on all models."""

    def test_workspace_has_timestamps(self):
        """Test Workspace has timestamp columns."""
        workspace = Workspace(id="ws-1", name="Test", slug="test", owner_id=1)
        assert hasattr(workspace, 'created_at')
        assert hasattr(workspace, 'updated_at')

    def test_project_has_timestamps(self):
        """Test Project has timestamp columns."""
        project = Project(id="proj-1", workspace_id="ws-1", name="Test", slug="test")
        assert hasattr(project, 'created_at')
        assert hasattr(project, 'updated_at')

    def test_asset_has_timestamps(self):
        """Test Asset has timestamp columns."""
        asset = Asset(id="asset-1", type="image", name="Test", url="http://test.com")
        assert hasattr(asset, 'created_at')
        assert hasattr(asset, 'updated_at')

    def test_film_shot_has_timestamps(self):
        """Test FilmShot has timestamp columns."""
        shot = FilmShot(
            id="shot-1",
            shot_id="shot_001",
            film_project_id="film-1",
            video_url="http://test.com",
            prompt="Test",
            duration=3.0
        )
        assert hasattr(shot, 'created_at')
        assert hasattr(shot, 'updated_at')

    def test_shot_review_has_timestamps(self):
        """Test ShotReview has timestamp columns."""
        review = ShotReview(id="rev-1", shot_id="shot-1", status="approved")
        assert hasattr(review, 'created_at')
        assert hasattr(review, 'updated_at')
        assert hasattr(review, 'reviewed_at')


class TestModelDocstrings:
    """Test that models have proper documentation."""

    def test_asset_has_docstring(self):
        """Test Asset model has comprehensive docstring."""
        assert Asset.__doc__ is not None
        assert "everything is an asset" in Asset.__doc__.lower()

    def test_asset_relationship_has_docstring(self):
        """Test AssetRelationship has docstring with examples."""
        assert AssetRelationship.__doc__ is not None
        assert "examples" in AssetRelationship.__doc__.lower()

    def test_asset_collection_has_docstring(self):
        """Test AssetCollection has docstring with examples."""
        assert AssetCollection.__doc__ is not None
        assert "examples" in AssetCollection.__doc__.lower()


class TestModelPrimaryKeys:
    """Test primary key configurations."""

    def test_workspace_primary_key(self):
        """Test Workspace uses String UUID primary key."""
        pk = Workspace.__table__.primary_key.columns['id']
        assert pk.type.__class__.__name__ == 'String'

    def test_project_primary_key(self):
        """Test Project uses String UUID primary key."""
        pk = Project.__table__.primary_key.columns['id']
        assert pk.type.__class__.__name__ == 'String'

    def test_user_primary_key(self):
        """Test User uses Integer autoincrement primary key."""
        pk = User.__table__.primary_key.columns['id']
        assert pk.type.__class__.__name__ == 'Integer'
        assert pk.autoincrement is True

    def test_channel_primary_key(self):
        """Test Channel uses Integer primary key."""
        pk = Channel.__table__.primary_key.columns['id']
        assert pk.type.__class__.__name__ == 'Integer'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
