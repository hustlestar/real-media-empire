"""make content_id nullable for bundle jobs

Revision ID: 1f6daa946e69
Revises: d4ec806d55f4
Create Date: 2025-10-01 14:29:08.860913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f6daa946e69'
down_revision: Union[str, None] = 'd4ec806d55f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make content_id nullable to support bundle jobs
    op.alter_column('processing_jobs', 'content_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Make content_id not nullable again
    op.alter_column('processing_jobs', 'content_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=False)
