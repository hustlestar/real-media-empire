"""add bundles and bundle_attempts tables

Revision ID: d4ec806d55f4
Revises: 3814148912bf
Create Date: 2025-10-01 12:30:01.789250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd4ec806d55f4'
down_revision: Union[str, None] = '3814148912bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create bundles table
    op.create_table(
        'bundles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique bundle ID'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='User who created this bundle'),
        sa.Column('name', sa.String(length=255), nullable=True, comment='Optional bundle name'),
        sa.Column('content_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False, comment='Array of content IDs in this bundle'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Bundle creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for bundles
    op.create_index('idx_bundles_user_id', 'bundles', ['user_id'], unique=False)
    op.create_index('idx_bundles_created_at', 'bundles', [sa.text('created_at DESC')], unique=False)

    # Create bundle_attempts table
    op.create_table(
        'bundle_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique attempt ID'),
        sa.Column('bundle_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to bundle'),
        sa.Column('attempt_number', sa.Integer(), nullable=False, comment='Sequential attempt number for this bundle'),
        sa.Column('processing_type', sa.String(length=50), nullable=False, comment='Type of AI processing (summary/mvp_plan/content_ideas)'),
        sa.Column('output_language', sa.String(length=10), nullable=False, comment='Output language for AI response'),
        sa.Column('system_prompt', sa.Text(), nullable=False, comment='Full system prompt used'),
        sa.Column('user_prompt', sa.Text(), nullable=True, comment='User prompt template used'),
        sa.Column('combined_content_preview', sa.Text(), nullable=True, comment='Preview of combined content (titles + lengths)'),
        sa.Column('custom_instructions', sa.Text(), nullable=True, comment='Custom user instructions'),
        sa.Column('result_path', sa.Text(), nullable=True, comment='Path to processing result file'),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Reference to processing job'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False, comment='Attempt creation timestamp'),
        sa.ForeignKeyConstraint(['bundle_id'], ['bundles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['processing_jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bundle_id', 'attempt_number', name='uq_bundle_attempt_number')
    )

    # Create indexes for bundle_attempts
    op.create_index('idx_bundle_attempts_bundle_id', 'bundle_attempts', ['bundle_id'], unique=False)
    op.create_index('idx_bundle_attempts_job_id', 'bundle_attempts', ['job_id'], unique=False)
    op.create_index('idx_bundle_attempts_created_at', 'bundle_attempts', [sa.text('created_at DESC')], unique=False)

    # Add bundle-related columns to processing_jobs
    op.add_column('processing_jobs', sa.Column('bundle_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Reference to bundle if job is from bundle'))
    op.add_column('processing_jobs', sa.Column('content_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True, comment='Array of content IDs for bundle jobs'))

    # Create foreign key constraint for bundle_id
    op.create_foreign_key('fk_processing_jobs_bundle_id', 'processing_jobs', 'bundles', ['bundle_id'], ['id'], ondelete='CASCADE')

    # Create index on bundle_id
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
