"""add_film_id_to_shot_generations

Revision ID: 6db0c760d1a7
Revises: d059a51015a2
Create Date: 2025-11-09 07:36:38.448979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6db0c760d1a7'
down_revision: Union[str, None] = 'd059a51015a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make scene_id nullable to support standalone shots
    op.alter_column(
        'shot_generations',
        'scene_id',
        existing_type=sa.String(),
        nullable=True
    )

    # Add film_id column to shot_generations table
    op.add_column(
        'shot_generations',
        sa.Column('film_id', sa.String(), nullable=True)
    )

    # Add index for better query performance
    op.create_index(
        'ix_shot_generations_film_id',
        'shot_generations',
        ['film_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove index
    op.drop_index('ix_shot_generations_film_id', table_name='shot_generations')

    # Remove film_id column
    op.drop_column('shot_generations', 'film_id')
