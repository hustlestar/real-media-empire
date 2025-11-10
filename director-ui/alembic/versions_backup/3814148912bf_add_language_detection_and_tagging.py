"""add language detection and tagging

Revision ID: 3814148912bf
Revises: 60cbc6e768e2
Create Date: 2025-10-01 11:11:35.370482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3814148912bf'
down_revision: Union[str, None] = '60cbc6e768e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    is_postgresql = conn.dialect.name == 'postgresql'

    # Create language_enum only for PostgreSQL
    if is_postgresql:
        result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'language_enum'"))
        if not result.scalar():
            language_enum = postgresql.ENUM('en', 'ru', 'es', name='language_enum', create_type=False)
            language_enum.create(conn, checkfirst=False)

    # Add detected_language column to content_items (nullable for existing data)
    op.add_column('content_items',
        sa.Column('detected_language',
                  sa.String(10) if not is_postgresql else postgresql.ENUM('en', 'ru', 'es', name='language_enum', create_type=False),
                  nullable=True,
                  comment='Detected language of content'))

    # Add extracted_text_paths JSON/JSONB column (for multiple language versions)
    op.add_column('content_items',
        sa.Column('extracted_text_paths',
                  sa.JSON() if not is_postgresql else postgresql.JSONB(astext_type=sa.Text()),
                  nullable=True,
                  comment='Paths to extracted text files by language'))

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.String() if not is_postgresql else postgresql.UUID(as_uuid=True), nullable=False, comment='Unique tag ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='Tag name'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='Tag creation timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create index on tag name
    op.create_index('idx_tags_name', 'tags', ['name'], unique=True)

    # Create content_tags junction table
    op.create_table(
        'content_tags',
        sa.Column('content_id', sa.String() if not is_postgresql else postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to content item'),
        sa.Column('tag_id', sa.String() if not is_postgresql else postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to tag'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='Tag assignment timestamp'),
        sa.ForeignKeyConstraint(['content_id'], ['content_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('content_id', 'tag_id')
    )

    # Create indexes for content_tags
    op.create_index('idx_content_tags_content_id', 'content_tags', ['content_id'], unique=False)
    op.create_index('idx_content_tags_tag_id', 'content_tags', ['tag_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_content_tags_tag_id', table_name='content_tags')
    op.drop_index('idx_content_tags_content_id', table_name='content_tags')
    op.drop_index('idx_tags_name', table_name='tags')

    # Drop tables
    op.drop_table('content_tags')
    op.drop_table('tags')

    # Drop columns from content_items
    op.drop_column('content_items', 'extracted_text_paths')
    op.drop_column('content_items', 'detected_language')

    # Drop language_enum
    sa.Enum(name='language_enum').drop(op.get_bind(), checkfirst=True)
