"""add_heygen_and_postiz_tables

Revision ID: a1b2c3d4e5f6
Revises: 85562a830bc1
Create Date: 2025-01-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '85562a830bc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add HeyGen avatar videos and Postiz social publishing tables."""

    # Create avatar_videos table
    op.create_table(
        'avatar_videos',
        sa.Column('id', sa.String(255), nullable=False, comment='Avatar video unique ID (UUID)'),
        sa.Column('video_id', sa.String(255), nullable=False, comment='HeyGen video ID'),
        sa.Column('title', sa.String(500), nullable=True, comment='Video title'),
        sa.Column('script', sa.Text(), nullable=False, comment='Video script text'),
        sa.Column('avatar_id', sa.String(255), nullable=False, comment='HeyGen avatar ID'),
        sa.Column('avatar_name', sa.String(255), nullable=True, comment='Avatar name'),
        sa.Column('voice_id', sa.String(255), nullable=False, comment='HeyGen voice ID'),
        sa.Column('voice_name', sa.String(255), nullable=True, comment='Voice name'),

        # Configuration
        sa.Column('aspect_ratio', sa.String(10), server_default='9:16', nullable=False, comment='Aspect ratio (9:16, 16:9, 1:1, 4:5)'),
        sa.Column('background_type', sa.String(50), server_default='color', nullable=False, comment='Background type (color, image, video)'),
        sa.Column('background_value', sa.String(1024), server_default='#000000', nullable=False, comment='Background value (hex color or URL)'),
        sa.Column('voice_speed', sa.Float(), server_default='1.1', nullable=False, comment='Voice speed multiplier'),
        sa.Column('voice_pitch', sa.Integer(), server_default='50', nullable=False, comment='Voice pitch (0-100)'),
        sa.Column('voice_emotion', sa.String(50), server_default='Excited', nullable=False, comment='Voice emotion'),
        sa.Column('avatar_scale', sa.Float(), server_default='1.0', nullable=False, comment='Avatar scale multiplier'),
        sa.Column('has_green_screen', sa.Boolean(), server_default='false', nullable=False, comment='Green screen enabled'),
        sa.Column('avatar_offset_x', sa.Float(), server_default='0.0', nullable=False, comment='Avatar horizontal offset'),
        sa.Column('avatar_offset_y', sa.Float(), server_default='0.0', nullable=False, comment='Avatar vertical offset'),
        sa.Column('caption', sa.Boolean(), server_default='false', nullable=False, comment='Auto-captions enabled'),
        sa.Column('test', sa.Boolean(), server_default='false', nullable=False, comment='Test mode (no credits)'),

        # Generation results
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, comment='Generation status'),
        sa.Column('video_url', sa.String(1024), nullable=True, comment='Generated video URL'),
        sa.Column('duration', sa.Float(), nullable=True, comment='Video duration in seconds'),
        sa.Column('cost', sa.Float(), server_default='0.0', nullable=False, comment='Generation cost'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if failed'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='Additional HeyGen metadata'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Completion timestamp'),

        sa.PrimaryKeyConstraint('id', name='pk_avatar_videos'),
        sa.UniqueConstraint('video_id', name='uq_avatar_videos_video_id')
    )
    op.create_index('idx_avatar_videos_status', 'avatar_videos', ['status'])
    op.create_index('idx_avatar_videos_avatar_id', 'avatar_videos', ['avatar_id'])
    op.create_index('idx_avatar_videos_created_at', 'avatar_videos', ['created_at'])

    # Create social_accounts table
    op.create_table(
        'social_accounts',
        sa.Column('id', sa.String(255), nullable=False, comment='Social account unique ID (UUID)'),
        sa.Column('platform', sa.String(50), nullable=False, comment='Platform name (tiktok, youtube, instagram, etc.)'),
        sa.Column('account_name', sa.String(255), nullable=False, comment='Account display name'),
        sa.Column('account_handle', sa.String(255), nullable=True, comment='Account handle (@username or channel ID)'),

        # Authentication (should be encrypted in production)
        sa.Column('credentials', sa.JSON(), nullable=True, comment='Platform-specific credentials (encrypted)'),
        sa.Column('access_token', sa.Text(), nullable=True, comment='OAuth access token'),
        sa.Column('refresh_token', sa.Text(), nullable=True, comment='OAuth refresh token'),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True, comment='Token expiration time'),

        # Account settings
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False, comment='Account active status'),
        sa.Column('default_settings', sa.JSON(), nullable=True, comment='Platform-specific default post settings'),
        sa.Column('posting_schedule', sa.JSON(), nullable=True, comment='Scheduled posting times'),

        # Metadata
        sa.Column('platform_user_id', sa.String(255), nullable=True, comment='Platform-specific user/channel ID'),
        sa.Column('follower_count', sa.Integer(), server_default='0', nullable=False, comment='Follower count'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True, comment='Last sync timestamp'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),

        sa.PrimaryKeyConstraint('id', name='pk_social_accounts')
    )
    op.create_index('idx_social_accounts_platform', 'social_accounts', ['platform'])
    op.create_index('idx_social_accounts_active', 'social_accounts', ['is_active'])

    # Create publishing_posts table
    op.create_table(
        'publishing_posts',
        sa.Column('id', sa.String(255), nullable=False, comment='Post unique ID (UUID)'),
        sa.Column('social_account_id', sa.String(255), nullable=False, comment='Social account ID (foreign key)'),

        # Content
        sa.Column('content_type', sa.String(50), nullable=False, comment='Content type (video, image, text, carousel)'),
        sa.Column('content_url', sa.String(1024), nullable=True, comment='URL to video/image asset'),
        sa.Column('caption', sa.Text(), nullable=True, comment='Post caption/description'),
        sa.Column('hashtags', sa.JSON(), nullable=True, comment='Array of hashtags'),

        # Scheduling
        sa.Column('status', sa.String(50), server_default='draft', nullable=False, comment='Post status (draft, scheduled, publishing, published, failed)'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True, comment='Scheduled publish time'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True, comment='Actual publish time'),

        # Platform-specific
        sa.Column('platform', sa.String(50), nullable=False, comment='Target platform'),
        sa.Column('platform_settings', sa.JSON(), nullable=True, comment='Platform-specific options'),

        # Publishing results
        sa.Column('platform_post_id', sa.String(255), nullable=True, comment='Platform-specific post ID'),
        sa.Column('platform_url', sa.String(1024), nullable=True, comment='Direct link to post'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Error message if failed'),

        # Source tracking
        sa.Column('source_id', sa.String(255), nullable=True, comment='Source content ID (film_id, avatar_video_id, etc.)'),
        sa.Column('source_type', sa.String(50), nullable=True, comment='Source type (film, avatar_video, presentation)'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),

        sa.PrimaryKeyConstraint('id', name='pk_publishing_posts'),
        sa.ForeignKeyConstraint(['social_account_id'], ['social_accounts.id'], name='fk_publishing_posts_social_account_id', ondelete='CASCADE')
    )
    op.create_index('idx_publishing_posts_account', 'publishing_posts', ['social_account_id'])
    op.create_index('idx_publishing_posts_status', 'publishing_posts', ['status'])
    op.create_index('idx_publishing_posts_platform', 'publishing_posts', ['platform'])
    op.create_index('idx_publishing_posts_scheduled', 'publishing_posts', ['scheduled_at'])
    op.create_index('idx_publishing_posts_source', 'publishing_posts', ['source_id', 'source_type'])

    # Create publishing_analytics table
    op.create_table(
        'publishing_analytics',
        sa.Column('id', sa.String(255), nullable=False, comment='Analytics unique ID (UUID)'),
        sa.Column('post_id', sa.String(255), nullable=False, comment='Post ID (foreign key)'),

        # Engagement metrics
        sa.Column('views', sa.Integer(), server_default='0', nullable=False, comment='Total views'),
        sa.Column('likes', sa.Integer(), server_default='0', nullable=False, comment='Total likes'),
        sa.Column('comments', sa.Integer(), server_default='0', nullable=False, comment='Total comments'),
        sa.Column('shares', sa.Integer(), server_default='0', nullable=False, comment='Total shares'),
        sa.Column('saves', sa.Integer(), server_default='0', nullable=False, comment='Total saves/bookmarks'),

        # Performance metrics
        sa.Column('engagement_rate', sa.Float(), server_default='0.0', nullable=False, comment='Engagement rate percentage'),
        sa.Column('watch_time', sa.Float(), server_default='0.0', nullable=False, comment='Total watch time in seconds'),
        sa.Column('avg_watch_time', sa.Float(), server_default='0.0', nullable=False, comment='Average watch time per view'),
        sa.Column('completion_rate', sa.Float(), server_default='0.0', nullable=False, comment='Completion rate percentage'),

        # Audience insights
        sa.Column('audience_demographics', sa.JSON(), nullable=True, comment='Audience demographics data'),
        sa.Column('traffic_sources', sa.JSON(), nullable=True, comment='Traffic sources breakdown'),

        # Timestamps
        sa.Column('fetched_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='When metrics were fetched'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False, comment='Last update timestamp'),

        sa.PrimaryKeyConstraint('id', name='pk_publishing_analytics'),
        sa.ForeignKeyConstraint(['post_id'], ['publishing_posts.id'], name='fk_publishing_analytics_post_id', ondelete='CASCADE')
    )
    op.create_index('idx_publishing_analytics_post', 'publishing_analytics', ['post_id'])
    op.create_index('idx_publishing_analytics_fetched', 'publishing_analytics', ['fetched_at'])


def downgrade() -> None:
    """Downgrade schema - remove HeyGen and Postiz tables."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index('idx_publishing_analytics_fetched', table_name='publishing_analytics')
    op.drop_index('idx_publishing_analytics_post', table_name='publishing_analytics')
    op.drop_table('publishing_analytics')

    op.drop_index('idx_publishing_posts_source', table_name='publishing_posts')
    op.drop_index('idx_publishing_posts_scheduled', table_name='publishing_posts')
    op.drop_index('idx_publishing_posts_platform', table_name='publishing_posts')
    op.drop_index('idx_publishing_posts_status', table_name='publishing_posts')
    op.drop_index('idx_publishing_posts_account', table_name='publishing_posts')
    op.drop_table('publishing_posts')

    op.drop_index('idx_social_accounts_active', table_name='social_accounts')
    op.drop_index('idx_social_accounts_platform', table_name='social_accounts')
    op.drop_table('social_accounts')

    op.drop_index('idx_avatar_videos_created_at', table_name='avatar_videos')
    op.drop_index('idx_avatar_videos_avatar_id', table_name='avatar_videos')
    op.drop_index('idx_avatar_videos_status', table_name='avatar_videos')
    op.drop_table('avatar_videos')
