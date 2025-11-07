# Database Migrations

This document explains how to manage database schema migrations for the director-ui project.

## Overview

The project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema management. Migrations are stored in the `alembic/versions/` directory.

## Prerequisites

1. Ensure you have a PostgreSQL database running
2. Set the `DATABASE_URL` environment variable in your `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/director_ui
   ```

## Running Migrations

### Apply All Pending Migrations (Upgrade)

To upgrade your database to the latest schema:

```bash
cd director-ui
uv run alembic upgrade head
```

This will apply all migrations that haven't been applied yet.

### Check Current Migration Status

To see which migrations have been applied:

```bash
cd director-ui
uv run alembic current
```

To see the migration history:

```bash
cd director-ui
uv run alembic history --verbose
```

### Rollback Migrations (Downgrade)

To rollback the last migration:

```bash
cd director-ui
uv run alembic downgrade -1
```

To rollback to a specific revision:

```bash
cd director-ui
uv run alembic downgrade <revision_id>
```

To rollback all migrations:

```bash
cd director-ui
uv run alembic downgrade base
```

## Recent Migrations

### Migration: a1b2c3d4e5f6 - HeyGen and Postiz Tables

**Created:** 2025-01-07

This migration adds support for HeyGen avatar video generation and Postiz multi-platform social media publishing.

**New Tables:**

1. **avatar_videos** - HeyGen avatar video generation tracking
   - Stores video generation requests and results
   - Configuration: aspect ratio, background, voice settings, avatar positioning
   - Status tracking: pending → processing → completed/failed
   - Cost and duration tracking

2. **social_accounts** - Social media platform account management
   - Multi-platform support (TikTok, YouTube, Instagram, Facebook, Twitter, LinkedIn)
   - OAuth credential storage (should be encrypted in production)
   - Account settings and posting schedules
   - Follower count tracking

3. **publishing_posts** - Published and scheduled social media posts
   - Content tracking (video, image, text, carousel)
   - Scheduling support with status management
   - Platform-specific settings
   - Source tracking (links to avatar videos, films, presentations)
   - Foreign key to social_accounts

4. **publishing_analytics** - Post performance metrics
   - Engagement metrics (views, likes, comments, shares, saves)
   - Performance metrics (engagement rate, watch time, completion rate)
   - Audience demographics and traffic sources
   - Foreign key to publishing_posts

**Indexes Created:**
- Performance indexes on status, platform, scheduled dates
- Foreign key indexes for relationships
- Timestamp indexes for queries

**To Apply This Migration:**
```bash
cd director-ui
uv run alembic upgrade a1b2c3d4e5f6
```

**To Rollback This Migration:**
```bash
cd director-ui
uv run alembic downgrade 85562a830bc1
```

## Creating New Migrations

### Manual Migration Creation

To create a new empty migration:

```bash
cd director-ui
uv run alembic revision -m "description_of_changes"
```

This will create a new migration file in `alembic/versions/` with upgrade() and downgrade() functions that you need to implement.

### Auto-generate Migration (Not Currently Configured)

The project uses manual migrations. Auto-generation would require configuring the ORM models properly in `alembic/env.py`.

## Migration File Structure

Each migration file contains:

```python
# Revision identifiers
revision: str = 'unique_id'
down_revision: Union[str, None] = 'previous_migration_id'

def upgrade() -> None:
    """Apply changes to database schema."""
    # Use op.create_table(), op.add_column(), etc.
    pass

def downgrade() -> None:
    """Revert changes (for rollback)."""
    # Use op.drop_table(), op.drop_column(), etc.
    pass
```

## Best Practices

1. **Always test migrations** on a development database before production
2. **Backup your database** before running migrations in production
3. **Write downgrade functions** to allow rollback if needed
4. **Use comments** on columns to document their purpose
5. **Create indexes** for frequently queried columns
6. **Use transactions** - Alembic wraps migrations in transactions by default
7. **Test rollback** - Always test that downgrade() works correctly

## Common Operations

### Creating a Table

```python
def upgrade() -> None:
    op.create_table(
        'table_name',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id', name='pk_table_name')
    )
    op.create_index('idx_table_name_field', 'table_name', ['name'])

def downgrade() -> None:
    op.drop_index('idx_table_name_field', table_name='table_name')
    op.drop_table('table_name')
```

### Adding a Column

```python
def upgrade() -> None:
    op.add_column('table_name',
                  sa.Column('new_column', sa.String(50), nullable=True))

def downgrade() -> None:
    op.drop_column('table_name', 'new_column')
```

### Creating an Index

```python
def upgrade() -> None:
    op.create_index('idx_table_field', 'table_name', ['field_name'])

def downgrade() -> None:
    op.drop_index('idx_table_field', table_name='table_name')
```

## Troubleshooting

### Error: Target database is not up to date

This means there are pending migrations. Run:
```bash
uv run alembic upgrade head
```

### Error: Can't locate revision identified by 'xxx'

The migration history is out of sync. Check:
```bash
uv run alembic current
uv run alembic history
```

### Error: Table already exists

The database has tables that weren't created through migrations. Options:
1. Drop the table and re-run migrations
2. Mark the migration as already applied: `uv run alembic stamp <revision>`

### Error: Database connection refused

Check:
1. PostgreSQL is running
2. DATABASE_URL is correct in `.env`
3. Database exists
4. User has proper permissions

## Production Deployment

For production deployments:

1. **Backup the database** first
2. **Run migrations during maintenance window** if possible
3. **Test on staging** environment first
4. **Monitor the migration** execution
5. **Have rollback plan** ready

```bash
# Production migration workflow
pg_dump -U user -d database > backup_$(date +%Y%m%d_%H%M%S).sql
uv run alembic upgrade head
# If issues occur:
# uv run alembic downgrade -1
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
