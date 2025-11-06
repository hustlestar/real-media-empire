"""Tag models for content categorization."""

from sqlalchemy import Table, Column, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import metadata


# Tags table
tags_table = Table(
    "tags",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), comment="Unique tag ID"),
    Column("name", Text, nullable=False, unique=True, comment="Tag name"),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Tag creation timestamp"
    ),
)

# Index for tag name
tags_name_index = Index("idx_tags_name", tags_table.c.name, unique=True)


# Content tags junction table
content_tags_table = Table(
    "content_tags",
    metadata,
    Column(
        "content_id",
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to content item"
    ),
    Column(
        "tag_id",
        UUID(as_uuid=True),
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to tag"
    ),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Tag assignment timestamp"
    ),
)

# Composite primary key
content_tags_table.append_constraint(
    content_tags_table.primary_key
)

# Indexes for content_tags
content_tags_content_index = Index("idx_content_tags_content_id", content_tags_table.c.content_id)
content_tags_tag_index = Index("idx_content_tags_tag_id", content_tags_table.c.tag_id)
