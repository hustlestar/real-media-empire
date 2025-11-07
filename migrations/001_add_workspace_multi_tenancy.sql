-- Migration: 001_add_workspace_multi_tenancy
-- Description: Adds workspace/project organization, platform variants, and publishing tracking
-- Date: 2025-11-07
-- Author: Architecture Improvements (ARCHITECTURE_IMPROVEMENTS.md)

-- ============================================================================
-- 1. CREATE NEW TABLES
-- ============================================================================

-- Workspaces table for multi-tenant isolation
CREATE TABLE IF NOT EXISTS workspaces (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    owner_id INTEGER NOT NULL,
    storage_quota_gb INTEGER DEFAULT 100,
    monthly_budget_usd FLOAT DEFAULT 1000.0,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workspaces_owner ON workspaces(owner_id);
CREATE INDEX idx_workspaces_slug ON workspaces(slug);

-- Projects table for hierarchical organization
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(255) PRIMARY KEY,
    workspace_id VARCHAR(255) NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    type VARCHAR(50) DEFAULT 'campaign',
    parent_project_id VARCHAR(255) REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active',
    description TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(workspace_id, slug)
);

CREATE INDEX idx_projects_workspace ON projects(workspace_id);
CREATE INDEX idx_projects_parent ON projects(parent_project_id);
CREATE INDEX idx_projects_type ON projects(type);

-- Film variants table for platform-specific versions
CREATE TABLE IF NOT EXISTS film_variants (
    id VARCHAR(255) PRIMARY KEY,
    film_project_id VARCHAR(255) NOT NULL REFERENCES film_projects(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    aspect_ratio VARCHAR(10) NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    max_duration_seconds INTEGER,
    output_path VARCHAR(1024),
    status VARCHAR(50) DEFAULT 'pending',
    generation_config JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(film_project_id, platform, aspect_ratio)
);

CREATE INDEX idx_film_variants_project ON film_variants(film_project_id);
CREATE INDEX idx_film_variants_platform ON film_variants(platform);

-- Publishing history table
CREATE TABLE IF NOT EXISTS publish_history (
    id VARCHAR(255) PRIMARY KEY,
    film_variant_id VARCHAR(255) REFERENCES film_variants(id) ON DELETE SET NULL,
    film_project_id VARCHAR(255) NOT NULL REFERENCES film_projects(id) ON DELETE CASCADE,
    account_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    platform_post_id VARCHAR(255),
    post_url VARCHAR(1024),
    title VARCHAR(500),
    description TEXT,
    published_at TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'published',
    metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_publish_history_variant ON publish_history(film_variant_id);
CREATE INDEX idx_publish_history_project ON publish_history(film_project_id);
CREATE INDEX idx_publish_history_platform ON publish_history(platform);
CREATE INDEX idx_publish_history_published_at ON publish_history(published_at);

-- Project-Asset relationship table
CREATE TABLE IF NOT EXISTS project_assets (
    project_id VARCHAR(255) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    asset_id VARCHAR(255) NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    used_in_shots JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, asset_id, role)
);

CREATE INDEX idx_project_assets_project ON project_assets(project_id);
CREATE INDEX idx_project_assets_asset ON project_assets(asset_id);

-- Shot-Character tracking table
CREATE TABLE IF NOT EXISTS shot_characters (
    film_project_id VARCHAR(255) NOT NULL REFERENCES film_projects(id) ON DELETE CASCADE,
    shot_id VARCHAR(255) NOT NULL,
    character_id VARCHAR(255) NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    shot_index INTEGER NOT NULL,
    prominence VARCHAR(50) DEFAULT 'primary',
    screen_time_seconds FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (film_project_id, shot_id, character_id)
);

CREATE INDEX idx_shot_characters_film ON shot_characters(film_project_id);
CREATE INDEX idx_shot_characters_character ON shot_characters(character_id);
CREATE INDEX idx_shot_characters_shot ON shot_characters(shot_id);

-- ============================================================================
-- 2. ALTER EXISTING TABLES
-- ============================================================================

-- Add workspace/project scoping to film_projects
ALTER TABLE film_projects ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(255) REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE film_projects ADD COLUMN IF NOT EXISTS project_id VARCHAR(255) REFERENCES projects(id) ON DELETE SET NULL;
ALTER TABLE film_projects ADD COLUMN IF NOT EXISTS base_film_id VARCHAR(255) REFERENCES film_projects(id);
ALTER TABLE film_projects ADD COLUMN IF NOT EXISTS variant_type VARCHAR(50);
ALTER TABLE film_projects ADD COLUMN IF NOT EXISTS published_at TIMESTAMP;
ALTER TABLE film_projects ADD COLUMN IF NOT EXISTS published_platforms JSON;

CREATE INDEX IF NOT EXISTS idx_film_projects_workspace ON film_projects(workspace_id);
CREATE INDEX IF NOT EXISTS idx_film_projects_project ON film_projects(project_id);
CREATE INDEX IF NOT EXISTS idx_film_projects_base ON film_projects(base_film_id);

-- Add workspace scoping to characters
ALTER TABLE characters ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(255) REFERENCES workspaces(id) ON DELETE CASCADE;
-- NOTE: projects_used column will be deprecated in favor of shot_characters relationship table
-- For now, keep it for backward compatibility, but new code should use shot_characters

CREATE INDEX IF NOT EXISTS idx_characters_workspace ON characters(workspace_id);

-- Remove unique constraint on character name (now unique within workspace)
ALTER TABLE characters DROP CONSTRAINT IF EXISTS characters_name_key;

-- Add workspace scoping and lifecycle tracking to assets
ALTER TABLE assets ADD COLUMN IF NOT EXISTS workspace_id VARCHAR(255) REFERENCES workspaces(id) ON DELETE CASCADE;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS source_asset_id VARCHAR(255) REFERENCES assets(id);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS generation_params JSON;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS cache_key VARCHAR(255);
ALTER TABLE assets ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS access_count INTEGER DEFAULT 0;
ALTER TABLE assets ADD COLUMN IF NOT EXISTS last_accessed_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_assets_workspace ON assets(workspace_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_source ON assets(source_asset_id);
CREATE INDEX IF NOT EXISTS idx_assets_cache_key ON assets(cache_key);
CREATE INDEX IF NOT EXISTS idx_assets_expires_at ON assets(expires_at);

-- ============================================================================
-- 3. DATA MIGRATION (Optional - for existing data)
-- ============================================================================

-- Create a default workspace for existing data
-- NOTE: Uncomment and customize if you have existing data

-- INSERT INTO workspaces (id, name, slug, owner_id, settings)
-- VALUES ('default', 'Default Workspace', 'default', 1, '{}')
-- ON CONFLICT (id) DO NOTHING;

-- Assign existing film_projects to default workspace
-- UPDATE film_projects SET workspace_id = 'default' WHERE workspace_id IS NULL;

-- Assign existing characters to default workspace
-- UPDATE characters SET workspace_id = 'default' WHERE workspace_id IS NULL;

-- Assign existing assets to default workspace
-- UPDATE assets SET workspace_id = 'default' WHERE workspace_id IS NULL;

-- ============================================================================
-- 4. MAKE WORKSPACE_ID NOT NULL (After data migration)
-- ============================================================================

-- NOTE: Uncomment these after running data migration

-- ALTER TABLE film_projects ALTER COLUMN workspace_id SET NOT NULL;
-- ALTER TABLE characters ALTER COLUMN workspace_id SET NOT NULL;
-- ALTER TABLE assets ALTER COLUMN workspace_id SET NOT NULL;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

-- DROP TABLE IF EXISTS shot_characters CASCADE;
-- DROP TABLE IF EXISTS project_assets CASCADE;
-- DROP TABLE IF EXISTS publish_history CASCADE;
-- DROP TABLE IF EXISTS film_variants CASCADE;
-- DROP TABLE IF EXISTS projects CASCADE;
-- DROP TABLE IF EXISTS workspaces CASCADE;
--
-- ALTER TABLE film_projects DROP COLUMN IF EXISTS workspace_id;
-- ALTER TABLE film_projects DROP COLUMN IF EXISTS project_id;
-- ALTER TABLE film_projects DROP COLUMN IF EXISTS base_film_id;
-- ALTER TABLE film_projects DROP COLUMN IF EXISTS variant_type;
-- ALTER TABLE film_projects DROP COLUMN IF EXISTS published_at;
-- ALTER TABLE film_projects DROP COLUMN IF EXISTS published_platforms;
--
-- ALTER TABLE characters DROP COLUMN IF EXISTS workspace_id;
-- ALTER TABLE assets DROP COLUMN IF EXISTS workspace_id;
-- ALTER TABLE assets DROP COLUMN IF EXISTS source_asset_id;
-- ALTER TABLE assets DROP COLUMN IF EXISTS generation_params;
-- ALTER TABLE assets DROP COLUMN IF EXISTS cache_key;
-- ALTER TABLE assets DROP COLUMN IF EXISTS expires_at;
-- ALTER TABLE assets DROP COLUMN IF EXISTS access_count;
-- ALTER TABLE assets DROP COLUMN IF EXISTS last_accessed_at;
