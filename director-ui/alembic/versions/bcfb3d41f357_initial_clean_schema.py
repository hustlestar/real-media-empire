"""initial_clean_schema

Revision ID: bcfb3d41f357
Revises: 
Create Date: 2025-11-10 10:33:21.287570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY


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
        sa.Column('slug', sa.String(255), unique=True, nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('storage_quota_gb', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('monthly_budget_usd', sa.Float(), nullable=False, server_default='1000.0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_workspaces_name', 'workspaces', ['name'])
    op.create_index('idx_workspaces_slug', 'workspaces', ['slug'])

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

    # 3. Projects - Workspace organization
    op.create_table(
        'projects',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, server_default='campaign', comment='campaign, brand, series, folder'),
        sa.Column('parent_project_id', sa.String(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active', comment='active, archived, deleted'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_projects_workspace', 'projects', ['workspace_id'])
    op.create_index('idx_projects_slug', 'projects', ['slug'])
    op.create_index('idx_projects_parent', 'projects', ['parent_project_id'])

    # ========================================================================
    # UNIVERSAL ASSET MODEL
    # ========================================================================

    # 4. Assets - Universal content storage (everything is an asset)
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
        sa.Column('asset_metadata', JSONB(), nullable=False, server_default='{}', comment='Type-specific metadata'),
        sa.Column('tags', ARRAY(sa.String()), nullable=False, server_default='{}', comment='Asset tags'),

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
    op.create_index('idx_assets_asset_metadata', 'assets', ['asset_metadata'],
                    postgresql_using='gin', postgresql_ops={'asset_metadata': 'jsonb_path_ops'})
    op.create_index('idx_assets_tags', 'assets', ['tags'], postgresql_using='gin')
    op.create_index('idx_assets_created_at', 'assets', ['created_at'])

    # 5. Asset Relationships - Universal linking (graph structure)
    op.create_table(
        'asset_relationships',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('parent_asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('child_asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),

        sa.Column('relationship_type', sa.String(50), nullable=False, comment='contains_shot, uses_character, uses_audio, generation_attempt, generated_video, final_edit, derived_from, variant_of'),
        sa.Column('sequence', sa.Integer(), nullable=True, comment='Order when relationship implies sequence'),
        sa.Column('relationship_metadata', sa.JSON(), nullable=False, server_default='{}', comment='Relationship-specific data'),

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

    # 6. Asset Collections - Grouping & organization
    op.create_table(
        'asset_collections',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),

        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, comment='project, character, storyboard, library'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('collection_metadata', sa.JSON(), nullable=False, server_default='{}'),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )

    # Collection indexes
    op.create_index('idx_collections_workspace', 'asset_collections', ['workspace_id'])
    op.create_index('idx_collections_type', 'asset_collections', ['type'])

    # 7. Asset Collection Members - Collection membership
    op.create_table(
        'asset_collection_members',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('collection_id', sa.String(), sa.ForeignKey('asset_collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_id', sa.String(), sa.ForeignKey('assets.id', ondelete='CASCADE'), nullable=False),

        sa.Column('sequence', sa.Integer(), nullable=True, comment='Order within collection'),
        sa.Column('member_metadata', sa.JSON(), nullable=False, server_default='{}', comment='Member-specific data'),

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

    # 8. Tags - Universal tags
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

    # 9. Asset Tags - Many-to-many asset tagging
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
    # CHARACTER & FILM MANAGEMENT
    # ========================================================================

    # 10. Characters - Visual consistency tracking
    op.create_table(
        'characters',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference_images', sa.JSON(), nullable=True, comment='Array of image URLs'),
        sa.Column('attributes', sa.JSON(), nullable=True, comment='Character attributes (age, gender, ethnicity, etc.)'),
        sa.Column('consistency_prompt', sa.Text(), nullable=True, comment='Generated prompt for AI consistency'),
        sa.Column('projects_used', sa.JSON(), nullable=True, comment='Array of project IDs where character is used'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_characters_workspace', 'characters', ['workspace_id'])
    op.create_index('idx_characters_name', 'characters', ['name'])

    # 11. Film Projects - AI-generated films
    op.create_table(
        'film_projects',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=True),
        sa.Column('project_id', sa.String(), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending', comment='pending, processing, completed, failed'),
        sa.Column('shots_config', sa.JSON(), nullable=True, comment='Original shots configuration'),
        sa.Column('generated_shots', sa.JSON(), nullable=True, comment='Generated shot metadata'),
        sa.Column('video_provider', sa.String(), nullable=True, comment='minimax, kling, runway'),
        sa.Column('image_provider', sa.String(), nullable=True, comment='fal, replicate'),
        sa.Column('audio_provider', sa.String(), nullable=True, comment='openai, elevenlabs'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('budget_limit', sa.Float(), nullable=True),
        sa.Column('output_path', sa.String(), nullable=True, comment='Final video path'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_film_projects_workspace', 'film_projects', ['workspace_id'])
    op.create_index('idx_film_projects_project', 'film_projects', ['project_id'])
    op.create_index('idx_film_projects_status', 'film_projects', ['status'])

    # 12. Film Shots - Individual shots within films
    op.create_table(
        'film_shots',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('shot_id', sa.String(), nullable=False, comment='Shot identifier (e.g., shot_001)'),
        sa.Column('film_project_id', sa.String(), sa.ForeignKey('film_projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('video_url', sa.String(), nullable=False),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True, comment='Source image for video generation'),
        sa.Column('audio_url', sa.String(), nullable=True, comment='Audio track for the shot'),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False, comment='Duration in seconds'),
        sa.Column('sequence_order', sa.Integer(), nullable=True, comment='Order in the final film'),
        sa.Column('status', sa.String(), nullable=False, server_default='completed', comment='completed, approved, rejected, needs_revision, generating, pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_film_shots_film_project', 'film_shots', ['film_project_id'])
    op.create_index('idx_film_shots_shot_id', 'film_shots', ['shot_id'])
    op.create_index('idx_film_shots_status', 'film_shots', ['status'])

    # 13. Shot Reviews - Review and feedback for shots
    op.create_table(
        'shot_reviews',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('shot_id', sa.String(), sa.ForeignKey('film_shots.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('status', sa.String(), nullable=False, comment='approved, rejected, needs_revision'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Director feedback and notes'),
        sa.Column('reviewer', sa.String(), nullable=True, comment='Username or email of reviewer'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_shot_reviews_shot', 'shot_reviews', ['shot_id'])

    # ========================================================================
    # PRESENTATION GENERATION
    # ========================================================================

    # 14. Presentations - AI-generated PowerPoint presentations
    op.create_table(
        'presentations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('topic', sa.String(), nullable=False),
        sa.Column('brief', sa.Text(), nullable=True),
        sa.Column('content_source', sa.String(), nullable=False, comment='ai, youtube, web, file'),
        sa.Column('content_url', sa.String(), nullable=True, comment='YouTube/web URL or file path'),
        sa.Column('num_slides', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('tone', sa.String(), nullable=False, server_default='professional'),
        sa.Column('target_audience', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=False, server_default='openai', comment='openai, anthropic, etc.'),
        sa.Column('model', sa.String(), nullable=False, server_default='gpt-4o-mini', comment='Model name'),
        sa.Column('status', sa.String(), nullable=False, server_default='pending', comment='pending, processing, completed, failed'),
        sa.Column('outline', sa.JSON(), nullable=True, comment='Generated outline'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('budget_limit', sa.Float(), nullable=True),
        sa.Column('output_path', sa.String(), nullable=True, comment='Final PPTX path'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_presentations_status', 'presentations', ['status'])

    # ========================================================================
    # AVATAR VIDEO GENERATION
    # ========================================================================

    # 15. Avatar Videos - HeyGen, Veed.io avatar videos
    op.create_table(
        'avatar_videos',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('provider', sa.String(), nullable=False, server_default='heygen', comment='heygen, veed, etc.'),
        sa.Column('video_id', sa.String(), unique=True, nullable=False, comment='Provider video_id'),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('script', sa.Text(), nullable=False),
        sa.Column('avatar_id', sa.String(), nullable=False),
        sa.Column('avatar_name', sa.String(), nullable=True),
        sa.Column('voice_id', sa.String(), nullable=False),
        sa.Column('voice_name', sa.String(), nullable=True),
        sa.Column('aspect_ratio', sa.String(), nullable=False, server_default='9:16', comment='9:16, 16:9, 1:1, 4:5'),
        sa.Column('background_type', sa.String(), nullable=False, server_default='color', comment='color, image, video'),
        sa.Column('background_value', sa.String(), nullable=False, server_default='#000000'),
        sa.Column('voice_speed', sa.Float(), nullable=False, server_default='1.1'),
        sa.Column('voice_pitch', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('voice_emotion', sa.String(), nullable=False, server_default='Excited'),
        sa.Column('avatar_scale', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('has_green_screen', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('avatar_offset_x', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avatar_offset_y', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('caption', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('test', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.String(), nullable=False, server_default='pending', comment='pending, processing, completed, failed'),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True, comment='Video duration in seconds'),
        sa.Column('cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('provider_metadata', sa.JSON(), nullable=True, comment='Provider-specific metadata'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_avatar_videos_provider', 'avatar_videos', ['provider'])
    op.create_index('idx_avatar_videos_video_id', 'avatar_videos', ['video_id'])
    op.create_index('idx_avatar_videos_status', 'avatar_videos', ['status'])

    # ========================================================================
    # SOCIAL MEDIA PUBLISHING
    # ========================================================================

    # 16. Social Accounts - Platform account configuration
    op.create_table(
        'social_accounts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('platform', sa.String(), nullable=False, comment='tiktok, youtube, instagram, facebook, twitter, linkedin'),
        sa.Column('account_name', sa.String(), nullable=False),
        sa.Column('account_handle', sa.String(), nullable=True, comment='@username or channel ID'),
        sa.Column('credentials', sa.JSON(), nullable=True, comment='Platform-specific credentials'),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('default_settings', sa.JSON(), nullable=True, comment='Platform-specific default post settings'),
        sa.Column('posting_schedule', sa.JSON(), nullable=True, comment='Scheduled posting times'),
        sa.Column('platform_user_id', sa.String(), nullable=True, comment='Platform user/channel ID'),
        sa.Column('follower_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_social_accounts_platform', 'social_accounts', ['platform'])

    # 17. Publishing Posts - Published or scheduled posts
    op.create_table(
        'publishing_posts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('social_account_id', sa.String(), sa.ForeignKey('social_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False, comment='video, image, text, carousel'),
        sa.Column('content_url', sa.String(), nullable=True, comment='URL to video/image asset'),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True, comment='Array of hashtags'),
        sa.Column('status', sa.String(), nullable=False, server_default='draft', comment='draft, scheduled, publishing, published, failed'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('platform_settings', sa.JSON(), nullable=True, comment='Platform-specific options'),
        sa.Column('platform_post_id', sa.String(), nullable=True, comment='Post ID from platform'),
        sa.Column('platform_url', sa.String(), nullable=True, comment='Direct link to post'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('source_id', sa.String(), nullable=True, comment='ID of source content'),
        sa.Column('source_type', sa.String(), nullable=True, comment='film, presentation, avatar_video'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_publishing_posts_account', 'publishing_posts', ['social_account_id'])
    op.create_index('idx_publishing_posts_status', 'publishing_posts', ['status'])
    op.create_index('idx_publishing_posts_platform', 'publishing_posts', ['platform'])

    # 18. Publishing Analytics - Analytics for posts
    op.create_table(
        'publishing_analytics',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('post_id', sa.String(), sa.ForeignKey('publishing_posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('likes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('shares', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('saves', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('engagement_rate', sa.Float(), nullable=False, server_default='0.0', comment='(likes + comments + shares) / views'),
        sa.Column('watch_time', sa.Float(), nullable=False, server_default='0.0', comment='Total watch time in seconds'),
        sa.Column('avg_watch_time', sa.Float(), nullable=False, server_default='0.0', comment='Average watch time per view'),
        sa.Column('completion_rate', sa.Float(), nullable=False, server_default='0.0', comment='% of viewers who watched to end'),
        sa.Column('audience_demographics', sa.JSON(), nullable=True, comment='Age, gender, location data'),
        sa.Column('traffic_sources', sa.JSON(), nullable=True, comment='Where views came from'),
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='When metrics were last fetched'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_publishing_analytics_post', 'publishing_analytics', ['post_id'])

    # ========================================================================
    # GENERATION HISTORY - Version Control for AI Creation
    # ========================================================================

    # 19. Script Generations - Script/Scene/Shot generation with version control
    op.create_table(
        'script_generations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('generation_type', sa.String(50), nullable=False, comment='script, scene, shot'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_id', sa.String(), sa.ForeignKey('script_generations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('input_subject', sa.Text(), nullable=True),
        sa.Column('input_action', sa.Text(), nullable=True),
        sa.Column('input_location', sa.Text(), nullable=True),
        sa.Column('input_style', sa.String(100), nullable=True),
        sa.Column('input_genre', sa.String(100), nullable=True),
        sa.Column('input_idea', sa.Text(), nullable=True, comment='For script generation from idea'),
        sa.Column('input_partial_data', sa.JSON(), nullable=True, comment='Any additional user inputs'),
        sa.Column('ai_feedback', sa.Text(), nullable=True, comment='User refinement instructions'),
        sa.Column('ai_enhancement_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('output_prompt', sa.Text(), nullable=True),
        sa.Column('output_negative_prompt', sa.Text(), nullable=True),
        sa.Column('output_metadata', sa.JSON(), nullable=True, comment='Style, shot type, etc.'),
        sa.Column('output_full_data', sa.JSON(), nullable=True, comment='Complete generation result'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Current working version'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rating', sa.Integer(), nullable=True, comment='1-5 stars'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_script_gens_workspace', 'script_generations', ['workspace_id'])
    op.create_index('idx_script_gens_project', 'script_generations', ['project_id'])
    op.create_index('idx_script_gens_type', 'script_generations', ['generation_type'])
    op.create_index('idx_script_gens_parent', 'script_generations', ['parent_id'])

    # 20. Scenes - Scenes within script generations
    op.create_table(
        'scenes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('script_generation_id', sa.String(), sa.ForeignKey('script_generations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scene_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('time_of_day', sa.String(50), nullable=True),
        sa.Column('mood', sa.String(100), nullable=True),
        sa.Column('characters', sa.JSON(), nullable=True, comment='Array of character names/refs'),
        sa.Column('duration_estimate', sa.Integer(), nullable=True, comment='in seconds'),
        sa.Column('pacing', sa.String(50), nullable=True, comment='slow, medium, fast, action'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_scenes_script_gen', 'scenes', ['script_generation_id'])

    # 21. Shot Generations - Shot generation with version control
    op.create_table(
        'shot_generations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), nullable=True),
        sa.Column('scene_id', sa.String(), sa.ForeignKey('scenes.id', ondelete='CASCADE'), nullable=True, comment='Nullable for standalone shots'),
        sa.Column('film_id', sa.String(), nullable=True, comment='Film/project association'),
        sa.Column('shot_number', sa.Integer(), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=True, comment='For storyboard ordering'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('parent_id', sa.String(), sa.ForeignKey('shot_generations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('negative_prompt', sa.Text(), nullable=True),
        sa.Column('shot_type', sa.String(100), nullable=True),
        sa.Column('camera_motion', sa.String(100), nullable=True),
        sa.Column('lighting', sa.String(100), nullable=True),
        sa.Column('emotion', sa.String(100), nullable=True),
        sa.Column('shot_metadata', sa.JSON(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=False, server_default='3.0'),
        sa.Column('ai_feedback', sa.Text(), nullable=True, comment='For regeneration'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rating', sa.Integer(), nullable=True, comment='1-5 stars'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_shot_gens_workspace', 'shot_generations', ['workspace_id'])
    op.create_index('idx_shot_gens_scene', 'shot_generations', ['scene_id'])
    op.create_index('idx_shot_gens_film', 'shot_generations', ['film_id'])
    op.create_index('idx_shot_gens_parent', 'shot_generations', ['parent_id'])
    op.create_index('idx_shot_gens_sequence', 'shot_generations', ['sequence_order'])

    # 22. Generation Sessions - Grouping related generation work
    op.create_table(
        'generation_sessions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('workspace_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_generations', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_generation_id', sa.String(), sa.ForeignKey('script_generations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_gen_sessions_workspace', 'generation_sessions', ['workspace_id'])

    # 23. Generation Notes - Comments and notes for collaboration
    op.create_table(
        'generation_notes',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('generation_id', sa.String(), nullable=False, comment='ID of script_generation or shot_generation'),
        sa.Column('generation_table', sa.String(50), nullable=False, comment='script_generations or shot_generations'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    )
    op.create_index('idx_gen_notes_generation', 'generation_notes', ['generation_id'])

    # ========================================================================
    # LEGACY CONTENT SYSTEM (for backward compatibility)
    # ========================================================================

    # 10. Content Items - Legacy content storage (will migrate to assets later)
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

    # 11. Content Tags - Legacy content tagging (many-to-many)
    op.create_table(
        'content_tags',
        sa.Column('content_id', sa.String(), sa.ForeignKey('content_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tag_id', sa.String(), sa.ForeignKey('tags.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('content_id', 'tag_id'),
    )
    op.create_index('idx_content_tags_content', 'content_tags', ['content_id'])
    op.create_index('idx_content_tags_tag', 'content_tags', ['tag_id'])

    # ========================================================================
    # SEED DATA - Default workspace, user, and project
    # ========================================================================

    # Insert default user (id=66395090 from MAINTAINER_CHAT_ID)
    op.execute("""
        INSERT INTO users (id, email, username, password_hash, is_active, is_superuser)
        VALUES (66395090, 'admin@media-empire.local', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfS6ZXuHvK', true, true)
        ON CONFLICT (id) DO NOTHING;
    """)

    # Insert default workspace
    op.execute("""
        INSERT INTO workspaces (id, name, slug, owner_id, storage_quota_gb, monthly_budget_usd, settings)
        VALUES ('default-workspace', 'Default Workspace', 'default', 66395090, 100, 1000.0, '{}')
        ON CONFLICT (id) DO NOTHING;
    """)

    # Insert default project
    op.execute("""
        INSERT INTO projects (id, workspace_id, name, slug, type, status, project_metadata)
        VALUES ('demo-project-001', 'default-workspace', 'Demo Project', 'demo-project-001', 'campaign', 'active', '{}')
        ON CONFLICT (id) DO NOTHING;
    """)


def downgrade() -> None:
    """Drop all tables."""

    # Drop in reverse order (respect foreign keys)
    op.drop_table('content_tags')
    op.drop_table('content_items')
    op.drop_table('generation_notes')
    op.drop_table('generation_sessions')
    op.drop_table('shot_generations')
    op.drop_table('scenes')
    op.drop_table('script_generations')
    op.drop_table('publishing_analytics')
    op.drop_table('publishing_posts')
    op.drop_table('social_accounts')
    op.drop_table('avatar_videos')
    op.drop_table('presentations')
    op.drop_table('shot_reviews')
    op.drop_table('film_shots')
    op.drop_table('film_projects')
    op.drop_table('characters')
    op.drop_table('asset_tags')
    op.drop_table('tags')
    op.drop_table('asset_collection_members')
    op.drop_table('asset_collections')
    op.drop_table('asset_relationships')
    op.drop_table('assets')
    op.drop_table('projects')
    op.drop_table('users')
    op.drop_table('workspaces')
