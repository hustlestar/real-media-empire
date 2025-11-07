# Database Migrations

This directory contains database migration scripts for the Media Empire project.

## Overview

The migration system adds:
- **Workspace multi-tenancy** - Isolate content by brand/client/organization
- **Project hierarchy** - Organize films into campaigns, series, folders
- **Platform variants** - Generate films optimized for different platforms
- **Publishing tracking** - Full audit trail of where content was published
- **Asset lifecycle** - Track asset lineage and enable cache management
- **Character-shot tracking** - Know which characters appear in which shots

## Migration Files

### 001_add_workspace_multi_tenancy.sql

**Description**: Core schema changes for workspace organization and publishing integration

**What it adds**:
- `workspaces` table - Multi-tenant isolation
- `projects` table - Hierarchical project organization
- `film_variants` table - Platform-specific versions (16:9, 9:16, 1:1)
- `publish_history` table - Publishing audit trail
- `project_assets` table - Asset-project relationships
- `shot_characters` table - Character appearance tracking

**What it modifies**:
- `film_projects` - Adds workspace_id, project_id, publishing tracking
- `characters` - Adds workspace_id, removes unique name constraint
- `assets` - Adds workspace_id, lineage tracking, cache management

## How to Apply Migrations

### Option 1: PostgreSQL (Recommended)

```bash
# 1. Connect to your PostgreSQL database
psql -U your_username -d your_database_name

# 2. Run the migration
\i migrations/001_add_workspace_multi_tenancy.sql

# 3. Verify tables were created
\dt

# 4. Check workspace table
SELECT * FROM workspaces;
```

### Option 2: Using psql from command line

```bash
psql -U your_username -d your_database_name -f migrations/001_add_workspace_multi_tenancy.sql
```

### Option 3: For Director-UI Backend (Alembic)

If using the director-ui backend with Alembic:

```bash
cd director-ui
# TODO: Create Alembic migration from models
# For now, use raw SQL approach above
```

## Data Migration Steps

### Step 1: Create Default Workspace

If you have existing data, you'll need to create a default workspace and assign existing records to it.

```sql
-- Create default workspace
INSERT INTO workspaces (id, name, slug, owner_id, settings)
VALUES ('default', 'Default Workspace', 'default', 1, '{}');

-- Assign existing records to default workspace
UPDATE film_projects SET workspace_id = 'default' WHERE workspace_id IS NULL;
UPDATE characters SET workspace_id = 'default' WHERE workspace_id IS NULL;
UPDATE assets SET workspace_id = 'default' WHERE workspace_id IS NULL;

-- Make workspace_id required (after migration)
ALTER TABLE film_projects ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE characters ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE assets ALTER COLUMN workspace_id SET NOT NULL;
```

### Step 2: Verify Migration

```sql
-- Check workspace was created
SELECT * FROM workspaces;

-- Verify existing films have workspace
SELECT id, title, workspace_id FROM film_projects LIMIT 5;

-- Verify tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('workspaces', 'projects', 'film_variants', 'publish_history', 'project_assets', 'shot_characters');
```

## Rollback Instructions

If you need to rollback the migration:

```sql
-- WARNING: This will delete all workspace/project data!

DROP TABLE IF EXISTS shot_characters CASCADE;
DROP TABLE IF EXISTS project_assets CASCADE;
DROP TABLE IF EXISTS publish_history CASCADE;
DROP TABLE IF EXISTS film_variants CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;

-- Remove added columns
ALTER TABLE film_projects DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE film_projects DROP COLUMN IF EXISTS project_id;
ALTER TABLE film_projects DROP COLUMN IF EXISTS base_film_id;
ALTER TABLE film_projects DROP COLUMN IF EXISTS variant_type;
ALTER TABLE film_projects DROP COLUMN IF EXISTS published_at;
ALTER TABLE film_projects DROP COLUMN IF EXISTS published_platforms;

ALTER TABLE characters DROP COLUMN IF EXISTS workspace_id;

ALTER TABLE assets DROP COLUMN IF EXISTS workspace_id;
ALTER TABLE assets DROP COLUMN IF EXISTS source_asset_id;
ALTER TABLE assets DROP COLUMN IF EXISTS generation_params;
ALTER TABLE assets DROP COLUMN IF EXISTS cache_key;
ALTER TABLE assets DROP COLUMN IF EXISTS expires_at;
ALTER TABLE assets DROP COLUMN IF EXISTS access_count;
ALTER TABLE assets DROP COLUMN IF EXISTS last_accessed_at;
```

## Testing the Migration

After applying the migration, test with these queries:

```sql
-- 1. Create a test workspace
INSERT INTO workspaces (id, name, slug, owner_id)
VALUES ('test', 'Test Workspace', 'test', 1);

-- 2. Create a test project
INSERT INTO projects (id, workspace_id, name, slug, type)
VALUES ('test-project', 'test', 'Test Campaign', 'test-campaign', 'campaign');

-- 3. Create a test film with workspace and project
INSERT INTO film_projects (id, workspace_id, project_id, title, status)
VALUES ('test-film', 'test', 'test-project', 'Test Film', 'pending');

-- 4. Verify relationships
SELECT
    w.name as workspace,
    p.name as project,
    f.title as film
FROM workspaces w
JOIN projects p ON p.workspace_id = w.id
JOIN film_projects f ON f.project_id = p.id
WHERE w.id = 'test';

-- 5. Clean up test data
DELETE FROM film_projects WHERE id = 'test-film';
DELETE FROM projects WHERE id = 'test-project';
DELETE FROM workspaces WHERE id = 'test';
```

## Database Configuration

Make sure your `.env` file has the correct database credentials:

```env
JDBC_HOST=localhost
JDBC_PORT=5432
JDBC_USER_NAME=your_username
JDBC_PASSWORD=your_password
JDBC_DATABASE=your_database_name
```

## Next Steps After Migration

1. **Update API endpoints** to filter by workspace
2. **Add workspace selector** to UI
3. **Update film generation** to accept workspace_id
4. **Add publish button** to FilmGenerationPage
5. **Test workspace isolation** - ensure users can only see their workspace content

See `ARCHITECTURE_IMPROVEMENTS.md` for the complete implementation roadmap.

## Troubleshooting

### Error: relation "workspaces" already exists

The migration script uses `IF NOT EXISTS`, so this shouldn't happen. If it does, the table is already created. You can skip that part of the migration.

### Error: column "workspace_id" already exists

Similar to above - column already exists, skip the ALTER TABLE command.

### Foreign key constraint fails

Make sure you're running the migration in order:
1. Create new tables first
2. Then alter existing tables
3. Finally add foreign key constraints

### Can't make workspace_id NOT NULL

You need to assign all existing records to a workspace first:

```sql
-- Create default workspace
INSERT INTO workspaces (id, name, slug, owner_id) VALUES ('default', 'Default', 'default', 1);

-- Update all records
UPDATE film_projects SET workspace_id = 'default' WHERE workspace_id IS NULL;
UPDATE characters SET workspace_id = 'default' WHERE workspace_id IS NULL;
UPDATE assets SET workspace_id = 'default' WHERE workspace_id IS NULL;

-- Now you can make it NOT NULL
ALTER TABLE film_projects ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE characters ALTER COLUMN workspace_id SET NOT NULL;
ALTER TABLE assets ALTER COLUMN workspace_id SET NOT NULL;
```

## Support

For questions or issues:
1. Check `ARCHITECTURE_IMPROVEMENTS.md` for background
2. Review the SQL migration file comments
3. Test queries provided above
4. Check PostgreSQL logs for detailed error messages
