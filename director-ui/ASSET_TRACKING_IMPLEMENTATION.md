# Asset Tracking Implementation Guide

**Goal**: Ensure "script, shot, film, video, image - everything is asset and must be preserved and have a way to be reused"

## ✅ Completed Implementation

### 1. Database Schema
- ✅ Added `workspace_id` to characters and assets tables
- ✅ Added `character_id` to assets for character-asset linking
- ✅ Added `source` column to track asset origin (upload, generation, import)
- ✅ Added `generation_cost` column for cost tracking
- ✅ Added `generation_metadata` JSON column for full generation details
- ✅ Migration: `ebd8cad30182_add_workspace_id_to_characters_and_`

### 2. Asset Saver Helper Module
Created `/director-ui/src/api/helpers/asset_saver.py` with:

- ✅ `save_generation_as_asset()` - Generic asset saver
- ✅ `save_script_as_asset()` - Scripts → text assets
- ✅ `save_shot_as_asset()` - Shots → video/image/audio assets
- ✅ `save_film_as_asset()` - Films → video assets
- ✅ `save_audio_as_asset()` - TTS/voice → audio assets

### 3. Character Image Generation
- ✅ Updated `/director-ui/src/api/routers/characters.py`
- ✅ All generated character images auto-saved to assets table
- ✅ Includes full metadata (model, prompt, seed, cost)

## 🔄 Integration Needed

### Scripts (script_writer.py)

**Endpoint**: `/api/script-writer/generate-from-idea`

**Current Behavior**: Saves to `script_generations` table only

**Needed Integration**:
```python
from api.helpers.asset_saver import save_script_as_asset

# After creating ScriptGeneration record
await save_script_as_asset(
    db=db,
    workspace_id=script_gen.workspace_id,
    script_id=script_gen.id,
    script_title=script_gen.output_full_data.get("script", {}).get("title", "Untitled"),
    script_content=json.dumps(script_gen.output_full_data),
    generation_cost=0.0,  # Calculate based on model/tokens
    model="gpt-4o-mini",  # From generation config
    prompt=script_gen.input_idea,
    genre=script_gen.input_genre,
    style=script_gen.input_style
)
```

### Shots (shot generation endpoint - TBD)

**Needed Integration**: When shots are generated with video providers
```python
from api.helpers.asset_saver import save_shot_as_asset

# After shot video generation
assets = await save_shot_as_asset(
    db=db,
    workspace_id=workspace_id,
    shot_id=shot.id,
    shot_name=f"Shot {shot.sequence_order}",
    video_url=shot.video_url,
    image_url=shot.image_url,  # If reference frame exists
    audio_url=shot.audio_url,  # If separate audio exists
    prompt=shot.prompt,
    generation_cost=shot.generation_cost,
    provider="minimax",  # or kling, runway
    model=shot.model,
    duration=shot.duration_seconds,
    thumbnail_url=shot.thumbnail_url,
    character_ids=[char.character_id for char in shot.characters]
)
```

### Films (film generation pipeline)

**Needed Integration**: When complete films are generated
```python
from api.helpers.asset_saver import save_film_as_asset

# After film compilation
asset = await save_film_as_asset(
    db=db,
    workspace_id=film.workspace_id,
    film_id=film.id,
    film_title=film.title,
    video_url=film.output_path,
    generation_cost=film.total_cost,
    duration=sum(shot.duration for shot in film.shots),
    thumbnail_url=film.thumbnail_url,
    provider=film.video_provider,
    shots_count=len(film.shots),
    character_ids=list(set(char.id for shot in film.shots for char in shot.characters))
)
```

### Audio (audio_generation.py, voice_cloning.py)

**Needed Integration**: TTS and voice cloning
```python
from api.helpers.asset_saver import save_audio_as_asset

# After audio generation
asset = await save_audio_as_asset(
    db=db,
    workspace_id=workspace_id,
    name=f"TTS: {text[:50]}...",
    audio_url=audio_url,
    generation_cost=cost,
    provider="elevenlabs",  # or openai, google
    model=model_id,
    text=text,
    voice_id=voice_id,
    duration=duration,
    character_id=character_id if applicable
)
```

## Benefits of Asset Tracking

### 1. Cost Control
```sql
-- Total spent on generation
SELECT SUM(generation_cost) FROM assets WHERE source = 'generation';

-- Cost by type
SELECT type, SUM(generation_cost) as total_cost
FROM assets
WHERE source = 'generation'
GROUP BY type;

-- Cost by character
SELECT c.name, SUM(a.generation_cost) as total_cost
FROM assets a
JOIN characters c ON a.character_id = c.id
GROUP BY c.id, c.name;
```

### 2. Reusability
```sql
-- Find all images for a character
SELECT * FROM assets
WHERE character_id = 'char_uuid'
AND type = 'image';

-- Find all videos with specific tags
SELECT * FROM assets
WHERE tags @> '["cinematic", "outdoor"]'
AND type = 'video';

-- Find scripts by genre
SELECT * FROM assets
WHERE type = 'script'
AND generation_metadata->>'genre' = 'thriller';
```

### 3. Audit Trail
```sql
-- All generation attempts for a workspace
SELECT
    name,
    type,
    generation_cost,
    generation_metadata->>'provider' as provider,
    generation_metadata->>'model' as model,
    created_at
FROM assets
WHERE workspace_id = 'workspace_uuid'
AND source = 'generation'
ORDER BY created_at DESC;

-- Failed vs successful generations
SELECT
    COUNT(*) FILTER (WHERE url IS NOT NULL) as successful,
    COUNT(*) FILTER (WHERE url IS NULL) as failed,
    SUM(generation_cost) as total_spent
FROM assets
WHERE source = 'generation'
AND workspace_id = 'workspace_uuid';
```

### 4. Asset Lineage
```sql
-- Find all derivatives of a source asset
WITH RECURSIVE asset_tree AS (
    SELECT id, name, source_asset_id, 0 as depth
    FROM assets
    WHERE id = 'source_asset_uuid'

    UNION ALL

    SELECT a.id, a.name, a.source_asset_id, at.depth + 1
    FROM assets a
    JOIN asset_tree at ON a.source_asset_id = at.id
)
SELECT * FROM asset_tree;
```

## Asset Types

| Type | Description | Examples |
|------|-------------|----------|
| `image` | Character images, reference frames, thumbnails | Character portraits, storyboard frames |
| `video` | Generated videos, films, shots | Complete films, individual shots |
| `audio` | TTS, voice cloning, music | Character dialogue, narration, soundtracks |
| `script` | Generated scripts, scenes | Full scripts, scene descriptions |
| `text` | Other text content | Prompts, descriptions, notes |

## Metadata Structure

All assets include:

```json
{
  "generation_metadata": {
    "model": "flux-dev",
    "model_name": "FLUX.1 Dev",
    "provider": "fal",
    "prompt": "Full prompt text...",
    "character_id": "uuid",
    "character_name": "Whiskers",
    "generated_at": "2025-11-09T12:30:00"
  },
  "tags": ["ai-generated", "character-image", "flux-dev"],
  "source": "generation",
  "generation_cost": 0.025
}
```

## Testing Asset Saving

After integrating asset saving into an endpoint:

1. Generate content through the endpoint
2. Check assets table:
   ```sql
   SELECT * FROM assets
   WHERE created_at > NOW() - INTERVAL '1 hour'
   ORDER BY created_at DESC;
   ```
3. Verify metadata is complete
4. Verify cost tracking is accurate
5. Verify tags are appropriate
6. Verify workspace_id is set

## Frontend Integration (Future)

Once all generation endpoints save to assets, add:

1. **Assets Library Page**: Browse/search all assets by type/tag/cost
2. **Asset Reuse**: Drag assets into new projects
3. **Cost Dashboard**: Visualize spending by type/character/workspace
4. **Asset Preview**: View asset metadata and generation details
5. **Bulk Operations**: Tag, favorite, delete multiple assets

## Current Status

- ✅ **Images**: Character images auto-saved
- ⏳ **Scripts**: Integration needed in `script_writer.py`
- ⏳ **Shots**: Integration needed in shot generation endpoint
- ⏳ **Films**: Integration needed in film compilation
- ⏳ **Audio**: Integration needed in TTS endpoints

**Commits:**
- `f261a64` - Database schema with workspace isolation and asset tracking
- `bb78dad` - Asset saver helper module with all generation types
