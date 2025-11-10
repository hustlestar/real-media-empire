# Asset-Centric Database Schema

## Philosophy

**Everything is an Asset.** Scripts, text, audio, video, images, shots, films, characters - all are Assets with different types. This enables universal reusability and composition.

## Core Tables

### 1. `assets` (Universal Content)

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Core fields (minimal, universal)
    type VARCHAR(50) NOT NULL,  -- script, text, audio, video, image, shot, film, character_ref, scene
    name VARCHAR(255) NOT NULL,

    -- Storage
    url TEXT,                   -- Public CDN URL
    file_path TEXT,             -- Local filesystem path
    size BIGINT,                -- File size in bytes
    duration FLOAT,             -- Duration for audio/video (seconds)

    -- Metadata (type-specific data goes here)
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',

    -- Generation tracking
    source VARCHAR(50),         -- upload, generation, import, derivative
    generation_cost FLOAT,
    generation_metadata JSONB,  -- Provider, model, prompt, seed

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assets_workspace_id ON assets(workspace_id);
CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_source ON assets(source);
CREATE INDEX idx_assets_metadata ON assets USING gin(metadata);
CREATE INDEX idx_assets_tags ON assets USING gin(tags);
```

**Type Examples & Metadata:**

- **image**: `{width, height, format, thumbnail_url}`
- **video**: `{width, height, format, fps, codec, thumbnail_url}`
- **audio**: `{format, sample_rate, channels, bitrate}`
- **text**: `{language, word_count, char_count, detected_language}`
- **script**: `{language, scenes, shot_count, estimated_duration}`
- **shot**: `{scene_id, sequence, camera_angle, duration, prompt}`
- **film**: `{status, total_duration, shot_count, platform_variants}`
- **character_ref**: `{description, attributes, consistency_prompt}`
- **scene**: `{script_id, duration, shot_count, setting}`

### 2. `asset_relationships` (Universal Linking)

```sql
CREATE TABLE asset_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    child_asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,

    relationship_type VARCHAR(50) NOT NULL,
    -- used_in, derived_from, variant_of, part_of, reference_for, generated_from

    sequence INTEGER,           -- Order when relationship implies sequence
    metadata JSONB DEFAULT '{}', -- Relationship-specific data

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(parent_asset_id, child_asset_id, relationship_type)
);

CREATE INDEX idx_asset_rel_parent ON asset_relationships(parent_asset_id);
CREATE INDEX idx_asset_rel_child ON asset_relationships(child_asset_id);
CREATE INDEX idx_asset_rel_type ON asset_relationships(relationship_type);
```

**Relationship Examples:**

- Film (parent) → Shot (child): `relationship_type='part_of'`, `sequence=1`
- Shot (parent) → Video (child): `relationship_type='generated_from'`
- Character (parent) → Image (child): `relationship_type='reference_for'`
- Image Original (parent) → Image Upscaled (child): `relationship_type='derived_from'`
- Script (parent) → Scene (child): `relationship_type='part_of'`, `sequence=1`

### 3. `asset_collections` (Grouping & Organization)

```sql
CREATE TABLE asset_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,  -- project, character, storyboard, library
    description TEXT,
    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_collections_workspace ON asset_collections(workspace_id);
CREATE INDEX idx_collections_type ON asset_collections(type);
```

### 4. `asset_collection_members` (Collection Membership)

```sql
CREATE TABLE asset_collection_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES asset_collections(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,

    sequence INTEGER,           -- Order within collection
    metadata JSONB DEFAULT '{}', -- Member-specific data

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(collection_id, asset_id)
);

CREATE INDEX idx_collection_members_collection ON asset_collection_members(collection_id);
CREATE INDEX idx_collection_members_asset ON asset_collection_members(asset_id);
```

## Migration Strategy

### Phase 1: Create New Tables
1. Create `assets`, `asset_relationships`, `asset_collections`, `asset_collection_members`
2. Keep existing tables for backward compatibility

### Phase 2: Migrate Data
1. Migrate existing Asset records to new schema
2. Convert Characters → Assets (type='character_ref')
3. Convert FilmProjects → Assets (type='film') + Collections
4. Convert Shots → Assets (type='shot') with relationships
5. Convert Content → Assets (type='text')

### Phase 3: Update Application Code
1. Create new Asset service with universal methods
2. Update film generation to use Asset relationships
3. Update character generation to use Asset collections
4. Migrate all consumers to new schema

### Phase 4: Cleanup
1. Drop old tables once migration verified
2. Remove old model classes

## Benefits

✅ **Universal Reusability**: Any asset can be used in any context
✅ **Flexible Composition**: Relationships define how assets connect
✅ **Type Safety**: Asset type + metadata validation
✅ **Query Simplicity**: One table for all content queries
✅ **Version Control**: Derived_from relationships track lineage
✅ **Cost Attribution**: All generation costs in one place
✅ **Workspace Isolation**: Single workspace_id for all content

## Example Queries

### Get all shots for a film
```sql
SELECT a.*
FROM assets a
JOIN asset_relationships r ON r.child_asset_id = a.id
WHERE r.parent_asset_id = :film_id
  AND r.relationship_type = 'part_of'
  AND a.type = 'shot'
ORDER BY r.sequence;
```

### Get all reference images for a character
```sql
SELECT a.*
FROM assets a
JOIN asset_relationships r ON r.child_asset_id = a.id
WHERE r.parent_asset_id = :character_id
  AND r.relationship_type = 'reference_for'
  AND a.type = 'image';
```

### Find all assets using a specific audio track
```sql
SELECT a.*
FROM assets a
JOIN asset_relationships r ON r.parent_asset_id = a.id
WHERE r.child_asset_id = :audio_id
  AND r.relationship_type = 'used_in';
```

### Get complete film structure
```sql
WITH RECURSIVE film_tree AS (
    -- Root: the film itself
    SELECT id, type, name, metadata, 0 as depth
    FROM assets
    WHERE id = :film_id

    UNION ALL

    -- Recursively get children
    SELECT a.id, a.type, a.name, a.metadata, ft.depth + 1
    FROM assets a
    JOIN asset_relationships r ON r.child_asset_id = a.id
    JOIN film_tree ft ON r.parent_asset_id = ft.id
)
SELECT * FROM film_tree ORDER BY depth, type;
```
