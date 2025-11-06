"""Film projects table definition for SQLAlchemy Core.

This module defines the film_projects table schema for AI-generated film tracking.
"""

from sqlalchemy import Table, Column, String, Text, Float, DateTime, JSON, Index
from sqlalchemy.sql import func

from .base import metadata

# Film projects table definition
film_projects_table = Table(
    "film_projects",
    metadata,
    Column("id", String(255), primary_key=True, comment="Film project unique ID"),
    Column("title", String(500), nullable=False, comment="Film title"),
    Column("description", Text, nullable=True, comment="Film description"),
    Column("status", String(50), nullable=False, default="pending", server_default="pending", comment="Project status"),
    Column("shots_config", JSON, nullable=True, comment="Original shots configuration"),
    Column("generated_shots", JSON, nullable=True, comment="Generated shot metadata"),
    Column("video_provider", String(50), nullable=True, comment="Video generation provider"),
    Column("image_provider", String(50), nullable=True, comment="Image generation provider"),
    Column("audio_provider", String(50), nullable=True, comment="Audio generation provider"),
    Column("total_cost", Float, nullable=False, default=0.0, server_default="0.0", comment="Total generation cost"),
    Column("budget_limit", Float, nullable=True, comment="Budget limit"),
    Column("output_path", String(1024), nullable=True, comment="Final video output path"),
    Column("error_message", Text, nullable=True, comment="Error message if failed"),
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
    Column(
        "completed_at",
        DateTime(timezone=True),
        nullable=True,
        comment="Completion timestamp",
    ),
)

# Index for status-based queries
film_projects_status_index = Index(
    "idx_film_projects_status",
    film_projects_table.c.status,
)
