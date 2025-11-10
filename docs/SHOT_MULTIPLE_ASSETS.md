# Shot with Multiple Assets - Usage Guide

## Overview

Shots in the asset-centric architecture can link to **multiple assets** of each type:
- ✅ Multiple characters
- ✅ Multiple audio tracks
- ✅ Multiple scripts/text
- ✅ Multiple generation attempts (takes)

This flexibility enables complex shot composition and iterative refinement.

---

## Asset Relationship Types

### Shot → Character (`uses_character`)
A shot can feature multiple characters appearing together or separately.

```python
# Link multiple characters to a shot
await asset_service.link_shot_assets(
    shot_id=shot_uuid,
    characters=[
        hero_character_id,
        villain_character_id,
        sidekick_character_id
    ]
)
```

**Use Cases:**
- Dialogue scenes with multiple speakers
- Group shots
- Background characters
- Character interactions

### Shot → Audio (`uses_audio`)
A shot can use multiple audio tracks (dialogue, music, sound effects).

```python
# Link multiple audio tracks with sequence
await asset_service.link_shot_assets(
    shot_id=shot_uuid,
    audios=[
        dialogue_audio_id,    # sequence=1
        background_music_id,  # sequence=2
        sound_effects_id      # sequence=3
    ]
)
```

**Use Cases:**
- Dialogue + background music
- Multiple sound effects layers
- Voiceover + ambient sound
- Audio mixing from multiple sources

### Shot → Script/Text (`uses_script`)
A shot can reference multiple scripts or text assets.

```python
# Link multiple scripts
await asset_service.link_shot_assets(
    shot_id=shot_uuid,
    scripts=[
        dialogue_script_id,
        stage_directions_id,
        camera_notes_id
    ]
)
```

**Use Cases:**
- Dialogue script
- Stage directions
- Camera instructions
- Alternative versions
- Translation scripts

---

## Complete Shot Creation Example

### Scenario: Dialogue Scene with 2 Characters

```python
from services.asset_service import AssetService

# Initialize service
asset_service = AssetService(db)

# 1. Create shot (zero shot - text description only)
shot_id = await asset_service.create_shot(
    workspace_id="workspace-123",
    name="Scene 3 - Confrontation",
    description="Hero confronts villain in the alley",
    shot_number="03A",
    camera_angle="medium two-shot",
    duration_target=8.0,
    prompt="Cinematic medium shot, hero and villain facing each other in dark alley"
)

# 2. Link characters
await asset_service.link_shot_assets(
    shot_id=shot_id,
    characters=[
        hero_character_id,
        villain_character_id
    ]
)

# 3. Link audio tracks
await asset_service.link_shot_assets(
    shot_id=shot_id,
    audios=[
        hero_dialogue_id,      # "Why did you betray us?"
        villain_dialogue_id,   # "You were too weak!"
        background_music_id,   # Tension music
        rain_sound_fx_id       # Ambient rain
    ]
)

# 4. Link scripts
await asset_service.link_shot_assets(
    shot_id=shot_id,
    scripts=[
        dialogue_script_id,
        blocking_script_id
    ]
)

# 5. Generate first take
take1_id = await asset_service.create_shot_take(
    shot_id=shot_id,
    attempt_number=1,
    selected=False,
    generation_params={"provider": "minimax", "model": "video-01"},
    generation_cost=0.50
)

# 6. Link generated video to take
video1_id = await asset_service.link_take_video(
    take_id=take1_id,
    video_url="https://cdn.example.com/take1.mp4",
    duration=8.2,
    video_metadata={"width": 1920, "height": 1080, "fps": 24}
)

# 7. Director reviews - not happy, try again
take2_id = await asset_service.create_shot_take(
    shot_id=shot_id,
    attempt_number=2,
    selected=True,  # This one is selected!
    generation_params={"provider": "minimax", "model": "video-01", "seed": 54321},
    quality_score=9.5,
    director_notes="Perfect! Lighting and timing are excellent",
    generation_cost=0.50
)

video2_id = await asset_service.link_take_video(
    take_id=take2_id,
    video_url="https://cdn.example.com/take2.mp4",
    duration=8.1,
    video_metadata={"width": 1920, "height": 1080, "fps": 24}
)
```

---

## Querying Shot Assets

### Get All Characters in Shot
```python
characters = await asset_service.get_child_assets(
    parent_asset_id=shot_id,
    relationship_type="uses_character",
    asset_type="character_ref"
)

for char in characters:
    print(f"Character: {char['name']}")
```

### Get All Audio Tracks in Shot
```python
audios = await asset_service.get_child_assets(
    parent_asset_id=shot_id,
    relationship_type="uses_audio",
    asset_type="audio"
)

# Audios are ordered by sequence
for audio in audios:
    print(f"Audio #{audio['sequence']}: {audio['name']}")
```

### Get All Scripts for Shot
```python
scripts = await asset_service.get_child_assets(
    parent_asset_id=shot_id,
    relationship_type="uses_script",
    asset_type="script"
)
```

### Get All Takes (Generation Attempts)
```python
takes = await asset_service.get_shot_takes(shot_id)

for take in takes:
    metadata = take['asset_metadata']
    selected = metadata.get('selected', False)
    attempt = metadata.get('attempt_number')
    score = metadata.get('quality_score')
    print(f"Take {attempt}: {'✓ SELECTED' if selected else 'alternate'} (score: {score})")
```

### Get Selected Take Video
```python
selected_take = await asset_service.get_selected_take(shot_id)

if selected_take:
    # Get video for this take
    videos = await asset_service.get_child_assets(
        parent_asset_id=UUID(selected_take['id']),
        relationship_type="generated_video",
        asset_type="video"
    )
    if videos:
        print(f"Selected video: {videos[0]['url']}")
```

---

## SQL Queries

### Get Complete Shot Structure
```sql
-- Get shot with all linked assets
SELECT
    s.id as shot_id,
    s.name as shot_name,
    a.id as asset_id,
    a.name as asset_name,
    a.type as asset_type,
    r.relationship_type,
    r.sequence
FROM assets s
JOIN asset_relationships r ON r.parent_asset_id = s.id
JOIN assets a ON a.id = r.child_asset_id
WHERE s.id = :shot_id
  AND s.type = 'shot'
ORDER BY r.relationship_type, r.sequence NULLS LAST;
```

### Get All Characters Used in Shot
```sql
SELECT a.*
FROM assets a
JOIN asset_relationships r ON r.child_asset_id = a.id
WHERE r.parent_asset_id = :shot_id
  AND r.relationship_type = 'uses_character'
  AND a.type = 'character_ref'
ORDER BY a.name;
```

### Get Audio Tracks in Layering Order
```sql
SELECT a.*, r.sequence
FROM assets a
JOIN asset_relationships r ON r.child_asset_id = a.id
WHERE r.parent_asset_id = :shot_id
  AND r.relationship_type = 'uses_audio'
  AND a.type = 'audio'
ORDER BY r.sequence NULLS LAST;
```

### Get Selected Take with Video
```sql
SELECT
    take.id as take_id,
    take.name as take_name,
    take.asset_metadata->>'attempt_number' as attempt,
    take.asset_metadata->>'quality_score' as score,
    video.url as video_url,
    video.duration
FROM assets shot
JOIN asset_relationships rt ON rt.parent_asset_id = shot.id AND rt.relationship_type = 'generation_attempt'
JOIN assets take ON take.id = rt.child_asset_id AND take.type = 'shot_take'
JOIN asset_relationships rv ON rv.parent_asset_id = take.id AND rv.relationship_type = 'generated_video'
JOIN assets video ON video.id = rv.child_asset_id AND video.type = 'video'
WHERE shot.id = :shot_id
  AND take.asset_metadata->>'selected' = 'true';
```

---

## Database Structure

### Shot Asset
```json
{
  "id": "shot-uuid",
  "type": "shot",
  "name": "Scene 3 - Confrontation",
  "asset_metadata": {
    "shot_number": "03A",
    "description": "Hero confronts villain in the alley",
    "camera_angle": "medium two-shot",
    "duration_target": 8.0,
    "prompt": "Cinematic medium shot..."
  }
}
```

### Relationships
```
shot-uuid
  ├── uses_character → hero-uuid
  ├── uses_character → villain-uuid
  ├── uses_audio (seq=1) → dialogue1-uuid
  ├── uses_audio (seq=2) → dialogue2-uuid
  ├── uses_audio (seq=3) → music-uuid
  ├── uses_audio (seq=4) → rain-uuid
  ├── uses_script → dialogue-script-uuid
  ├── uses_script → blocking-script-uuid
  ├── generation_attempt (seq=1) → take1-uuid → generated_video → video1-uuid
  └── generation_attempt (seq=2) → take2-uuid → generated_video → video2-uuid ✓ selected
```

---

## Best Practices

### 1. Character Consistency
```python
# Always link characters that appear in the shot
# This enables:
# - Tracking which characters appear in which shots
# - Character usage analytics
# - Consistent visual style across shots
await asset_service.link_shot_assets(
    shot_id=shot_id,
    characters=[char_id for char_id in appearing_characters]
)
```

### 2. Audio Layering
```python
# Use sequence numbers for audio mixing order
# Lower sequence = lower layer (e.g., background music)
# Higher sequence = higher layer (e.g., dialogue on top)
await asset_service.link_shot_assets(
    shot_id=shot_id,
    audios=[
        background_music_id,  # seq=1 (bottom layer)
        ambient_sounds_id,    # seq=2
        sound_effects_id,     # seq=3
        dialogue_id           # seq=4 (top layer)
    ]
)
```

### 3. Multiple Takes
```python
# Always create multiple takes for comparison
# Mark only one as selected
for i in range(3):
    take_id = await asset_service.create_shot_take(
        shot_id=shot_id,
        attempt_number=i+1,
        selected=(i == 2),  # Select take 3
        generation_cost=0.50
    )
```

### 4. Script Variants
```python
# Keep multiple script versions for A/B testing or localization
await asset_service.link_shot_assets(
    shot_id=shot_id,
    scripts=[
        english_script_id,
        spanish_script_id,
        director_notes_id
    ]
)
```

---

## Benefits

✅ **Flexibility**: Complex shots with multiple elements
✅ **Reusability**: Assets can be used in multiple shots
✅ **Versioning**: Multiple takes preserved with metadata
✅ **Collaboration**: Directors can review and select best takes
✅ **Cost Tracking**: Every generation tracked with cost
✅ **Audit Trail**: Complete history of all attempts
✅ **Analytics**: Track character usage, generation stats
✅ **Scalability**: Add new relationship types easily

---

## Migration from Old Schema

Old schema had `shot_characters` table. New schema uses `asset_relationships`:

### Before (Old Schema)
```sql
CREATE TABLE shot_characters (
    shot_id UUID,
    character_id UUID
);
```

### After (New Schema)
```sql
-- Now it's just a relationship!
INSERT INTO asset_relationships (
    parent_asset_id,  -- shot_id
    child_asset_id,   -- character_id
    relationship_type
) VALUES (
    :shot_id,
    :character_id,
    'uses_character'
);
```

**Benefits of new approach:**
- Universal pattern for all asset types
- Supports metadata per relationship
- Supports sequences for ordering
- Type-safe with relationship_type
- No need for join tables per type
