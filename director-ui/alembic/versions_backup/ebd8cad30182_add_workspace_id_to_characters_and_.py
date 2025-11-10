"""add_workspace_id_to_characters_and_assets

Revision ID: ebd8cad30182
Revises: 2922e0be3dd2
Create Date: 2025-11-09 12:19:00.019724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebd8cad30182'
down_revision: Union[str, None] = '2922e0be3dd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add workspace_id to characters table
    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.add_column(sa.Column('workspace_id', sa.String(), nullable=True))
        batch_op.create_foreign_key('fk_characters_workspace_id', 'workspaces', ['workspace_id'], ['id'])
        batch_op.create_index('idx_characters_workspace_id', ['workspace_id'])

    # Add workspace_id and generation tracking to assets table
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('workspace_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('character_id', sa.String(), nullable=True, comment='Character this asset was generated for'))
        batch_op.add_column(sa.Column('source', sa.String(), nullable=True, comment='Source of asset (upload, generation, import)'))
        batch_op.add_column(sa.Column('generation_cost', sa.Float(), nullable=True, comment='Cost to generate this asset'))
        batch_op.add_column(sa.Column('generation_metadata', sa.JSON(), nullable=True, comment='Generation details (model, prompt, seed)'))
        batch_op.create_foreign_key('fk_assets_workspace_id', 'workspaces', ['workspace_id'], ['id'])
        batch_op.create_foreign_key('fk_assets_character_id', 'characters', ['character_id'], ['id'])
        batch_op.create_index('idx_assets_workspace_id', ['workspace_id'])
        batch_op.create_index('idx_assets_character_id', ['character_id'])
        batch_op.create_index('idx_assets_source', ['source'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove added columns from assets
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.drop_index('idx_assets_source')
        batch_op.drop_index('idx_assets_character_id')
        batch_op.drop_index('idx_assets_workspace_id')
        batch_op.drop_constraint('fk_assets_character_id', type_='foreignkey')
        batch_op.drop_constraint('fk_assets_workspace_id', type_='foreignkey')
        batch_op.drop_column('generation_metadata')
        batch_op.drop_column('generation_cost')
        batch_op.drop_column('source')
        batch_op.drop_column('character_id')
        batch_op.drop_column('workspace_id')

    # Remove added columns from characters
    with op.batch_alter_table('characters', schema=None) as batch_op:
        batch_op.drop_index('idx_characters_workspace_id')
        batch_op.drop_constraint('fk_characters_workspace_id', type_='foreignkey')
        batch_op.drop_column('workspace_id')
