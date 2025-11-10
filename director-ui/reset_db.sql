-- Reset database script
-- Run this to drop all tables and start fresh with the new migration

-- Drop all tables (in dependency order)
DROP TABLE IF EXISTS content_tags CASCADE;
DROP TABLE IF EXISTS content_items CASCADE;
DROP TABLE IF EXISTS asset_tags CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS asset_collection_members CASCADE;
DROP TABLE IF EXISTS asset_collections CASCADE;
DROP TABLE IF EXISTS asset_relationships CASCADE;
DROP TABLE IF EXISTS assets CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;

-- Drop any other tables that might exist from old schema
DROP TABLE IF EXISTS film_projects CASCADE;
DROP TABLE IF EXISTS characters CASCADE;
DROP TABLE IF EXISTS presentations CASCADE;
DROP TABLE IF EXISTS avatar_videos CASCADE;
DROP TABLE IF EXISTS social_accounts CASCADE;
DROP TABLE IF EXISTS publishing_posts CASCADE;
DROP TABLE IF EXISTS publishing_analytics CASCADE;
DROP TABLE IF EXISTS film_shots CASCADE;
DROP TABLE IF EXISTS shot_reviews CASCADE;
DROP TABLE IF EXISTS script_generations CASCADE;
DROP TABLE IF EXISTS scenes CASCADE;
DROP TABLE IF EXISTS shot_generations CASCADE;
DROP TABLE IF EXISTS generation_sessions CASCADE;
DROP TABLE IF EXISTS generation_notes CASCADE;

-- Drop Alembic version table to start fresh
DROP TABLE IF EXISTS alembic_version CASCADE;
