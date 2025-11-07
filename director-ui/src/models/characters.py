"""Characters table definition for SQLAlchemy Core.

This module defines the characters table schema for character consistency tracking.
"""

from sqlalchemy import Table, Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func

from .base import metadata

# Characters table definition
characters_table = Table(
    "characters",
    metadata,
    Column("id", String(36), primary_key=True, comment="Character unique ID"),
    Column("name", String(255), nullable=False, unique=True, comment="Character name"),
    Column("description", Text, nullable=True, comment="Character description"),
    Column("reference_images", JSON, nullable=True, comment="Array of reference image URLs"),
    Column("attributes", JSON, nullable=True, comment="Character physical attributes"),
    Column("consistency_prompt", Text, nullable=True, comment="Generated AI consistency prompt"),
    Column("projects_used", JSON, nullable=True, comment="Array of project IDs using this character"),
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
