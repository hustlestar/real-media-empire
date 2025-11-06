"""Database models for the Telegram bot template.

This module contains SQLAlchemy Core table definitions used by Alembic
for database migrations. The actual database operations continue to use
asyncpg for performance and simplicity.
"""

from .base import metadata
from .users import users_table
from .content import (
    content_items_table,
    processing_jobs_table,
    SourceType,
    ProcessingStatus,
    JobProcessingType,
    JobStatus,
)
from .characters import characters_table
from .assets import assets_table
from .film_projects import film_projects_table
from .presentations import presentations_table

__all__ = [
    "metadata",
    "users_table",
    "content_items_table",
    "processing_jobs_table",
    "SourceType",
    "ProcessingStatus",
    "JobProcessingType",
    "JobStatus",
    "characters_table",
    "assets_table",
    "film_projects_table",
    "presentations_table",
]
