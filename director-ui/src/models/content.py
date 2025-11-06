"""Content items and processing jobs table definitions."""

from sqlalchemy import Table, Column, String, Text, BigInteger, DateTime, Enum, Index, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import enum

from .base import metadata


class SourceType(str, enum.Enum):
    """Content source types."""
    PDF_URL = "pdf_url"
    PDF_FILE = "pdf_file"
    YOUTUBE = "youtube"
    WEB = "web"


class ProcessingStatus(str, enum.Enum):
    """Content processing status."""
    PENDING = "pending"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"


class JobProcessingType(str, enum.Enum):
    """AI processing job types."""
    SUMMARY = "summary"
    MVP_PLAN = "mvp_plan"
    CONTENT_IDEAS = "content_ideas"
    BLOG_POST = "blog_post"


class JobStatus(str, enum.Enum):
    """Processing job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Language(str, enum.Enum):
    """Supported languages for content detection."""
    EN = "en"
    RU = "ru"
    ES = "es"


# Content items table
content_items_table = Table(
    "content_items",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), comment="Unique content ID"),
    Column("content_hash", String(64), nullable=False, unique=True, comment="SHA256 hash of content for deduplication"),
    Column(
        "source_type",
        Enum(SourceType, name="source_type_enum", create_type=True),
        nullable=False,
        comment="Type of content source"
    ),
    Column("source_url", Text, nullable=True, comment="Original URL if from URL source"),
    Column("file_reference", Text, nullable=True, comment="Path to uploaded file"),
    Column("extracted_text_path", Text, nullable=False, comment="Path to file containing extracted text"),
    Column("metadata", JSONB, nullable=False, server_default="{}", comment="Content metadata (title, duration, word_count, etc.)"),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="User who created this content"),
    Column(
        "processing_status",
        Enum(ProcessingStatus, name="processing_status_enum", create_type=True),
        nullable=False,
        server_default=ProcessingStatus.PENDING.value,
        comment="Content extraction status"
    ),
    Column("error_message", Text, nullable=True, comment="Error message if extraction failed"),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Content creation timestamp"
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="Last update timestamp"
    ),
)

# Indexes for content_items
content_items_hash_index = Index("idx_content_items_hash", content_items_table.c.content_hash, unique=True)
content_items_user_index = Index("idx_content_items_user_id", content_items_table.c.user_id)
content_items_status_index = Index("idx_content_items_status", content_items_table.c.processing_status)
content_items_created_index = Index("idx_content_items_created_at", content_items_table.c.created_at.desc())


# Processing jobs table
processing_jobs_table = Table(
    "processing_jobs",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), comment="Unique job ID"),
    Column(
        "content_id",
        UUID(as_uuid=True),
        ForeignKey("content_items.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to content item"
    ),
    Column(
        "processing_type",
        Enum(JobProcessingType, name="job_processing_type_enum", create_type=True),
        nullable=False,
        comment="Type of AI processing"
    ),
    Column(
        "status",
        Enum(JobStatus, name="job_status_enum", create_type=True),
        nullable=False,
        server_default=JobStatus.PENDING.value,
        comment="Job execution status"
    ),
    Column("result_path", Text, nullable=True, comment="Path to file containing AI processing result"),
    Column("user_prompt", Text, nullable=True, comment="Custom user instructions for AI"),
    Column("output_language", String(10), nullable=False, server_default="en", comment="Output language for AI response"),
    Column("error_message", Text, nullable=True, comment="Error message if processing failed"),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, comment="User who requested this job"),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Job creation timestamp"
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="Last update timestamp"
    ),
)

# Indexes for processing_jobs
processing_jobs_content_index = Index("idx_processing_jobs_content_id", processing_jobs_table.c.content_id)
processing_jobs_user_index = Index("idx_processing_jobs_user_id", processing_jobs_table.c.user_id)
processing_jobs_status_index = Index("idx_processing_jobs_status", processing_jobs_table.c.status)
processing_jobs_created_index = Index("idx_processing_jobs_created_at", processing_jobs_table.c.created_at.desc())