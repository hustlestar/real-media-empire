"""create_asset_centric_schema_v2

Revision ID: 2d0bd74884ab
Revises: e383eec480f9
Create Date: 2025-11-10 10:22:41.470339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d0bd74884ab'
down_revision: Union[str, None] = 'e383eec480f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create new asset-centric tables."""

    # Create assets_v2 table (universal content storage)
    op.create_table(
        'assets_v2',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=True),

        # Core universal fields
        sa.Column('type', sa.String(50), nullable=False, comment='Asset type: script, text, audio, video, image, shot, film, character_ref, scene'),
        sa.Column('name', sa.String(255), nullable=False),

        # Storage
        sa.Column('url', sa.Text(), nullable=True, comment='Public CDN URL'),
        sa.Column('file_path', sa.Text(), nullable=True, comment='Local filesystem path'),
        sa.Column('size', sa.BigInteger(), nullable=True, comment='File size in bytes'),
        sa.Column('duration', sa.Float(), nullable=True, comment='Duration for audio/video in seconds'),

        # Flexible metadata (type-specific data)
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}', comment='Type-specific metadata'),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=False, server_default='{}', comment='Asset tags'),

        # Generation tracking
        sa.Column('source', sa.String(50), nullable=True, comment='Source: upload, generation, import, derivative'),
        sa.Column('generation_cost', sa.Float(), nullable=True, comment='Cost to generate this asset'),
        sa.Column('generation_metadata', sa.JSON(), nullable=True, comment='Provider, model, prompt, seed'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Create indexes for assets_v2
    op.create_index('idx_assets_v2_workspace_id', 'assets_v2', ['workspace_id'])
    op.create_index('idx_assets_v2_type', 'assets_v2', ['type'])
    op.create_index('idx_assets_v2_source', 'assets_v2', ['source'])
    op.create_index('idx_assets_v2_metadata', 'assets_v2', ['metadata'], postgresql_using='gin')
    op.create_index('idx_assets_v2_tags', 'assets_v2', ['tags'], postgresql_using='gin')

    # Create asset_relationships table (universal linking)
    op.create_table(
        'asset_relationships',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('parent_asset_id', sa.String(), sa.ForeignKey('assets_v2.id', ondelete='CASCADE'), nullable=False),
        sa.Column('child_asset_id', sa.String(), sa.ForeignKey('assets_v2.id', ondelete='CASCADE'), nullable=False),

        sa.Column('relationship_type', sa.String(50), nullable=False, comment='used_in, derived_from, variant_of, part_of, reference_for, generated_from'),
        sa.Column('sequence', sa.Integer(), nullable=True, comment='Order when relationship implies sequence'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}', comment='Relationship-specific data'),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Create unique constraint for relationships
    op.create_unique_constraint(
        'uq_asset_relationships_parent_child_type',
        'asset_relationships',
        ['parent_asset_id', 'child_asset_id', 'relationship_type']
    )

    # Create indexes for asset_relationships
    op.create_index('idx_asset_rel_parent', 'asset_relationships', ['parent_asset_id'])
    op.create_index('idx_asset_rel_child', 'asset_relationships', ['child_asset_id'])
    op.create_index('idx_asset_rel_type', 'asset_relationships', ['relationship_type'])

    # Create asset_collections table (grouping & organization)
    op.create_table(
        'asset_collections',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),

        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, comment='project, character, storyboard, library'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Create indexes for asset_collections
    op.create_index('idx_collections_workspace', 'asset_collections', ['workspace_id'])
    op.create_index('idx_collections_type', 'asset_collections', ['type'])

    # Create asset_collection_members table (collection membership)
    op.create_table(
        'asset_collection_members',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('collection_id', sa.String(), sa.ForeignKey('asset_collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_id', sa.String(), sa.ForeignKey('assets_v2.id', ondelete='CASCADE'), nullable=False),

        sa.Column('sequence', sa.Integer(), nullable=True, comment='Order within collection'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}', comment='Member-specific data'),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Create unique constraint for collection membership
    op.create_unique_constraint(
        'uq_collection_members_collection_asset',
        'asset_collection_members',
        ['collection_id', 'asset_id']
    )

    # Create indexes for asset_collection_members
    op.create_index('idx_collection_members_collection', 'asset_collection_members', ['collection_id'])
    op.create_index('idx_collection_members_asset', 'asset_collection_members', ['asset_id'])


def downgrade() -> None:
    """Downgrade schema - Drop new asset-centric tables."""

    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('asset_collection_members')
    op.drop_table('asset_collections')
    op.drop_table('asset_relationships')
    op.drop_table('assets_v2')
