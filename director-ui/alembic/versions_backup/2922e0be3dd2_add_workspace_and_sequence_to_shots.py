"""add_workspace_and_sequence_to_shots

Revision ID: 2922e0be3dd2
Revises: 6db0c760d1a7
Create Date: 2025-11-09 07:42:13.833195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2922e0be3dd2'
down_revision: Union[str, None] = '6db0c760d1a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add workspace_id for organizing shots by workspace
    op.add_column(
        'shot_generations',
        sa.Column('workspace_id', sa.String(), nullable=True)
    )

    # Add sequence_order for shot sequencing in storyboards
    op.add_column(
        'shot_generations',
        sa.Column('sequence_order', sa.Integer(), nullable=True)
    )

    # Add indexes for better query performance
    op.create_index(
        'ix_shot_generations_workspace_id',
        'shot_generations',
        ['workspace_id'],
        unique=False
    )

    op.create_index(
        'ix_shot_generations_sequence_order',
        'shot_generations',
        ['sequence_order'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove indexes
    op.drop_index('ix_shot_generations_sequence_order', table_name='shot_generations')
    op.drop_index('ix_shot_generations_workspace_id', table_name='shot_generations')

    # Remove columns
    op.drop_column('shot_generations', 'sequence_order')
    op.drop_column('shot_generations', 'workspace_id')
