"""fix_reserved_columns_and_add_providers

Revision ID: 3f2fde3ed5e5
Revises: a1b2c3d4e5f6
Create Date: 2025-11-08 12:43:26.639710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f2fde3ed5e5'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Rename reserved 'metadata' column to 'asset_metadata' in assets table
    op.alter_column('assets', 'metadata', new_column_name='asset_metadata')

    # 2. Rename reserved 'metadata' column to 'content_metadata' in content_items table
    op.alter_column('content_items', 'metadata', new_column_name='content_metadata')

    # 3. Add provider column to presentations table
    op.add_column('presentations', sa.Column('provider', sa.String(50), nullable=False, server_default='openai'))

    # 4. Add provider column to avatar_videos table (if it doesn't exist)
    # Check if column exists first to handle cases where AvatarVideo was already created with provider
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('avatar_videos')]
    if 'provider' not in columns:
        op.add_column('avatar_videos', sa.Column('provider', sa.String(50), nullable=False, server_default='heygen'))


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the changes in opposite order

    # 4. Remove provider column from avatar_videos
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('avatar_videos')]
    if 'provider' in columns:
        op.drop_column('avatar_videos', 'provider')

    # 3. Remove provider column from presentations
    op.drop_column('presentations', 'provider')

    # 2. Rename content_metadata back to metadata in content_items
    op.alter_column('content_items', 'content_metadata', new_column_name='metadata')

    # 1. Rename asset_metadata back to metadata in assets
    op.alter_column('assets', 'asset_metadata', new_column_name='metadata')
