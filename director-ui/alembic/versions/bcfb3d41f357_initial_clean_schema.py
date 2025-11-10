"""initial_clean_schema

Revision ID: bcfb3d41f357
Revises: 
Create Date: 2025-11-10 10:33:21.287570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcfb3d41f357'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create clean asset-centric schema from scratch."""

    # ========================================================================
    # CORE INFRASTRUCTURE TABLES
    # ========================================================================

    # 1. Workspaces - Multi-tenancy
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_workspaces_name', 'workspaces', ['name'])

    # 2. Users - Authentication
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])

    # ========================================================================
    # UNIVERSAL ASSET MODEL
    # ========================================================================

    # 3. Assets - Universal content storage (everything is an asset)
    op.create_table(
        'assets',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=True),

        # Core universal fields
        sa.Column('type', sa.String(50), nullable=False, comment='Asset type: script, text, audio, video, image, shot, shot_take, film, character_ref, scene'),
        sa.Column('name', sa.String(255), nullable=False),

        # Storage
        sa.Column('url', sa.Text(), nullable=True, comment='Public CDN URL'),
        sa.Column('file_path', sa.Text(), nullable=True, comment='Local filesystem path'),
        sa.Column('size', sa.BigInteger(), nullable=True, comment='File size in bytes'),
        sa.Column('duration', sa.Float(), nullable=True, comment='Duration for audio/video in seconds'),

        # Flexible metadata (type-specific data stored as JSONB)
        sa.Column('asset_metadata', sa.JSON(), nullable=False, server_default='{}', comment='Type-specific metadata'),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=False, server_default='{}', comment='Asset tags'),

        # Generation tracking
        sa.Column('source', sa.String(50), nullable=True, comment='Source: upload, generation, import, derivative'),
        sa.Column('generation_cost', sa.Float(), nullable=True, comment='Cost to generate this asset'),
        sa.Column('generation_metadata', sa.JSON(), nullable=True, comment='Provider, model, prompt, seed'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Asset indexes
    op.create_index('idx_assets_workspace_id', 'assets', ['workspace_id'])
    op.create_index('idx_assets_type', 'assets', ['type'])
    op.create_index('idx_assets_source', 'assets', ['source'])
    op.create_index('idx_assets_asset_metadata', 'assets', ['asset_metadata'], postgresql_using='gin')
    op.create_index('idx_assets_tags', 'assets', ['tags'], postgresql_using='gin')
    op.create_index('idx_assets_created_at', 'assets', ['created_at'])

    # 4. Asset Relationships - Universal linking (graph structure)
    op.create_table(
        'asset_relationships',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('parent_asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('child_asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),

        sa.Column('relationship_type', sa.String(50), nullable=False, comment='contains_shot, uses_character, uses_audio, generation_attempt, generated_video, final_edit, derived_from, variant_of'),
        sa.Column('sequence', sa.Integer(), nullable=True, comment='Order when relationship implies sequence'),
        sa.Column('asset_metadata', sa.JSON(), nullable=False, server_default='{}', comment='Relationship-specific data'),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Relationship constraints and indexes
    op.create_unique_constraint(
        'uq_asset_relationships_parent_child_type',
        'asset_relationships',
        ['parent_asset_id', 'child_asset_id', 'relationship_type']
    )
    op.create_index('idx_asset_rel_parent', 'asset_relationships', ['parent_asset_id'])
    op.create_index('idx_asset_rel_child', 'asset_relationships', ['child_asset_id'])
    op.create_index('idx_asset_rel_type', 'asset_relationships', ['relationship_type'])
    op.create_index('idx_asset_rel_parent_type', 'asset_relationships', ['parent_asset_id', 'relationship_type'])

    # 5. Asset Collections - Grouping & organization
    op.create_table(
        'asset_collections',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),

        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, comment='project, character, storyboard, library'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_metadata', sa.JSON(), nullable=False, server_default='{}'),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Collection indexes
    op.create_index('idx_collections_workspace', 'asset_collections', ['workspace_id'])
    op.create_index('idx_collections_type', 'asset_collections', ['type'])

    # 6. Asset Collection Members - Collection membership
    op.create_table(
        'asset_collection_members',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('collection_id', sa.String(), sa.ForeignKey('asset_collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),

        sa.Column('sequence', sa.Integer(), nullable=True, comment='Order within collection'),
        sa.Column('asset_metadata', sa.JSON(), nullable=False, server_default='{}', comment='Member-specific data'),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Collection member constraints and indexes
    op.create_unique_constraint(
        'uq_collection_members_collection_asset',
        'asset_collection_members',
        ['collection_id', 'asset_id']
    )
    op.create_index('idx_collection_members_collection', 'asset_collection_members', ['collection_id'])
    op.create_index('idx_collection_members_asset', 'asset_collection_members', ['asset_id'])

    # ========================================================================
    # TAGGING SYSTEM
    # ========================================================================

    # 7. Tags - Universal tags
    op.create_table(
        'tags',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('category', sa.String(50), nullable=True, comment='Optional tag category'),
        sa.Column('color', sa.String(7), nullable=True, comment='Hex color for UI'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_tags_name', 'tags', ['name'])
    op.create_index('idx_tags_category', 'tags', ['category'])

    # 8. Asset Tags - Many-to-many asset tagging
    op.create_table(
        'asset_tags',
        sa.Column('asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag_id', sa.String(), sa.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('asset_id', 'tag_id'),
    )
    op.create_index('idx_asset_tags_asset', 'asset_tags', ['asset_id'])
    op.create_index('idx_asset_tags_tag', 'asset_tags', ['tag_id'])

    # ========================================================================
    # LEGACY CONTENT SYSTEM (for backward compatibility)
    # ========================================================================

    # 9. Content Items - Legacy content storage (will migrate to assets later)
    op.create_table(
        'content_items',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('content_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('source_type', sa.String(50), nullable=False, comment='pdf_url, youtube, web, file_upload'),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('file_reference', sa.String(255), nullable=True),
        sa.Column('extracted_text_path', sa.Text(), nullable=False),
        sa.Column('extracted_text_paths', sa.JSON(), nullable=True, comment='Paths by language'),
        sa.Column('content_metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('processing_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('detected_language', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_content_items_hash', 'content_items', ['content_hash'])
    op.create_index('idx_content_items_user', 'content_items', ['user_id'])
    op.create_index('idx_content_items_status', 'content_items', ['processing_status'])

    # 10. Content Tags - Legacy content tagging (many-to-many)
    op.create_table(
        'content_tags',
        sa.Column('content_id', sa.String(), sa.ForeignKey('content_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag_id', sa.String(), sa.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('content_id', 'tag_id'),
    )
    op.create_index('idx_content_tags_content', 'content_tags', ['content_id'])
    op.create_index('idx_content_tags_tag', 'content_tags', ['tag_id'])


def downgrade() -> None:
    """Drop all tables."""

    # Drop in reverse order (respect foreign keys)
    op.drop_table('content_tags')
    op.drop_table('content_items')
    op.drop_table('asset_tags')
    op.drop_table('tags')
    op.drop_table('asset_collection_members')
    op.drop_table('asset_collections')
    op.drop_table('asset_relationships')
    op.drop_table('assets')
    op.drop_table('users')
    op.drop_table('workspaces')
