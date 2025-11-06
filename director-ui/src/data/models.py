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
