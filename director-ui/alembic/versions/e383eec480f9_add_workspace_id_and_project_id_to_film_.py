"""add_workspace_id_and_project_id_to_film_projects

Revision ID: e383eec480f9
Revises: ebd8cad30182
Create Date: 2025-11-09 13:43:01.457159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e383eec480f9'
down_revision: Union[str, None] = 'ebd8cad30182'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add workspace_id and project_id to film_projects table
    with op.batch_alter_table('film_projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('workspace_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('project_id', sa.String(), nullable=True))
        batch_op.create_foreign_key('fk_film_projects_workspace_id', 'workspaces', ['workspace_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_film_projects_project_id', 'projects', ['project_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index('idx_film_projects_workspace_id', ['workspace_id'])
        batch_op.create_index('idx_film_projects_project_id', ['project_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove workspace_id and project_id from film_projects table
    with op.batch_alter_table('film_projects', schema=None) as batch_op:
        batch_op.drop_index('idx_film_projects_project_id')
        batch_op.drop_index('idx_film_projects_workspace_id')
        batch_op.drop_constraint('fk_film_projects_project_id', type_='foreignkey')
        batch_op.drop_constraint('fk_film_projects_workspace_id', type_='foreignkey')
        batch_op.drop_column('project_id')
        batch_op.drop_column('workspace_id')
