"""add_blog_post_processing_type

Revision ID: 029bcafb7929
Revises: 1f6daa946e69
Create Date: 2025-10-01 16:40:58.964812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '029bcafb7929'
down_revision: Union[str, None] = '1f6daa946e69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add 'blog_post' to job_processing_type_enum
    op.execute("ALTER TYPE job_processing_type_enum ADD VALUE IF NOT EXISTS 'blog_post'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL doesn't support removing enum values, so we can't truly downgrade
    # This would require recreating the enum type and all dependent objects
    pass
