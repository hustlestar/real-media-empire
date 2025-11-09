"""Presentations table definition for SQLAlchemy Core.

This module defines the presentations table schema for AI-generated PowerPoint tracking.
"""

from sqlalchemy import Table, Column, String, Text, Integer, Float, DateTime, JSON, Index
from sqlalchemy.sql import func

from .base import metadata

# Presentations table definition
presentations_table = Table(
    "presentations",
    metadata,
    Column("id", String(255), primary_key=True, comment="Presentation unique ID"),
    Column("title", String(500), nullable=False, comment="Presentation title"),
    Column("topic", String(500), nullable=False, comment="Presentation topic"),
    Column("brief", Text, nullable=True, comment="Presentation brief"),
    Column("content_source", String(50), nullable=False, comment="Content source (ai, youtube, web, file)"),
    Column("content_url", String(1024), nullable=True, comment="Source URL or file path"),
    Column("num_slides", Integer, nullable=False, default=10, server_default="10", comment="Number of slides"),
    Column("tone", String(50), nullable=False, default="professional", server_default="professional", comment="Presentation tone"),
    Column("target_audience", String(255), nullable=True, comment="Target audience"),
    Column("provider", String(50), nullable=False, default="openai", server_default="openai", comment="AI provider (openai, anthropic, etc.)"),
    Column("model", String(50), nullable=False, default="gpt-4o-mini", server_default="gpt-4o-mini", comment="AI model name"),
    Column("status", String(50), nullable=False, default="pending", server_default="pending", comment="Generation status"),
    Column("outline", JSON, nullable=True, comment="Generated outline"),
    Column("total_cost", Float, nullable=False, default=0.0, server_default="0.0", comment="Total generation cost"),
    Column("budget_limit", Float, nullable=True, comment="Budget limit"),
    Column("output_path", String(1024), nullable=True, comment="Final PPTX output path"),
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
presentations_status_index = Index(
    "idx_presentations_status",
    presentations_table.c.status,
)

# Index for content source filtering
presentations_source_index = Index(
    "idx_presentations_content_source",
    presentations_table.c.content_source,
)
