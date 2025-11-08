"""add_generation_history_tables

Revision ID: d059a51015a2
Revises: a7194f3d0364
Create Date: 2025-11-08 20:04:56.798188

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd059a51015a2'
down_revision: Union[str, None] = 'a7194f3d0364'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add generation history tables for version control."""

    # Create script_generations table (main version control table)
    op.create_table(
        'script_generations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),

        # Generation metadata
        sa.Column('generation_type', sa.String(50), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_id', sa.String(), nullable=True),

        # Input data (what user provided)
        sa.Column('input_subject', sa.Text(), nullable=True),
        sa.Column('input_action', sa.Text(), nullable=True),
        sa.Column('input_location', sa.Text(), nullable=True),
        sa.Column('input_style', sa.String(100), nullable=True),
        sa.Column('input_genre', sa.String(100), nullable=True),
        sa.Column('input_idea', sa.Text(), nullable=True),
        sa.Column('input_partial_data', sa.JSON(), nullable=True),

        # AI refinement feedback
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('ai_enhancement_enabled', sa.Boolean(), nullable=True, server_default='0'),

        # Generated output
        sa.Column('output_prompt', sa.Text(), nullable=True),
        sa.Column('output_negative_prompt', sa.Text(), nullable=True),
        sa.Column('output_metadata', sa.JSON(), nullable=True),
        sa.Column('output_full_data', sa.JSON(), nullable=True),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('rating', sa.Integer(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['script_generations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.CheckConstraint("generation_type IN ('script', 'scene', 'shot')", name='check_generation_type'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating'),
        sa.UniqueConstraint('project_id', 'generation_type', 'version', name='unique_project_generation_version')
    )

    # Create indexes for script_generations
    op.create_index('idx_script_generations_project', 'script_generations', ['project_id'])
    op.create_index('idx_script_generations_active', 'script_generations', ['is_active'])
    op.create_index('idx_script_generations_created', 'script_generations', ['created_at'])

    # Create scenes table
    op.create_table(
        'scenes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('script_generation_id', sa.String(), nullable=False),

        # Scene details
        sa.Column('scene_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('time_of_day', sa.String(50), nullable=True),
        sa.Column('mood', sa.String(100), nullable=True),
        sa.Column('characters', sa.JSON(), nullable=True),

        # Scene metadata
        sa.Column('duration_estimate', sa.Integer(), nullable=True),  # in seconds
        sa.Column('pacing', sa.String(50), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['script_generation_id'], ['script_generations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("pacing IN ('slow', 'medium', 'fast', 'action')", name='check_pacing'),
        sa.UniqueConstraint('script_generation_id', 'scene_number', name='unique_script_scene_number')
    )

    # Create indexes for scenes
    op.create_index('idx_scenes_script', 'scenes', ['script_generation_id'])

    # Create shot_generations table (shot version control)
    op.create_table(
        'shot_generations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scene_id', sa.String(), nullable=False),

        # Shot identification
        sa.Column('shot_number', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_id', sa.String(), nullable=True),

        # Shot configuration
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('negative_prompt', sa.Text(), nullable=True),
        sa.Column('shot_type', sa.String(100), nullable=True),
        sa.Column('camera_motion', sa.String(100), nullable=True),
        sa.Column('lighting', sa.String(100), nullable=True),
        sa.Column('emotion', sa.String(100), nullable=True),

        # Shot metadata
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True, server_default='3.0'),

        # AI feedback for regeneration
        sa.Column('ai_feedback', sa.Text(), nullable=True),

        # Status
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('is_favorite', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('rating', sa.Integer(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['shot_generations.id'], ondelete='CASCADE'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_shot_rating'),
        sa.UniqueConstraint('scene_id', 'shot_number', 'version', name='unique_scene_shot_version')
    )

    # Create indexes for shot_generations
    op.create_index('idx_shot_generations_scene', 'shot_generations', ['scene_id'])
    op.create_index('idx_shot_generations_active', 'shot_generations', ['is_active', 'scene_id'])

    # Create generation_sessions table (for grouping related work)
    op.create_table(
        'generation_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # Session metadata
        sa.Column('total_generations', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('active_generation_id', sa.String(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['active_generation_id'], ['script_generations.id'])
    )

    # Create generation_notes table (comments/collaboration)
    op.create_table(
        'generation_notes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('generation_id', sa.String(), nullable=False),
        sa.Column('generation_table', sa.String(50), nullable=False),  # 'script_generations' or 'shot_generations'

        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=False),

        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for generation_notes
    op.create_index('idx_generation_notes', 'generation_notes', ['generation_id', 'generation_table'])


def downgrade() -> None:
    """Downgrade schema - Remove generation history tables."""
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('generation_notes')
    op.drop_table('generation_sessions')
    op.drop_table('shot_generations')
    op.drop_table('scenes')
    op.drop_table('script_generations')
