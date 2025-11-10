"""
Integration tests for model relationships and database constraints.

Tests relationships between models, cascade deletes, and database integrity.
Requires a test database connection.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data.models import (
    Base,
    Workspace,
    Project,
    Channel,
    Author,
    Character,
    Asset,
    FilmProject,
    FilmVariant,
    PublishHistory,
    ProjectAsset,
    ShotCharacter,
    channel_authors
)


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


# =============================================================================
# Workspace → Projects Relationship Tests
# =============================================================================

class TestWorkspaceProjectRelationship:
    """Test Workspace to Project relationships."""

    def test_workspace_can_have_multiple_projects(self, db_session):
        """Test that a workspace can have multiple projects."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test-workspace",
            owner_id=1
        )
        db_session.add(workspace)

        project1 = Project(
            id="proj-1",
            workspace_id="ws-1",
            name="Project 1",
            slug="project-1"
        )
        project2 = Project(
            id="proj-2",
            workspace_id="ws-1",
            name="Project 2",
            slug="project-2"
        )

        db_session.add_all([project1, project2])
        db_session.commit()

        # Query workspace and check projects
        ws = db_session.query(Workspace).filter_by(id="ws-1").first()
        assert ws is not None
        assert len(ws.projects) == 2

        project_names = {p.name for p in ws.projects}
        assert "Project 1" in project_names
        assert "Project 2" in project_names

    def test_workspace_cascade_delete_projects(self, db_session):
        """Test that deleting workspace cascades to projects."""
        workspace = Workspace(
            id="ws-cascade",
            name="Cascade Test",
            slug="cascade-test",
            owner_id=1
        )
        db_session.add(workspace)

        project = Project(
            id="proj-cascade",
            workspace_id="ws-cascade",
            name="Child Project",
            slug="child-project"
        )
        db_session.add(project)
        db_session.commit()

        # Verify project exists
        assert db_session.query(Project).filter_by(id="proj-cascade").first() is not None

        # Delete workspace
        db_session.delete(workspace)
        db_session.commit()

        # Verify project was also deleted
        assert db_session.query(Project).filter_by(id="proj-cascade").first() is None


# =============================================================================
# Project Hierarchy Tests
# =============================================================================

class TestProjectHierarchy:
    """Test Project parent-child relationships."""

    def test_project_can_have_parent(self, db_session):
        """Test that projects can have parent projects."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )
        db_session.add(workspace)

        parent_project = Project(
            id="proj-parent",
            workspace_id="ws-1",
            name="Parent Campaign",
            slug="parent-campaign",
            type="campaign"
        )

        child_project = Project(
            id="proj-child",
            workspace_id="ws-1",
            name="Child Series",
            slug="child-series",
            type="series",
            parent_project_id="proj-parent"
        )

        db_session.add_all([parent_project, child_project])
        db_session.commit()

        # Query and verify relationship
        child = db_session.query(Project).filter_by(id="proj-child").first()
        assert child.parent_project_id == "proj-parent"
        assert child.parent is not None
        assert child.parent.name == "Parent Campaign"

        # Check parent has children
        parent = db_session.query(Project).filter_by(id="proj-parent").first()
        assert len(parent.children) == 1
        assert parent.children[0].name == "Child Series"

    def test_project_hierarchy_cascade_delete(self, db_session):
        """Test that deleting parent cascades to children."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )
        db_session.add(workspace)

        parent = Project(
            id="proj-parent",
            workspace_id="ws-1",
            name="Parent",
            slug="parent"
        )

        child = Project(
            id="proj-child",
            workspace_id="ws-1",
            name="Child",
            slug="child",
            parent_project_id="proj-parent"
        )

        db_session.add_all([parent, child])
        db_session.commit()

        # Delete parent
        db_session.delete(parent)
        db_session.commit()

        # Verify child was also deleted
        assert db_session.query(Project).filter_by(id="proj-child").first() is None


# =============================================================================
# Channel ↔ Author Many-to-Many Tests
# =============================================================================

class TestChannelAuthorRelationship:
    """Test Channel and Author many-to-many relationship."""

    def test_channel_can_have_multiple_authors(self, db_session):
        """Test that a channel can have multiple authors."""
        channel = Channel(id=1, name="Philosophy Channel")
        author1 = Author(id=1, name="Plato")
        author2 = Author(id=2, name="Aristotle")

        db_session.add_all([channel, author1, author2])

        # Add authors to channel
        channel.authors.append(author1)
        channel.authors.append(author2)

        db_session.commit()

        # Query and verify
        ch = db_session.query(Channel).filter_by(id=1).first()
        assert len(ch.authors) == 2

        author_names = {a.name for a in ch.authors}
        assert "Plato" in author_names
        assert "Aristotle" in author_names

    def test_author_can_have_multiple_channels(self, db_session):
        """Test that an author can be associated with multiple channels."""
        author = Author(id=1, name="Einstein")
        channel1 = Channel(id=1, name="Physics Channel")
        channel2 = Channel(id=2, name="Science Channel")

        db_session.add_all([author, channel1, channel2])

        # Add channels to author
        author.channels.append(channel1)
        author.channels.append(channel2)

        db_session.commit()

        # Query and verify
        au = db_session.query(Author).filter_by(id=1).first()
        assert len(au.channels) == 2

        channel_names = {c.name for c in au.channels}
        assert "Physics Channel" in channel_names
        assert "Science Channel" in channel_names


# =============================================================================
# Character → Asset Relationship Tests
# =============================================================================

class TestCharacterAssetRelationship:
    """Test Character to Asset relationships."""

    def test_character_can_have_generated_assets(self, db_session):
        """Test that character can have multiple generated assets."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        character = Character(
            id="char-1",
            workspace_id="ws-1",
            name="Hero Character"
        )

        asset1 = Asset(
            id="asset-1",
            workspace_id="ws-1",
            name="Hero Portrait",
            type="image",
            url="https://example.com/hero1.jpg",
            character_id="char-1"
        )

        asset2 = Asset(
            id="asset-2",
            workspace_id="ws-1",
            name="Hero Full Body",
            type="image",
            url="https://example.com/hero2.jpg",
            character_id="char-1"
        )

        db_session.add_all([workspace, character, asset1, asset2])
        db_session.commit()

        # Query character and check assets
        char = db_session.query(Character).filter_by(id="char-1").first()
        assert char is not None
        assert len(char.generated_assets) == 2


# =============================================================================
# FilmProject → FilmVariant Relationship Tests
# =============================================================================

class TestFilmProjectVariantRelationship:
    """Test FilmProject to FilmVariant relationships."""

    def test_film_can_have_multiple_variants(self, db_session):
        """Test that a film can have multiple platform variants."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        film = FilmProject(
            id="film-1",
            workspace_id="ws-1",
            title="Base Film"
        )

        variant1 = FilmVariant(
            id="variant-1",
            film_project_id="film-1",
            platform="youtube",
            aspect_ratio="16:9",
            width=1920,
            height=1080
        )

        variant2 = FilmVariant(
            id="variant-2",
            film_project_id="film-1",
            platform="tiktok",
            aspect_ratio="9:16",
            width=1080,
            height=1920
        )

        db_session.add_all([workspace, film, variant1, variant2])
        db_session.commit()

        # Query film and check variants
        f = db_session.query(FilmProject).filter_by(id="film-1").first()
        assert f is not None
        assert len(f.platform_variants) == 2

        platforms = {v.platform for v in f.platform_variants}
        assert "youtube" in platforms
        assert "tiktok" in platforms

    def test_film_variant_cascade_delete(self, db_session):
        """Test that deleting film cascades to variants."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        film = FilmProject(
            id="film-1",
            workspace_id="ws-1",
            title="Test Film"
        )

        variant = FilmVariant(
            id="variant-1",
            film_project_id="film-1",
            platform="youtube",
            aspect_ratio="16:9",
            width=1920,
            height=1080
        )

        db_session.add_all([workspace, film, variant])
        db_session.commit()

        # Delete film
        db_session.delete(film)
        db_session.commit()

        # Verify variant was also deleted
        assert db_session.query(FilmVariant).filter_by(id="variant-1").first() is None


# =============================================================================
# FilmProject Base/Variant Relationship Tests
# =============================================================================

class TestFilmProjectBaseVariantRelationship:
    """Test FilmProject base film and variant relationships."""

    def test_film_can_have_base_film(self, db_session):
        """Test that a film variant can reference a base film."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        base_film = FilmProject(
            id="film-base",
            workspace_id="ws-1",
            title="Base Film"
        )

        variant_film = FilmProject(
            id="film-variant",
            workspace_id="ws-1",
            title="Platform Variant",
            base_film_id="film-base",
            variant_type="platform_variant"
        )

        db_session.add_all([workspace, base_film, variant_film])
        db_session.commit()

        # Query variant and check base
        variant = db_session.query(FilmProject).filter_by(id="film-variant").first()
        assert variant.base_film is not None
        assert variant.base_film.id == "film-base"

        # Query base and check variants
        base = db_session.query(FilmProject).filter_by(id="film-base").first()
        assert len(base.variants) == 1
        assert base.variants[0].id == "film-variant"


# =============================================================================
# PublishHistory → FilmVariant Relationship Tests
# =============================================================================

class TestPublishHistoryRelationship:
    """Test PublishHistory relationships."""

    def test_publish_history_links_to_variant_and_film(self, db_session):
        """Test that publish history links to both variant and film."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        film = FilmProject(
            id="film-1",
            workspace_id="ws-1",
            title="Test Film"
        )

        variant = FilmVariant(
            id="variant-1",
            film_project_id="film-1",
            platform="youtube",
            aspect_ratio="16:9",
            width=1920,
            height=1080
        )

        history = PublishHistory(
            id="pub-1",
            film_variant_id="variant-1",
            film_project_id="film-1",
            account_id="account-1",
            platform="youtube",
            published_at=datetime.now()
        )

        db_session.add_all([workspace, film, variant, history])
        db_session.commit()

        # Query history and verify relationships
        pub = db_session.query(PublishHistory).filter_by(id="pub-1").first()
        assert pub.film_variant is not None
        assert pub.film_variant.id == "variant-1"
        assert pub.film_project is not None
        assert pub.film_project.id == "film-1"

    def test_publish_history_survives_variant_deletion(self, db_session):
        """Test that publish history remains when variant is deleted (SET NULL)."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        film = FilmProject(
            id="film-1",
            workspace_id="ws-1",
            title="Test Film"
        )

        variant = FilmVariant(
            id="variant-1",
            film_project_id="film-1",
            platform="youtube",
            aspect_ratio="16:9",
            width=1920,
            height=1080
        )

        history = PublishHistory(
            id="pub-1",
            film_variant_id="variant-1",
            film_project_id="film-1",
            account_id="account-1",
            platform="youtube",
            published_at=datetime.now()
        )

        db_session.add_all([workspace, film, variant, history])
        db_session.commit()

        # Delete variant
        db_session.delete(variant)
        db_session.commit()

        # Verify history still exists with null variant_id
        pub = db_session.query(PublishHistory).filter_by(id="pub-1").first()
        assert pub is not None
        assert pub.film_variant_id is None  # Should be set to NULL
        assert pub.film_project_id == "film-1"  # Film reference intact


# =============================================================================
# ProjectAsset Association Tests
# =============================================================================

class TestProjectAssetAssociation:
    """Test ProjectAsset association table."""

    def test_project_can_have_multiple_assets_with_roles(self, db_session):
        """Test that projects can have multiple assets with different roles."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        project = Project(
            id="proj-1",
            workspace_id="ws-1",
            name="Test Project",
            slug="test-project"
        )

        asset1 = Asset(
            id="asset-1",
            workspace_id="ws-1",
            name="Source Image",
            type="image",
            url="https://example.com/source.jpg"
        )

        asset2 = Asset(
            id="asset-2",
            workspace_id="ws-1",
            name="Final Video",
            type="video",
            url="https://example.com/final.mp4"
        )

        pa1 = ProjectAsset(
            project_id="proj-1",
            asset_id="asset-1",
            role="source"
        )

        pa2 = ProjectAsset(
            project_id="proj-1",
            asset_id="asset-2",
            role="final"
        )

        db_session.add_all([workspace, project, asset1, asset2, pa1, pa2])
        db_session.commit()

        # Query project and check assets
        proj = db_session.query(Project).filter_by(id="proj-1").first()
        assert len(proj.assets) == 2

        # Check roles
        roles = {pa.role for pa in proj.assets}
        assert "source" in roles
        assert "final" in roles


# =============================================================================
# ShotCharacter Association Tests
# =============================================================================

class TestShotCharacterAssociation:
    """Test ShotCharacter association table."""

    def test_film_can_track_character_appearances(self, db_session):
        """Test that films can track which characters appear in which shots."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        film = FilmProject(
            id="film-1",
            workspace_id="ws-1",
            title="Test Film"
        )

        character = Character(
            id="char-1",
            workspace_id="ws-1",
            name="Hero"
        )

        sc1 = ShotCharacter(
            film_project_id="film-1",
            shot_id="shot-001",
            character_id="char-1",
            shot_index=1,
            prominence="primary",
            screen_time_seconds=10.5
        )

        sc2 = ShotCharacter(
            film_project_id="film-1",
            shot_id="shot-003",
            character_id="char-1",
            shot_index=3,
            prominence="secondary",
            screen_time_seconds=5.0
        )

        db_session.add_all([workspace, film, character, sc1, sc2])
        db_session.commit()

        # Query film and check character appearances
        f = db_session.query(FilmProject).filter_by(id="film-1").first()
        assert len(f.shot_characters) == 2

        # Query character and check appearances
        char = db_session.query(Character).filter_by(id="char-1").first()
        assert len(char.shot_appearances) == 2

        # Calculate total screen time
        total_screen_time = sum(sc.screen_time_seconds for sc in char.shot_appearances)
        assert total_screen_time == 15.5


# =============================================================================
# Asset Lineage Tests
# =============================================================================

class TestAssetLineage:
    """Test Asset lineage tracking."""

    def test_asset_can_have_source_asset(self, db_session):
        """Test that assets can track their source."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

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

        db_session.add_all([workspace, source_asset, derived_asset])
        db_session.commit()

        # Query derived and check source
        derived = db_session.query(Asset).filter_by(id="asset-derived").first()
        assert derived.source is not None
        assert derived.source.id == "asset-source"
        assert derived.source.name == "Source Image"

        # Query source and check derivatives
        source = db_session.query(Asset).filter_by(id="asset-source").first()
        assert len(source.derivatives) == 1
        assert source.derivatives[0].id == "asset-derived"


# =============================================================================
# Complex Query Tests
# =============================================================================

class TestComplexQueries:
    """Test complex queries across relationships."""

    def test_find_all_films_in_workspace(self, db_session):
        """Test querying all films in a workspace."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        project = Project(
            id="proj-1",
            workspace_id="ws-1",
            name="Test Project",
            slug="test"
        )

        film1 = FilmProject(
            id="film-1",
            workspace_id="ws-1",
            project_id="proj-1",
            title="Film 1"
        )

        film2 = FilmProject(
            id="film-2",
            workspace_id="ws-1",
            title="Film 2"
        )

        db_session.add_all([workspace, project, film1, film2])
        db_session.commit()

        # Query all films in workspace
        films = db_session.query(FilmProject).filter_by(workspace_id="ws-1").all()
        assert len(films) == 2

    def test_find_character_total_screen_time(self, db_session):
        """Test calculating total screen time for a character across films."""
        workspace = Workspace(
            id="ws-1",
            name="Test Workspace",
            slug="test",
            owner_id=1
        )

        character = Character(
            id="char-1",
            workspace_id="ws-1",
            name="Hero"
        )

        film1 = FilmProject(
            id="film-1",
            workspace_id="ws-1",
            title="Film 1"
        )

        film2 = FilmProject(
            id="film-2",
            workspace_id="ws-1",
            title="Film 2"
        )

        sc1 = ShotCharacter(
            film_project_id="film-1",
            shot_id="shot-1",
            character_id="char-1",
            shot_index=1,
            screen_time_seconds=10.0
        )

        sc2 = ShotCharacter(
            film_project_id="film-2",
            shot_id="shot-1",
            character_id="char-1",
            shot_index=1,
            screen_time_seconds=15.5
        )

        db_session.add_all([workspace, character, film1, film2, sc1, sc2])
        db_session.commit()

        # Query character and calculate total
        char = db_session.query(Character).filter_by(id="char-1").first()
        total_time = sum(sc.screen_time_seconds for sc in char.shot_appearances)
        assert total_time == 25.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
