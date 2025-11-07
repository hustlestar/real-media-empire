from sqlalchemy import Column, Integer, String, Table, ForeignKey, Text, JSON, DateTime, Float, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

channel_authors = Table(
    "channel_authors", Base.metadata, Column("channel_id", Integer, ForeignKey("channels.id")), Column("author_id", Integer, ForeignKey("authors.id"))
)


# ============================================================================
# Workspace & Project Models (Multi-tenancy and Organization)
# ============================================================================

class Workspace(Base):
    """Workspace model for multi-tenant content isolation.

    A workspace represents a brand, client, or organization.
    All content (films, characters, assets) is scoped to a workspace.
    """
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    owner_id = Column(Integer, nullable=False)  # User who owns this workspace
    storage_quota_gb = Column(Integer, default=100)
    monthly_budget_usd = Column(Float, default=1000.0)
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    film_projects = relationship("FilmProject", back_populates="workspace")
    characters = relationship("Character", back_populates="workspace")
    assets = relationship("Asset", back_populates="workspace")

    def __repr__(self):
        return f"<Workspace(id={self.id}, name={self.name}, slug={self.slug})>"


class Project(Base):
    """Project model for hierarchical content organization.

    Projects can be nested (e.g., Campaign → Series → Episodes).
    All film projects belong to a project for organization.
    """
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    type = Column(String(50), default="campaign")  # 'campaign', 'brand', 'series', 'folder'
    parent_project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    status = Column(String(50), default="active")
    description = Column(Text)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    parent = relationship("Project", remote_side="Project.id", backref="children")
    film_projects = relationship("FilmProject", back_populates="project")
    assets = relationship("ProjectAsset", back_populates="project")

    __table_args__ = (
        Index('idx_projects_workspace', 'workspace_id'),
        Index('idx_projects_parent', 'parent_project_id'),
        Index('idx_projects_type', 'type'),
    )

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, type={self.type})>"


# ============================================================================
# Original Models (YouTube Channel Management)
# ============================================================================

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    authors = relationship("Author", secondary=channel_authors, back_populates="channels")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    channels = relationship("Channel", secondary=channel_authors, back_populates="authors")


class Character(Base):
    """Character model for visual consistency tracking.

    Characters are reusable across multiple films within a workspace.
    Visual consistency is maintained through reference images and AI prompts.
    """
    __tablename__ = "characters"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    reference_images = Column(JSON)  # Array of image URLs
    attributes = Column(JSON)  # Character attributes (age, gender, ethnicity, etc.)
    consistency_prompt = Column(Text)  # Generated prompt for AI consistency
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="characters")
    shot_appearances = relationship("ShotCharacter", back_populates="character")

    __table_args__ = (
        Index('idx_characters_workspace', 'workspace_id'),
        # Unique constraint: name must be unique within workspace
        # (different workspaces can have characters with same name)
    )


class Asset(Base):
    """Asset model for media file tracking.

    Assets can be source files or generated content.
    Lineage tracking enables tracing transformations (image → video → final).
    """
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # image, video, audio
    url = Column(String, nullable=False)
    file_path = Column(String)  # Local file path
    size = Column(Integer)  # File size in bytes
    duration = Column(Float, nullable=True)  # For video/audio assets
    thumbnail_url = Column(String, nullable=True)
    tags = Column(JSON)  # Array of tags
    asset_metadata = Column(JSON)  # Additional metadata (dimensions, codec, etc.)
    is_favorite = Column(Boolean, default=False)

    # Asset lifecycle management
    source_asset_id = Column(String, ForeignKey("assets.id"), nullable=True)  # Lineage tracking
    generation_params = Column(JSON)  # Parameters used to generate this asset
    cache_key = Column(String(255))  # For content-addressed caching
    expires_at = Column(DateTime, nullable=True)  # Cache TTL
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="assets")
    source = relationship("Asset", remote_side="Asset.id", backref="derivatives")
    project_associations = relationship("ProjectAsset", back_populates="asset")

    __table_args__ = (
        Index('idx_assets_workspace', 'workspace_id'),
        Index('idx_assets_type', 'type'),
        Index('idx_assets_source', 'source_asset_id'),
        Index('idx_assets_cache_key', 'cache_key'),
        Index('idx_assets_expires_at', 'expires_at'),
    )


class FilmProject(Base):
    """Film project model for tracking AI-generated films.

    Each film belongs to a workspace and optionally a project for organization.
    Supports platform variants and publishing tracking.
    """
    __tablename__ = "film_projects"

    id = Column(String, primary_key=True)  # film_id
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="pending")  # pending, processing, completed, failed

    # Generation configuration
    shots_config = Column(JSON)  # Original shots configuration
    generated_shots = Column(JSON)  # Generated shot metadata
    video_provider = Column(String)  # minimax, kling, runway
    image_provider = Column(String)  # fal, replicate
    audio_provider = Column(String)  # openai, elevenlabs

    # Cost tracking
    total_cost = Column(Float, default=0.0)
    budget_limit = Column(Float)

    # Output
    output_path = Column(String)  # Final video path (base version)
    base_film_id = Column(String, ForeignKey("film_projects.id"), nullable=True)  # For variants
    variant_type = Column(String(50), nullable=True)  # NULL = base, or 'platform_variant'

    # Publishing tracking
    published_at = Column(DateTime, nullable=True)
    published_platforms = Column(JSON, default=[])  # List of platforms published to

    # Metadata
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="film_projects")
    project = relationship("Project", back_populates="film_projects")
    base_film = relationship("FilmProject", remote_side="FilmProject.id", backref="variants")
    platform_variants = relationship("FilmVariant", back_populates="film_project")
    publish_history = relationship("PublishHistory", back_populates="film_project")
    shot_characters = relationship("ShotCharacter", back_populates="film_project")

    __table_args__ = (
        Index('idx_film_projects_workspace', 'workspace_id'),
        Index('idx_film_projects_project', 'project_id'),
        Index('idx_film_projects_status', 'status'),
        Index('idx_film_projects_base', 'base_film_id'),
    )


class Presentation(Base):
    """Presentation model for tracking AI-generated PowerPoint presentations."""
    __tablename__ = "presentations"

    id = Column(String, primary_key=True)  # presentation_id
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    brief = Column(Text)
    content_source = Column(String, nullable=False)  # ai, youtube, web, file
    content_url = Column(String, nullable=True)  # YouTube/web URL or file path
    num_slides = Column(Integer, default=10)
    tone = Column(String, default="professional")
    target_audience = Column(String)
    model = Column(String, default="gpt-4o-mini")
    status = Column(String, default="pending")  # pending, processing, completed, failed
    outline = Column(JSON)  # Generated outline
    total_cost = Column(Float, default=0.0)
    budget_limit = Column(Float)
    output_path = Column(String)  # Final PPTX path
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


# ============================================================================
# Platform Variants & Publishing Models
# ============================================================================

class FilmVariant(Base):
    """Platform-specific film variant model.

    Enables generating different aspect ratios and configurations for each platform.
    Example: One base film → YouTube (16:9), TikTok (9:16), Instagram (1:1)
    """
    __tablename__ = "film_variants"

    id = Column(String, primary_key=True)
    film_project_id = Column(String, ForeignKey("film_projects.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)  # youtube, tiktok, instagram_reels, instagram_feed
    aspect_ratio = Column(String(10), nullable=False)  # 16:9, 9:16, 1:1
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    max_duration_seconds = Column(Integer)
    output_path = Column(String(1024))
    status = Column(String(50), default="pending")
    generation_config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    film_project = relationship("FilmProject", back_populates="platform_variants")
    publish_records = relationship("PublishHistory", back_populates="film_variant")

    __table_args__ = (
        Index('idx_film_variants_project', 'film_project_id'),
        Index('idx_film_variants_platform', 'platform'),
    )


class PublishHistory(Base):
    """Publishing history model tracking where films were published.

    Creates audit trail of all publications with platform-specific metadata.
    Enables answering: "Where was this film published?" and "What metrics did it get?"
    """
    __tablename__ = "publish_history"

    id = Column(String, primary_key=True)
    film_variant_id = Column(String, ForeignKey("film_variants.id", ondelete="SET NULL"), nullable=True)
    film_project_id = Column(String, ForeignKey("film_projects.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String, nullable=False)
    platform = Column(String(50), nullable=False)
    platform_post_id = Column(String(255))  # External ID from platform API
    post_url = Column(String(1024))
    title = Column(String(500))
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)
    status = Column(String(50), default="published")
    metrics = Column(JSON, default={})  # views, likes, shares, comments
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    film_variant = relationship("FilmVariant", back_populates="publish_records")
    film_project = relationship("FilmProject", back_populates="publish_history")

    __table_args__ = (
        Index('idx_publish_history_variant', 'film_variant_id'),
        Index('idx_publish_history_project', 'film_project_id'),
        Index('idx_publish_history_platform', 'platform'),
        Index('idx_publish_history_published_at', 'published_at'),
    )


# ============================================================================
# Relationship Tables
# ============================================================================

class ProjectAsset(Base):
    """Project-Asset association table with role tracking.

    Enables tracking which assets belong to which projects and their role
    (source material, generated content, intermediate, final output).
    """
    __tablename__ = "project_assets"

    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(50), nullable=False, primary_key=True)  # source, generated, intermediate, final
    used_in_shots = Column(JSON, default=[])  # Array of shot IDs where this asset appears
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="assets")
    asset = relationship("Asset", back_populates="project_associations")

    __table_args__ = (
        Index('idx_project_assets_project', 'project_id'),
        Index('idx_project_assets_asset', 'asset_id'),
    )


class ShotCharacter(Base):
    """Shot-Character association tracking which characters appear in which shots.

    Enables querying: "Show me all shots featuring Character X"
    and "Which characters appear in this film?"
    """
    __tablename__ = "shot_characters"

    film_project_id = Column(String, ForeignKey("film_projects.id", ondelete="CASCADE"), primary_key=True)
    shot_id = Column(String, primary_key=True)
    character_id = Column(String, ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True)
    shot_index = Column(Integer, nullable=False)  # Order in film
    prominence = Column(String(50), default="primary")  # primary, secondary, background
    screen_time_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    film_project = relationship("FilmProject", back_populates="shot_characters")
    character = relationship("Character", back_populates="shot_appearances")

    __table_args__ = (
        Index('idx_shot_characters_film', 'film_project_id'),
        Index('idx_shot_characters_character', 'character_id'),
        Index('idx_shot_characters_shot', 'shot_id'),
    )
