"""add_workspaces_projects_and_film_shots_tables

Revision ID: a7194f3d0364
Revises: 3f2fde3ed5e5
Create Date: 2025-11-08 16:14:05.201261

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7194f3d0364'
down_revision: Union[str, None] = '3f2fde3ed5e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('storage_quota_gb', sa.Integer(), nullable=True, server_default='100'),
        sa.Column('monthly_budget_usd', sa.Float(), nullable=True, server_default='1000.0'),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workspace_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True, server_default='campaign'),
        sa.Column('parent_project_id', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='active'),
        sa.Column('project_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.ForeignKeyConstraint(['parent_project_id'], ['projects.id'])
    )

    # Create film_shots table
    op.create_table(
        'film_shots',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('shot_id', sa.String(), nullable=False),
        sa.Column('film_project_id', sa.String(), nullable=False),
        sa.Column('video_url', sa.String(), nullable=False),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('audio_url', sa.String(), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='completed'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['film_project_id'], ['film_projects.id'])
    )

    # Create shot_reviews table
    op.create_table(
        'shot_reviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('shot_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reviewer', sa.String(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['shot_id'], ['film_shots.id']),
        sa.UniqueConstraint('shot_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('shot_reviews')
    op.drop_table('film_shots')
    op.drop_table('projects')
    op.drop_table('workspaces')
