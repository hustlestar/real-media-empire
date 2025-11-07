from sqlalchemy import Column, Integer, String, Table, ForeignKey, Text, JSON, DateTime, Float, Boolean
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


class Character(Base):
    """Character model for visual consistency tracking."""
    __tablename__ = "characters"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    reference_images = Column(JSON)  # Array of image URLs
    attributes = Column(JSON)  # Character attributes (age, gender, ethnicity, etc.)
    consistency_prompt = Column(Text)  # Generated prompt for AI consistency
    projects_used = Column(JSON)  # Array of project IDs where character is used
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Asset(Base):
    """Asset model for media file tracking."""
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FilmProject(Base):
    """Film project model for tracking AI-generated films."""
    __tablename__ = "film_projects"

    id = Column(String, primary_key=True)  # film_id
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


class AvatarVideo(Base):
    """HeyGen avatar video generation tracking."""
    __tablename__ = "avatar_videos"

    id = Column(String, primary_key=True)  # UUID
    video_id = Column(String, unique=True, nullable=False)  # HeyGen video_id
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
    metadata = Column(JSON)  # Additional HeyGen metadata

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
