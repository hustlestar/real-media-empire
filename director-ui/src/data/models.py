from sqlalchemy import Column, Integer, String, Table, ForeignKey, Text, JSON, DateTime, Float, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

channel_authors = Table(
    "channel_authors", Base.metadata, Column("channel_id", Integer, ForeignKey("channels.id")), Column("author_id", Integer, ForeignKey("authors.id"))
)


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


class Workspace(Base):
    """Workspace model for multi-tenant organization."""
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True)  # UUID
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    owner_id = Column(Integer, nullable=False)
    storage_quota_gb = Column(Integer, default=100)
    monthly_budget_usd = Column(Float, default=1000.0)
    description = Column(Text, nullable=True)  # Workspace description
    settings = Column(JSON, default=dict)  # Workspace settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    film_projects = relationship("FilmProject", back_populates="workspace")
    characters = relationship("Character", back_populates="workspace")
    assets = relationship("Asset", back_populates="workspace")


class Project(Base):
    """Project model for organizing work within workspaces."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)  # UUID
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    type = Column(String, default="campaign")  # campaign, brand, series, folder
    parent_project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    status = Column(String, default="active")  # active, archived, deleted
    description = Column(Text, nullable=True)
    project_metadata = Column(JSON, default=dict)  # Project metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    films = relationship("FilmProject", back_populates="project")


class Character(Base):
    """Character model for visual consistency tracking."""
    __tablename__ = "characters"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    reference_images = Column(JSON)  # Array of image URLs
    attributes = Column(JSON)  # Character attributes (age, gender, ethnicity, etc.)
    consistency_prompt = Column(Text)  # Generated prompt for AI consistency
    projects_used = Column(JSON)  # Array of project IDs where character is used
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="characters")
    # Note: Character → Asset relationships now use asset_relationships table


class Asset(Base):
    """Universal asset model - everything is an asset.

    ⚠️  CRITICAL DESIGN PRINCIPLE: This model MUST remain generic, common, and NOT LEAKY!

    🚫 NEVER add relationship-specific foreign keys (e.g., character_id, film_id)
    🚫 NEVER add type-specific columns (e.g., thumbnail_url, is_favorite)
    ✅ ALWAYS use metadata JSONB for type-specific data
    ✅ ALWAYS use asset_relationships table for connections between assets

    Asset types: script, text, audio, video, image, shot, shot_take, film, character_ref, scene

    This model stores ALL content with a minimal universal schema:
    - Core fields: id, workspace_id, type, name
    - Storage: url, file_path, size, duration
    - Flexible: metadata (JSONB), tags (array)
    - Tracking: source, generation_cost, generation_metadata

    Type-specific data goes in metadata:
    - image: {width, height, format, thumbnail_url}
    - shot: {shot_number, description, camera_angle, duration_target, prompt}
    - shot_take: {attempt_number, selected, generation_params, quality_score}
    - character_ref: {description, attributes, consistency_prompt}

    Relationships use asset_relationships table:
    - Film → Shot: parent=film, child=shot, type='contains_shot'
    - Shot → Character: parent=shot, child=character, type='uses_character'
    - Shot → Take: parent=shot, child=take, type='generation_attempt'
    - Take → Video: parent=take, child=video, type='generated_video'

    This design enables:
    ✅ Universal reusability across projects
    ✅ Flexible schema evolution without migrations
    ✅ Clear separation of concerns
    ✅ Type safety through metadata validation
    ✅ Graph-based relationships
    """
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)

    # Core universal fields
    type = Column(String(50), nullable=False)  # Asset type
    name = Column(String(255), nullable=False)

    # Storage
    url = Column(Text, nullable=True)  # Public CDN URL
    file_path = Column(Text, nullable=True)  # Local filesystem path
    size = Column(BigInteger, nullable=True)  # File size in bytes (BigInteger for files >2GB)
    duration = Column(Float, nullable=True)  # Duration for audio/video (seconds)

    # Flexible metadata (type-specific data stored as JSONB)
    asset_metadata = Column(JSON, nullable=False, default=dict)  # Type-specific metadata
    tags = Column(ARRAY(String), nullable=False, default=list)  # Asset tags array

    # Generation tracking
    source = Column(String(50), nullable=True)  # Source: upload, generation, import, derivative
    generation_cost = Column(Float, nullable=True)  # Cost to generate this asset
    generation_metadata = Column(JSON, nullable=True)  # Provider, model, prompt, seed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="assets")
    # Note: Character relationships now use asset_relationships table
    parent_relationships = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.parent_asset_id",
        back_populates="parent_asset",
        cascade="all, delete-orphan"
    )
    child_relationships = relationship(
        "AssetRelationship",
        foreign_keys="AssetRelationship.child_asset_id",
        back_populates="child_asset",
        cascade="all, delete-orphan"
    )
    collection_memberships = relationship(
        "AssetCollectionMember",
        back_populates="asset",
        cascade="all, delete-orphan"
    )


class FilmProject(Base):
    """Film project model for tracking AI-generated films.

    Each film belongs to a workspace and optionally a project for organization.
    Supports platform variants and publishing tracking.
    """
    __tablename__ = "film_projects"

    id = Column(String, primary_key=True)  # film_id
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    shots_config = Column(JSON)  # Original shots configuration
    generated_shots = Column(JSON)  # Generated shot metadata
    video_provider = Column(String)  # minimax, kling, runway
    image_provider = Column(String)  # fal, replicate
    audio_provider = Column(String)  # openai, elevenlabs
    total_cost = Column(Float, default=0.0)
    budget_limit = Column(Float)
    output_path = Column(String)  # Final video path
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="film_projects")
    project = relationship("Project", back_populates="films")


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
    provider = Column(String, nullable=False, default="openai")  # openai, anthropic, etc.
    model = Column(String, default="gpt-4o-mini")  # Model name
    status = Column(String, default="pending")  # pending, processing, completed, failed
    outline = Column(JSON)  # Generated outline
    total_cost = Column(Float, default=0.0)
    budget_limit = Column(Float)
    output_path = Column(String)  # Final PPTX path
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class AvatarVideo(Base):
    """Avatar video generation tracking (HeyGen, Veed.io, etc.)."""
    __tablename__ = "avatar_videos"

    id = Column(String, primary_key=True)  # UUID
    provider = Column(String, nullable=False, default="heygen")  # heygen, veed, etc.
    video_id = Column(String, unique=True, nullable=False)  # Provider's video_id
    title = Column(String)
    script = Column(Text, nullable=False)
    avatar_id = Column(String, nullable=False)
    avatar_name = Column(String)
    voice_id = Column(String, nullable=False)
    voice_name = Column(String)

    # Configuration
    aspect_ratio = Column(String, default="9:16")  # 9:16, 16:9, 1:1, 4:5
    background_type = Column(String, default="color")  # color, image, video
    background_value = Column(String, default="#000000")
    voice_speed = Column(Float, default=1.1)
    voice_pitch = Column(Integer, default=50)
    voice_emotion = Column(String, default="Excited")
    avatar_scale = Column(Float, default=1.0)
    has_green_screen = Column(Boolean, default=False)
    avatar_offset_x = Column(Float, default=0.0)
    avatar_offset_y = Column(Float, default=0.0)
    caption = Column(Boolean, default=False)
    test = Column(Boolean, default=False)

    # Generation results
    status = Column(String, default="pending")  # pending, processing, completed, failed
    video_url = Column(String)
    duration = Column(Float)  # Video duration in seconds
    cost = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    provider_metadata = Column(JSON)  # Provider-specific metadata (HeyGen, Veed.io, etc.)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class SocialAccount(Base):
    """Social media platform account configuration."""
    __tablename__ = "social_accounts"

    id = Column(String, primary_key=True)  # UUID
    platform = Column(String, nullable=False)  # tiktok, youtube, instagram, facebook, twitter, linkedin
    account_name = Column(String, nullable=False)
    account_handle = Column(String)  # @username or channel ID

    # Authentication (encrypted in production)
    credentials = Column(JSON)  # Platform-specific credentials
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime, nullable=True)

    # Account settings
    is_active = Column(Boolean, default=True)
    default_settings = Column(JSON)  # Platform-specific default post settings
    posting_schedule = Column(JSON)  # Scheduled posting times

    # Metadata
    platform_user_id = Column(String)  # Platform's user/channel ID
    follower_count = Column(Integer, default=0)
    last_sync_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PublishingPost(Base):
    """Published or scheduled social media post."""
    __tablename__ = "publishing_posts"

    id = Column(String, primary_key=True)  # UUID
    social_account_id = Column(String, ForeignKey("social_accounts.id"), nullable=False)

    # Content
    content_type = Column(String, nullable=False)  # video, image, text, carousel
    content_url = Column(String)  # URL to video/image asset
    caption = Column(Text)
    hashtags = Column(JSON)  # Array of hashtags

    # Scheduling
    status = Column(String, default="draft")  # draft, scheduled, publishing, published, failed
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    # Platform-specific settings
    platform = Column(String, nullable=False)
    platform_settings = Column(JSON)  # Platform-specific options (privacy, location, etc.)

    # Publishing results
    platform_post_id = Column(String, nullable=True)  # Post ID from platform
    platform_url = Column(String, nullable=True)  # Direct link to post
    error_message = Column(Text, nullable=True)

    # Source tracking
    source_id = Column(String, nullable=True)  # ID of source content (film_id, presentation_id, avatar_video_id)
    source_type = Column(String, nullable=True)  # film, presentation, avatar_video

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    social_account = relationship("SocialAccount", backref="posts")


class PublishingAnalytics(Base):
    """Analytics data for published posts."""
    __tablename__ = "publishing_analytics"

    id = Column(String, primary_key=True)  # UUID
    post_id = Column(String, ForeignKey("publishing_posts.id"), nullable=False)

    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)

    # Performance metrics
    engagement_rate = Column(Float, default=0.0)  # (likes + comments + shares) / views
    watch_time = Column(Float, default=0.0)  # Total watch time in seconds
    avg_watch_time = Column(Float, default=0.0)  # Average watch time per view
    completion_rate = Column(Float, default=0.0)  # % of viewers who watched to end

    # Audience insights
    audience_demographics = Column(JSON)  # Age, gender, location data
    traffic_sources = Column(JSON)  # Where views came from

    # Timestamps
    fetched_at = Column(DateTime, default=datetime.utcnow)  # When metrics were last fetched
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    post = relationship("PublishingPost", backref="analytics")


class FilmShot(Base):
    """Individual shot within a film project."""
    __tablename__ = "film_shots"

    id = Column(String, primary_key=True)  # UUID
    shot_id = Column(String, nullable=False)  # Shot identifier (e.g., "shot_001")
    film_project_id = Column(String, ForeignKey("film_projects.id"), nullable=False)

    # Generated content URLs
    video_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)  # Source image for video generation
    audio_url = Column(String, nullable=True)  # Audio track for the shot

    # Shot configuration
    prompt = Column(Text, nullable=False)
    duration = Column(Float, nullable=False)  # Duration in seconds
    sequence_order = Column(Integer, nullable=True)  # Order in the final film

    # Status tracking
    status = Column(String, default="completed")  # completed, approved, rejected, needs_revision, generating, pending

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    film_project = relationship("FilmProject", backref="shots")


class ShotReview(Base):
    """Review and feedback for a film shot."""
    __tablename__ = "shot_reviews"

    id = Column(String, primary_key=True)  # UUID
    shot_id = Column(String, ForeignKey("film_shots.id"), nullable=False, unique=True)

    # Review details
    status = Column(String, nullable=False)  # approved, rejected, needs_revision
    notes = Column(Text, nullable=True)  # Director's feedback and notes
    reviewer = Column(String, nullable=True)  # Username or email of reviewer

    # Timestamps
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    shot = relationship("FilmShot", backref="review", uselist=False)


# ============================================================================
# Generation History Models - Version Control for AI Creation
# ============================================================================


class ScriptGeneration(Base):
    """Script/Scene/Shot generation with version control and AI refinement."""
    __tablename__ = "script_generations"

    id = Column(String, primary_key=True)  # UUID
    workspace_id = Column(String, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    user_id = Column(Integer, nullable=True)

    # Generation metadata
    generation_type = Column(String(50), nullable=False)  # 'script', 'scene', 'shot'
    version = Column(Integer, nullable=False, default=1)
    parent_id = Column(String, ForeignKey("script_generations.id"), nullable=True)

    # Input data (what user provided)
    input_subject = Column(Text, nullable=True)
    input_action = Column(Text, nullable=True)
    input_location = Column(Text, nullable=True)
    input_style = Column(String(100), nullable=True)
    input_genre = Column(String(100), nullable=True)
    input_idea = Column(Text, nullable=True)  # For script generation from idea
    input_partial_data = Column(JSON, nullable=True)  # Any additional user inputs

    # AI refinement feedback
    ai_feedback = Column(Text, nullable=True)  # User's refinement instructions
    ai_enhancement_enabled = Column(Boolean, default=False)

    # Generated output
    output_prompt = Column(Text, nullable=True)
    output_negative_prompt = Column(Text, nullable=True)
    output_metadata = Column(JSON, nullable=True)  # Style, shot type, etc.
    output_full_data = Column(JSON, nullable=True)  # Complete generation result

    # Status and user preferences
    is_active = Column(Boolean, default=True)  # Current working version
    is_favorite = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", backref="script_generations")
    parent = relationship("ScriptGeneration", remote_side=[id], backref="children")
    scenes = relationship("Scene", back_populates="script_generation", cascade="all, delete-orphan")


class Scene(Base):
    """Scene within a script generation."""
    __tablename__ = "scenes"

    id = Column(String, primary_key=True)  # UUID
    script_generation_id = Column(String, ForeignKey("script_generations.id"), nullable=False)

    # Scene details
    scene_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    time_of_day = Column(String(50), nullable=True)
    mood = Column(String(100), nullable=True)
    characters = Column(JSON, nullable=True)  # Array of character names/refs

    # Scene metadata
    duration_estimate = Column(Integer, nullable=True)  # in seconds
    pacing = Column(String(50), nullable=True)  # slow, medium, fast, action

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    script_generation = relationship("ScriptGeneration", back_populates="scenes")
    shot_generations = relationship("ShotGeneration", back_populates="scene", cascade="all, delete-orphan")


class ShotGeneration(Base):
    """Shot generation with version control and AI refinement."""
    __tablename__ = "shot_generations"

    id = Column(String, primary_key=True)  # UUID
    workspace_id = Column(String, nullable=True, index=True)  # Workspace organization
    scene_id = Column(String, ForeignKey("scenes.id"), nullable=True)  # Nullable for standalone shots
    film_id = Column(String, nullable=True, index=True)  # Film/project association

    # Shot identification and sequencing
    shot_number = Column(Integer, nullable=False)
    sequence_order = Column(Integer, nullable=True, index=True)  # For storyboard ordering
    version = Column(Integer, nullable=False, default=1)
    parent_id = Column(String, ForeignKey("shot_generations.id"), nullable=True)

    # Shot configuration
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    shot_type = Column(String(100), nullable=True)
    camera_motion = Column(String(100), nullable=True)
    lighting = Column(String(100), nullable=True)
    emotion = Column(String(100), nullable=True)

    # Shot metadata
    shot_metadata = Column(JSON, nullable=True)
    duration_seconds = Column(Float, default=3.0)

    # AI feedback for regeneration
    ai_feedback = Column(Text, nullable=True)

    # Status and user preferences
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scene = relationship("Scene", back_populates="shot_generations")
    parent = relationship("ShotGeneration", remote_side=[id], backref="children")


class GenerationSession(Base):
    """Session for grouping related generation work."""
    __tablename__ = "generation_sessions"

    id = Column(String, primary_key=True)  # UUID
    workspace_id = Column(String, nullable=True)
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)

    # Session metadata
    total_generations = Column(Integer, default=0)
    active_generation_id = Column(String, ForeignKey("script_generations.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GenerationNote(Base):
    """Comments and notes on generations for collaboration."""
    __tablename__ = "generation_notes"

    id = Column(String, primary_key=True)  # UUID
    generation_id = Column(String, nullable=False)  # ID of script_generation or shot_generation
    generation_table = Column(String(50), nullable=False)  # 'script_generations' or 'shot_generations'

    user_id = Column(Integer, nullable=True)
    note = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# Universal Asset System - Relationships & Collections
# ============================================================================


class AssetRelationship(Base):
    """Universal asset relationships - defines how assets connect.

    Examples:
    - Film (parent) → Shot (child): relationship_type='contains_shot', sequence=1
    - Shot (parent) → Character (child): relationship_type='uses_character'
    - Shot (parent) → Take (child): relationship_type='generation_attempt', sequence=1
    - Take (parent) → Video (child): relationship_type='generated_video'
    """
    __tablename__ = "asset_relationships"

    id = Column(String, primary_key=True)
    parent_asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    child_asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)

    relationship_type = Column(String(50), nullable=False)  # contains_shot, uses_character, generation_attempt, etc.
    sequence = Column(Integer, nullable=True)  # Order when relationship implies sequence
    relationship_metadata = Column(JSON, nullable=False, default=dict)  # Relationship-specific data

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent_asset = relationship(
        "Asset",
        foreign_keys=[parent_asset_id],
        back_populates="parent_relationships"
    )
    child_asset = relationship(
        "Asset",
        foreign_keys=[child_asset_id],
        back_populates="child_relationships"
    )


class AssetCollection(Base):
    """Asset collections for grouping and organization.

    Examples:
    - type='project': A film project containing all related assets
    - type='character': Character definition with reference images
    - type='storyboard': Collection of shots in sequence
    - type='library': Reusable asset library (music, sound effects, etc.)
    """
    __tablename__ = "asset_collections"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # project, character, storyboard, library
    description = Column(Text, nullable=True)
    collection_metadata = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship(
        "AssetCollectionMember",
        back_populates="collection",
        cascade="all, delete-orphan"
    )


class AssetCollectionMember(Base):
    """Membership relationship between assets and collections."""
    __tablename__ = "asset_collection_members"

    id = Column(String, primary_key=True)
    collection_id = Column(String, ForeignKey("asset_collections.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)

    sequence = Column(Integer, nullable=True)  # Order within collection
    member_metadata = Column(JSON, nullable=False, default=dict)  # Member-specific data

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    collection = relationship(
        "AssetCollection",
        back_populates="members"
    )
    asset = relationship(
        "Asset",
        back_populates="collection_memberships"
    )


class Tag(Base):
    """Universal tags for assets and content."""
    __tablename__ = "tags"

    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(50), nullable=True)  # Optional tag category
    color = Column(String(7), nullable=True)  # Hex color for UI

    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
