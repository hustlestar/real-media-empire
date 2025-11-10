# Clean Schema Implementation Plan

## Overview

Complete database schema redesign with asset-centric architecture. **Clean slate approach** - recreate all migrations from scratch, remove duplicated models, implement production-ready shot/film workflow.

## Goals

1. ✅ **Single Universal Asset Model** - No v2 models, no duplication
2. ✅ **Production-Ready Workflow** - Shot takes, generation history, director control
3. ✅ **Clean Migrations** - Start fresh, remove old baggage
4. ✅ **Backend Startup** - Make telegram token optional, ensure clean startup
5. ✅ **Service Layer** - Update all services to use unified schema

## Current State Analysis

### Existing Models to Consolidate
- `Asset` - Current asset model (has character_id FK - leaky)
- `Character` - Should become asset type
- `FilmProject` - Should become asset type
- `Content` - Should become asset type

### Tables to Keep (Core Infrastructure)
- `workspaces` - Multi-tenancy
- `users` - Authentication
- `content_tags` - Tagging system (can be adapted)

### Tables to Remove/Replace
- `assets` → Replace with `assets_v2` (then rename to `assets`)
- `characters` → Migrate to assets
- `film_projects` → Migrate to assets
- `content_items` → Migrate to assets

## Phase 1: Clean Slate Database Schema

### Step 1: Backup and Clear Migrations

```bash
# Backup existing alembic versions
mkdir -p director-ui/alembic/versions_old
mv director-ui/alembic/versions/*.py director-ui/alembic/versions_old/

# Keep alembic.ini and env.py
```

### Step 2: Create Initial Migration

Single migration that creates complete schema:

**Tables:**
1. **`workspaces`** - Multi-tenancy (keep existing)
2. **`users`** - Authentication (keep existing)
3. **`assets`** - Universal asset storage
4. **`asset_relationships`** - Asset graph
5. **`asset_collections`** - Grouping (projects, libraries)
6. **`asset_collection_members`** - Collection membership
7. **`tags`** - Universal tagging
8. **`asset_tags`** - Asset tagging (many-to-many)

### Step 3: Update Models

**`director-ui/src/data/models.py`** - Single clean file:

```python
# Keep: Base, Workspace, User

# Remove: Asset (old), Character, FilmProject, Content

# Add: UniversalAsset, AssetRelationship, AssetCollection, etc.
```

## Phase 2: Make Backend Optional Dependencies

### Telegram Token Optional

**`director-ui/src/core/config.py`:**

```python
class Config:
    # Required
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field(..., env="SECRET_KEY")

    # Optional - Telegram
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, env="TELEGRAM_CHAT_ID")

    # Optional - AI Providers
    fal_api_key: Optional[str] = Field(None, env="FAL_API_KEY")
    replicate_api_token: Optional[str] = Field(None, env="REPLICATE_API_TOKEN")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")

    def __init__(self):
        # Don't fail startup if optional keys missing
        # Log warnings instead
        if not self.telegram_bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set - bot features disabled")
```

**Backend startup checks:**
- Only initialize services if their keys are present
- Gracefully disable features with missing keys
- Log clear warnings about disabled features

## Phase 3: Service Layer Refactor

### Consolidate Services

**Before:**
- `content_service.py` - Content management
- `character_service.py` - Character management
- `film_service.py` - Film management
- `asset_service_v2.py` - New asset service

**After:**
- `asset_service.py` - Universal asset management (single service)
- Helper methods for specific asset types
- Type-safe wrappers for film/shot/character operations

### Asset Service Structure

```python
class AssetService:
    # Core CRUD
    async def create_asset(...)
    async def get_asset(...)
    async def update_asset(...)
    async def delete_asset(...)

    # Relationships
    async def create_relationship(...)
    async def get_children(...)
    async def get_parents(...)

    # Type-specific helpers
    async def create_character(...)  # Wrapper for create_asset(type='character_ref')
    async def create_shot(...)
    async def create_shot_take(...)
    async def get_selected_take(shot_id)

    # Film workflow
    async def create_film(...)
    async def add_shot_to_film(...)
    async def generate_shot_take(...)
    async def select_take(...)
    async def get_film_structure(...)
```

## Phase 4: Migration Strategy

### Option A: Fresh Start (Recommended for Development)

```bash
# Drop entire database
docker compose down -v  # if using docker
psql -U postgres -c "DROP DATABASE director_ui;"
psql -U postgres -c "CREATE DATABASE director_ui;"

# Run fresh migration
cd director-ui
alembic upgrade head

# Seed with test data
python scripts/seed_test_data.py
```

### Option B: Migration Script (For Production)

Create data migration script that:
1. Exports existing data to JSON
2. Drops old tables
3. Creates new schema
4. Imports data into new schema with type mappings

## Phase 5: Update API Endpoints

### Character Endpoints
```python
# Before: POST /api/characters
# After: POST /api/assets (type=character_ref)
# Or keep: POST /api/characters (wrapper that calls asset_service.create_character)
```

Keep existing endpoint paths for backward compatibility, but implement using unified asset service internally.

## Phase 6: Frontend Updates

### API Client Regeneration
```bash
cd director-ui/frontend
npm run generate-api
```

### Update TypeScript Types
- ContentResponse → AssetResponse
- Character types use Asset base
- Film types use Asset base

## Implementation Order

### Step 1: Database Schema (30 min)
- [ ] Move old migrations to backup
- [ ] Create fresh initial migration
- [ ] Update models.py (remove duplicates)
- [ ] Test migration runs successfully

### Step 2: Backend Config (15 min)
- [ ] Make telegram token optional
- [ ] Add graceful degradation for missing keys
- [ ] Test backend starts without all keys

### Step 3: Asset Service (45 min)
- [ ] Consolidate into single asset_service.py
- [ ] Remove asset_service_v2.py
- [ ] Add type-specific helper methods
- [ ] Update all imports

### Step 4: Update Existing Services (30 min)
- [ ] CharacterService → Use AssetService internally
- [ ] ContentService → Use AssetService internally
- [ ] Keep high-level APIs same, change implementation

### Step 5: API Endpoints (20 min)
- [ ] Update character generation endpoint
- [ ] Update content endpoints
- [ ] Test all endpoints work

### Step 6: Frontend (20 min)
- [ ] Regenerate API client
- [ ] Fix TypeScript errors
- [ ] Test UI works

### Step 7: Testing (30 min)
- [ ] Test backend startup
- [ ] Test character generation flow
- [ ] Test content extraction flow
- [ ] Test shot/film creation
- [ ] Verify logs appear correctly

**Total Estimated Time: ~3 hours**

## Rollout Plan

### Development (Now)
1. Create clean schema on dev database
2. Update all code
3. Test thoroughly
4. Commit and push

### Staging/Production (Later)
1. Run data migration script
2. Deploy new code
3. Verify all features work
4. Monitor for issues

## Success Criteria

- ✅ Backend starts without errors (even without telegram token)
- ✅ No v2 models in codebase
- ✅ Single Asset model handles all types
- ✅ Character generation works end-to-end
- ✅ Shot/film workflow is clear and functional
- ✅ All logs appear correctly
- ✅ Frontend builds without TypeScript errors
- ✅ All API endpoints respond correctly

## Files to Modify

```
director-ui/
├── alembic/
│   └── versions/
│       └── [new]_initial_schema.py          # Fresh migration
├── src/
│   ├── core/
│   │   └── config.py                         # Make telegram optional
│   ├── data/
│   │   ├── models.py                         # Remove duplicates, single Asset
│   │   └── models_v2.py                      # DELETE
│   ├── services/
│   │   ├── asset_service.py                  # Consolidated universal service
│   │   ├── asset_service_v2.py               # DELETE
│   │   ├── character_service.py              # Update to use AssetService
│   │   └── content_service.py                # Update to use AssetService
│   └── api/
│       └── routers/
│           ├── characters.py                 # Update to use AssetService
│           └── content.py                    # Update to use AssetService
└── frontend/
    └── src/
        └── api/                              # Regenerate
```

## Next Steps

1. **Review architecture docs** - Ensure shot/film workflow is clear
2. **Get approval** - Confirm this approach before implementing
3. **Execute** - Follow implementation order
4. **Test** - Verify everything works
5. **Deploy** - Push to branch and create PR
