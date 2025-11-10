"""add_characters_assets_film_presentations_tables

Revision ID: 85562a830bc1
Revises: 029bcafb7929
Create Date: 2025-11-06 15:49:49.404595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85562a830bc1'
down_revision: Union[str, None] = '029bcafb7929'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create characters table
    op.create_table(
        'characters',
        sa.Column('id', sa.String(36), nullable=False, comment='Character unique ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='Character name'),
        sa.Column('description', sa.Text(), nullable=True, comment='Character description'),
        sa.Column('reference_images', sa.JSON(), nullable=True, comment='Array of reference image URLs'),
        sa.Column('attributes', sa.JSON(), nullable=True, comment='Character physical attributes'),
        sa.Column('consistency_prompt', sa.Text(), nullable=True, comment='Generated AI consistency prompt'),
        sa.Column('projects_used', sa.JSON(), nullable=True, comment='Array of project IDs using this character'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),
        sa.PrimaryKeyConstraint('id', name='pk_characters'),
        sa.UniqueConstraint('name', name='uq_characters_name')
    )

    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.String(36), nullable=False, comment='Asset unique ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='Asset name/filename'),
        sa.Column('type', sa.String(50), nullable=False, comment='Asset type (image, video, audio)'),
        sa.Column('url', sa.String(1024), nullable=False, comment='Asset URL'),
        sa.Column('file_path', sa.String(1024), nullable=True, comment='Local file path'),
        sa.Column('size', sa.Integer(), nullable=True, comment='File size in bytes'),
        sa.Column('duration', sa.Float(), nullable=True, comment='Duration for video/audio assets'),
        sa.Column('thumbnail_url', sa.String(1024), nullable=True, comment='Thumbnail URL'),
        sa.Column('tags', sa.JSON(), nullable=True, comment='Array of tags'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='Additional metadata'),
        sa.Column('is_favorite', sa.Boolean(), server_default='false', nullable=False, comment='Favorite flag'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),
        sa.PrimaryKeyConstraint('id', name='pk_assets')
    )
    op.create_index('idx_assets_type', 'assets', ['type'])
    op.create_index('idx_assets_favorite', 'assets', ['is_favorite'])

    # Create film_projects table
    op.create_table(
        'film_projects',
        sa.Column('id', sa.String(255), nullable=False, comment='Film project unique ID'),
        sa.Column('title', sa.String(500), nullable=False, comment='Film title'),
        sa.Column('description', sa.Text(), nullable=True, comment='Film description'),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, comment='Project status'),
        sa.Column('shots_config', sa.JSON(), nullable=True, comment='Original shots configuration'),
        sa.Column('generated_shots', sa.JSON(), nullable=True, comment='Generated shot metadata'),
        sa.Column('video_provider', sa.String(50), nullable=True, comment='Video generation provider'),
        sa.Column('image_provider', sa.String(50), nullable=True, comment='Image generation provider'),
        sa.Column('audio_provider', sa.String(50), nullable=True, comment='Audio generation provider'),
        sa.Column('total_cost', sa.Float(), server_default='0.0', nullable=False, comment='Total generation cost'),
        sa.Column('budget_limit', sa.Float(), nullable=True, comment='Budget limit'),
        sa.Column('output_path', sa.String(1024), nullable=True, comment='Final video output path'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Completion timestamp'),
        sa.PrimaryKeyConstraint('id', name='pk_film_projects')
    )
    op.create_index('idx_film_projects_status', 'film_projects', ['status'])

    # Create presentations table
    op.create_table(
        'presentations',
        sa.Column('id', sa.String(255), nullable=False, comment='Presentation unique ID'),
        sa.Column('title', sa.String(500), nullable=False, comment='Presentation title'),
        sa.Column('topic', sa.String(500), nullable=False, comment='Presentation topic'),
        sa.Column('brief', sa.Text(), nullable=True, comment='Presentation brief'),
        sa.Column('content_source', sa.String(50), nullable=False, comment='Content source (ai, youtube, web, file)'),
        sa.Column('content_url', sa.String(1024), nullable=True, comment='Source URL or file path'),
        sa.Column('num_slides', sa.Integer(), server_default='10', nullable=False, comment='Number of slides'),
        sa.Column('tone', sa.String(50), server_default='professional', nullable=False, comment='Presentation tone'),
        sa.Column('target_audience', sa.String(255), nullable=True, comment='Target audience'),
        sa.Column('model', sa.String(50), server_default='gpt-4o-mini', nullable=False, comment='AI model used'),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, comment='Generation status'),
        sa.Column('outline', sa.JSON(), nullable=True, comment='Generated outline'),
        sa.Column('total_cost', sa.Float(), server_default='0.0', nullable=False, comment='Total generation cost'),
        sa.Column('budget_limit', sa.Float(), nullable=True, comment='Budget limit'),
        sa.Column('output_path', sa.String(1024), nullable=True, comment='Final PPTX output path'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Completion timestamp'),
        sa.PrimaryKeyConstraint('id', name='pk_presentations')
    )
    op.create_index('idx_presentations_status', 'presentations', ['status'])
    op.create_index('idx_presentations_content_source', 'presentations', ['content_source'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_index('idx_presentations_content_source', table_name='presentations')
    op.drop_index('idx_presentations_status', table_name='presentations')
    op.drop_table('presentations')

    op.drop_index('idx_film_projects_status', table_name='film_projects')
    op.drop_table('film_projects')

    op.drop_index('idx_assets_favorite', table_name='assets')
    op.drop_index('idx_assets_type', table_name='assets')
    op.drop_table('assets')

    op.drop_table('characters')
