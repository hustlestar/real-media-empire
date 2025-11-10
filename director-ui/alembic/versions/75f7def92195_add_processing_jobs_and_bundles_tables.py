"""add_processing_jobs_and_bundles_tables

Revision ID: 75f7def92195
Revises: bcfb3d41f357
Create Date: 2025-11-10 17:11:11.139884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '75f7def92195'
down_revision: Union[str, None] = 'bcfb3d41f357'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Detect database dialect
    conn = op.get_bind()
    is_postgresql = conn.dialect.name == 'postgresql'

    # Create enums for PostgreSQL
    if is_postgresql:
        # Create source_type_enum if it doesn't exist
        result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'source_type_enum'"))
        if not result.scalar():
            source_type_enum = postgresql.ENUM('pdf_url', 'pdf_file', 'youtube', 'web', name='source_type_enum', create_type=False)
            source_type_enum.create(conn, checkfirst=False)

        # Create processing_status_enum if it doesn't exist
        result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'processing_status_enum'"))
        if not result.scalar():
            processing_status_enum = postgresql.ENUM('pending', 'extracting', 'completed', 'failed', name='processing_status_enum', create_type=False)
            processing_status_enum.create(conn, checkfirst=False)

        # Create job_processing_type_enum if it doesn't exist
        result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'job_processing_type_enum'"))
        if not result.scalar():
            job_processing_type_enum = postgresql.ENUM('summary', 'mvp_plan', 'content_ideas', 'blog_post', name='job_processing_type_enum', create_type=False)
            job_processing_type_enum.create(conn, checkfirst=False)

        # Create job_status_enum if it doesn't exist
        result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'job_status_enum'"))
        if not result.scalar():
            job_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='job_status_enum', create_type=False)
            job_status_enum.create(conn, checkfirst=False)

    # ========================================================================
    # PROCESSING_JOBS TABLE
    # ========================================================================

    # Create processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(), server_default=sa.text('gen_random_uuid()') if is_postgresql else None, nullable=False, comment='Unique job ID'),
        sa.Column('content_id', sa.String(), nullable=True, comment='Reference to content item (nullable for bundle jobs) - String to match content_items.id'),
        sa.Column('processing_type', postgresql.ENUM('summary', 'mvp_plan', 'content_ideas', 'blog_post', name='job_processing_type_enum', create_type=False) if is_postgresql else sa.String(50), nullable=False, comment='Type of AI processing'),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='job_status_enum', create_type=False) if is_postgresql else sa.String(50), server_default='pending', nullable=False, comment='Job execution status'),
        sa.Column('result_path', sa.Text(), nullable=True, comment='Path to file containing AI processing result'),
        sa.Column('user_prompt', sa.Text(), nullable=True, comment='Custom user instructions for AI'),
        sa.Column('output_language', sa.String(length=10), server_default='en', nullable=False, comment='Output language for AI response'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if processing failed'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who requested this job'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='Job creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['content_id'], ['content_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for processing_jobs
    op.create_index('idx_processing_jobs_content_id', 'processing_jobs', ['content_id'], unique=False)
    op.create_index('idx_processing_jobs_user_id', 'processing_jobs', ['user_id'], unique=False)
    op.create_index('idx_processing_jobs_status', 'processing_jobs', ['status'], unique=False)
    op.create_index('idx_processing_jobs_created_at', 'processing_jobs', ['created_at'], postgresql_ops={'created_at': 'DESC'} if is_postgresql else None, unique=False)

    # ========================================================================
    # BUNDLES TABLES
    # ========================================================================

    # Create bundles table
    op.create_table(
        'bundles',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(), server_default=sa.text('gen_random_uuid()') if is_postgresql else None, nullable=False, comment='Unique bundle ID'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who created this bundle'),
        sa.Column('name', sa.String(length=255), nullable=True, comment='Optional bundle name'),
        sa.Column('content_ids', postgresql.ARRAY(sa.String()) if is_postgresql else sa.JSON(), nullable=False, comment='Array of content IDs in this bundle - String array to match content_items.id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='Bundle creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for bundles
    op.create_index('idx_bundles_user_id', 'bundles', ['user_id'], unique=False)
    op.create_index('idx_bundles_created_at', 'bundles', ['created_at'], postgresql_ops={'created_at': 'DESC'} if is_postgresql else None, unique=False)

    # Create bundle_attempts table
    op.create_table(
        'bundle_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(), server_default=sa.text('gen_random_uuid()') if is_postgresql else None, nullable=False, comment='Unique attempt ID'),
        sa.Column('bundle_id', postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(), nullable=False, comment='Reference to bundle'),
        sa.Column('attempt_number', sa.Integer(), nullable=False, comment='Sequential attempt number for this bundle'),
        sa.Column('processing_type', sa.String(length=50), nullable=False, comment='Type of AI processing (summary/mvp_plan/content_ideas)'),
        sa.Column('output_language', sa.String(length=10), nullable=False, comment='Output language for AI response'),
        sa.Column('system_prompt', sa.Text(), nullable=False, comment='Full system prompt used'),
        sa.Column('user_prompt', sa.Text(), nullable=True, comment='User prompt template used'),
        sa.Column('combined_content_preview', sa.Text(), nullable=True, comment='Preview of combined content (titles + lengths)'),
        sa.Column('custom_instructions', sa.Text(), nullable=True, comment='Custom user instructions'),
        sa.Column('result_path', sa.Text(), nullable=True, comment='Path to processing result file'),
        sa.Column('job_id', postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(), nullable=True, comment='Reference to processing job'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='Attempt creation timestamp'),
        sa.ForeignKeyConstraint(['bundle_id'], ['bundles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['processing_jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bundle_id', 'attempt_number', name='uq_bundle_attempt_number')
    )

    # Create indexes for bundle_attempts
    op.create_index('idx_bundle_attempts_bundle_id', 'bundle_attempts', ['bundle_id'], unique=False)
    op.create_index('idx_bundle_attempts_job_id', 'bundle_attempts', ['job_id'], unique=False)
    op.create_index('idx_bundle_attempts_created_at', 'bundle_attempts', ['created_at'], postgresql_ops={'created_at': 'DESC'} if is_postgresql else None, unique=False)

    # Add bundle-related columns to processing_jobs
    op.add_column('processing_jobs', sa.Column('bundle_id', postgresql.UUID(as_uuid=True) if is_postgresql else sa.String(), nullable=True, comment='Reference to bundle if job is from bundle'))
    op.add_column('processing_jobs', sa.Column('content_ids', postgresql.ARRAY(sa.String()) if is_postgresql else sa.JSON(), nullable=True, comment='Array of content IDs for bundle jobs - String array to match content_items.id'))

    # Create foreign key constraint and index for bundle_id
    op.create_foreign_key('fk_processing_jobs_bundle_id', 'processing_jobs', 'bundles', ['bundle_id'], ['id'], ondelete='CASCADE')
    op.create_index('idx_processing_jobs_bundle_id', 'processing_jobs', ['bundle_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    # Drop bundle_id column and index from processing_jobs
    op.drop_index('idx_processing_jobs_bundle_id', table_name='processing_jobs')
    op.drop_constraint('fk_processing_jobs_bundle_id', 'processing_jobs', type_='foreignkey')
    op.drop_column('processing_jobs', 'content_ids')
    op.drop_column('processing_jobs', 'bundle_id')

    # Drop indexes for bundle_attempts
    op.drop_index('idx_bundle_attempts_created_at', table_name='bundle_attempts')
    op.drop_index('idx_bundle_attempts_job_id', table_name='bundle_attempts')
    op.drop_index('idx_bundle_attempts_bundle_id', table_name='bundle_attempts')

    # Drop indexes for bundles
    op.drop_index('idx_bundles_created_at', table_name='bundles')
    op.drop_index('idx_bundles_user_id', table_name='bundles')

    # Drop tables
    op.drop_table('bundle_attempts')
    op.drop_table('bundles')

    # Drop indexes for processing_jobs
    op.drop_index('idx_processing_jobs_created_at', table_name='processing_jobs')
    op.drop_index('idx_processing_jobs_status', table_name='processing_jobs')
    op.drop_index('idx_processing_jobs_user_id', table_name='processing_jobs')
    op.drop_index('idx_processing_jobs_content_id', table_name='processing_jobs')

    # Drop processing_jobs table
    op.drop_table('processing_jobs')

    # Drop enums (if PostgreSQL)
    conn = op.get_bind()
    if conn.dialect.name == 'postgresql':
        sa.Enum(name='job_status_enum').drop(op.get_bind(), checkfirst=True)
        sa.Enum(name='job_processing_type_enum').drop(op.get_bind(), checkfirst=True)
        sa.Enum(name='processing_status_enum').drop(op.get_bind(), checkfirst=True)
        sa.Enum(name='source_type_enum').drop(op.get_bind(), checkfirst=True)
