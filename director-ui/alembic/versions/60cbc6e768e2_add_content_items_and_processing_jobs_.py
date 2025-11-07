"""add content_items and processing_jobs tables

Revision ID: 60cbc6e768e2
Revises: 001
Create Date: 2025-09-30 13:29:33.677407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '60cbc6e768e2'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enums (skip if already exist)
    conn = op.get_bind()

    # Check and create source_type_enum
    result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'source_type_enum'"))
    if not result.scalar():
        source_type_enum = postgresql.ENUM('pdf_url', 'pdf_file', 'youtube', 'web', name='source_type_enum', create_type=False)
        source_type_enum.create(conn, checkfirst=False)

    # Check and create processing_status_enum
    result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'processing_status_enum'"))
    if not result.scalar():
        processing_status_enum = postgresql.ENUM('pending', 'extracting', 'completed', 'failed', name='processing_status_enum', create_type=False)
        processing_status_enum.create(conn, checkfirst=False)

    # Check and create job_processing_type_enum
    result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'job_processing_type_enum'"))
    if not result.scalar():
        job_processing_type_enum = postgresql.ENUM('summary', 'mvp_plan', 'content_ideas', name='job_processing_type_enum', create_type=False)
        job_processing_type_enum.create(conn, checkfirst=False)

    # Check and create job_status_enum
    result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'job_status_enum'"))
    if not result.scalar():
        job_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='job_status_enum', create_type=False)
        job_status_enum.create(conn, checkfirst=False)

    # Create content_items table
    op.create_table(
        'content_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique content ID'),
        sa.Column('content_hash', sa.String(length=64), nullable=False, comment='SHA256 hash of content for deduplication'),
        sa.Column('source_type', postgresql.ENUM('pdf_url', 'pdf_file', 'youtube', 'web', name='source_type_enum', create_type=False), nullable=False, comment='Type of content source'),
        sa.Column('source_url', sa.Text(), nullable=True, comment='Original URL if from URL source'),
        sa.Column('file_reference', sa.Text(), nullable=True, comment='Path to uploaded file'),
        sa.Column('extracted_text_path', sa.Text(), nullable=False, comment='Path to file containing extracted text'),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False, comment='Content metadata'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who created this content'),
        sa.Column('processing_status', postgresql.ENUM('pending', 'extracting', 'completed', 'failed', name='processing_status_enum', create_type=False), server_default='pending', nullable=False, comment='Content extraction status'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if extraction failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Content creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash')
    )

    # Create indexes for content_items
    op.create_index('idx_content_items_hash', 'content_items', ['content_hash'], unique=True)
    op.create_index('idx_content_items_user_id', 'content_items', ['user_id'], unique=False)
    op.create_index('idx_content_items_status', 'content_items', ['processing_status'], unique=False)
    op.create_index('idx_content_items_created_at', 'content_items', [sa.text('created_at DESC')], unique=False)

    # Create processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique job ID'),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to content item'),
        sa.Column('processing_type', postgresql.ENUM('summary', 'mvp_plan', 'content_ideas', name='job_processing_type_enum', create_type=False), nullable=False, comment='Type of AI processing'),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='job_status_enum', create_type=False), server_default='pending', nullable=False, comment='Job execution status'),
        sa.Column('result_path', sa.Text(), nullable=True, comment='Path to file containing AI processing result'),
        sa.Column('user_prompt', sa.Text(), nullable=True, comment='Custom user instructions for AI'),
        sa.Column('output_language', sa.String(length=10), server_default='en', nullable=False, comment='Output language for AI response'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if processing failed'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who requested this job'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Job creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['content_id'], ['content_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for processing_jobs
    op.create_index('idx_processing_jobs_content_id', 'processing_jobs', ['content_id'], unique=False)
    op.create_index('idx_processing_jobs_user_id', 'processing_jobs', ['user_id'], unique=False)
    op.create_index('idx_processing_jobs_status', 'processing_jobs', ['status'], unique=False)
    op.create_index('idx_processing_jobs_created_at', 'processing_jobs', [sa.text('created_at DESC')], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_processing_jobs_created_at', table_name='processing_jobs')
    op.drop_index('idx_processing_jobs_status', table_name='processing_jobs')
    op.drop_index('idx_processing_jobs_user_id', table_name='processing_jobs')
    op.drop_index('idx_processing_jobs_content_id', table_name='processing_jobs')

    op.drop_index('idx_content_items_created_at', table_name='content_items')
    op.drop_index('idx_content_items_status', table_name='content_items')
    op.drop_index('idx_content_items_user_id', table_name='content_items')
    op.drop_index('idx_content_items_hash', table_name='content_items')

    # Drop tables
    op.drop_table('processing_jobs')
    op.drop_table('content_items')

    # Drop enums
    sa.Enum(name='job_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='job_processing_type_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='processing_status_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='source_type_enum').drop(op.get_bind(), checkfirst=True)
