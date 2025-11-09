"""Assets table definition for SQLAlchemy Core.

This module defines the assets table schema for media file tracking.
"""

from sqlalchemy import Table, Column, String, Integer, Float, Boolean, DateTime, JSON, Index
from sqlalchemy.sql import func

from .base import metadata

# Assets table definition
assets_table = Table(
    "assets",
    metadata,
    Column("id", String(36), primary_key=True, comment="Asset unique ID"),
    Column("name", String(255), nullable=False, comment="Asset name/filename"),
    Column("type", String(50), nullable=False, comment="Asset type (image, video, audio)"),
    Column("url", String(1024), nullable=False, comment="Asset URL"),
    Column("file_path", String(1024), nullable=True, comment="Local file path"),
    Column("size", Integer, nullable=True, comment="File size in bytes"),
    Column("duration", Float, nullable=True, comment="Duration for video/audio assets"),
    Column("thumbnail_url", String(1024), nullable=True, comment="Thumbnail URL"),
    Column("tags", JSON, nullable=True, comment="Array of tags"),
    Column("asset_metadata", JSON, nullable=True, comment="Additional metadata (dimensions, codec, etc.)"),
    Column("is_favorite", Boolean, nullable=False, default=False, server_default="false", comment="Favorite flag"),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
        comment="Creation timestamp",
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        default=func.current_timestamp(),
        server_default=func.current_timestamp(),
        comment="Last update timestamp",
    ),
)

# Index for faster type-based queries
assets_type_index = Index(
    "idx_assets_type",
    assets_table.c.type,
)

# Index for favorite filtering
assets_favorite_index = Index(
    "idx_assets_favorite",
    assets_table.c.is_favorite,
)
