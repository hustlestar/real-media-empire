# Shot & Film Architecture - Production Perspective

## Film Production Workflow

### 1. Pre-Production (Planning)
```
Film Project → Scenes → Shots (text descriptions)
```

- **Film Project**: Overall creative work with title, synopsis
- **Scene**: Optional logical grouping of related shots
- **Shot**: Creative intent - text description, camera angle, duration
  - Links to characters that should appear
  - Links to audio/music to use
  - Links to other reference assets

### 2. Production (Generation)

```
Shot → Generate → Shot Take #1 → Video Asset
Shot → Regenerate → Shot Take #2 → Video Asset
Shot → Regenerate → Shot Take #3 → Video Asset (selected for final)
```

- **Shot Take**: A single generation attempt (like film "takes")
- Each take creates a Video asset
- Multiple takes per shot (edit and try again)
- One take marked as "selected" for final cut

### 3. Post-Production (Assembly)

```
Film → [Shot #1 (selected take), Shot #2 (selected take), ...] → Final Video
```

- Assemble selected takes in sequence
- Apply transitions, effects
- Export final video

## Asset Types

### Core Types

1. **`film`** - Overall project
   ```json
   {
     "title": "My Short Film",
     "synopsis": "A hero's journey",
     "total_duration": 120.0,
     "status": "in_production"
   }
   ```

2. **`scene`** - Optional shot grouping
   ```json
   {
     "scene_number": 1,
     "setting": "desert landscape",
     "description": "opening sequence"
   }
   ```

3. **`shot`** - Creative intent (zero shot = text only)
   ```json
   {
     "shot_number": "01A",
     "description": "Hero walks into sunset",
     "camera_angle": "wide shot",
     "duration_target": 5.0,
     "prompt": "cinematic wide shot of hero walking into golden sunset"
   }
   ```

4. **`shot_take`** - Generation attempt
   ```json
   {
     "attempt_number": 3,
     "selected": true,
     "generation_params": {
       "provider": "minimax",
       "model": "video-01",
       "seed": 12345
     },
     "quality_score": 8.5,
     "director_notes": "Perfect! Use this one"
   }
   ```

5. **`video`** - Generated video file
   ```json
   {
     "width": 1920,
     "height": 1080,
     "fps": 24,
     "codec": "h264",
     "format": "mp4"
   }
   ```

6. **`audio`** - Sound/music
7. **`image`** - Still image
8. **`character_ref`** - Character definition
9. **`text`** - Script/content

## Relationship Patterns

### Film Structure
```
Film
├── contains_shot (seq=1) → Shot #1
│   ├── uses_character → Character A
│   ├── uses_audio → Background Music
│   ├── generation_attempt (seq=1) → Shot Take #1 → generated_video → Video Asset
│   ├── generation_attempt (seq=2) → Shot Take #2 → generated_video → Video Asset
│   └── generation_attempt (seq=3) → Shot Take #3 → generated_video → Video Asset ✓ selected
├── contains_shot (seq=2) → Shot #2
│   └── ...
└── final_edit → Final Assembled Video
```

### Relationship Types

| Relationship Type | Parent | Child | Description |
|------------------|---------|--------|-------------|
| `contains_shot` | Film/Scene | Shot | Shot belongs to film/scene |
| `uses_character` | Shot | Character | Shot features character |
| `uses_audio` | Shot | Audio | Shot uses audio |
| `uses_asset` | Shot | Any Asset | Shot uses any asset |
| `generation_attempt` | Shot | Shot Take | Take is attempt to generate shot |
| `generated_video` | Shot Take | Video | Take produced this video |
| `final_edit` | Film | Video | Final assembled video |
| `derived_from` | Video | Video | Video edited from original |
| `variant_of` | Asset | Asset | Alternative version |

## Shot Lifecycle Example

```python
# 1. Create shot with description (zero shot)
shot_id = await asset_service.create_asset(
    workspace_id="ws-123",
    asset_type="shot",
    name="Shot 01A - Hero Entrance",
    metadata={
        "shot_number": "01A",
        "description": "Hero walks into sunset",
        "camera_angle": "wide shot",
        "duration_target": 5.0,
        "prompt": "cinematic wide shot..."
    }
)

# 2. Link character to shot
await asset_service.create_relationship(
    parent_asset_id=shot_id,
    child_asset_id=hero_character_id,
    relationship_type="uses_character"
)

# 3. First generation attempt
take1_id = await asset_service.create_asset(
    workspace_id="ws-123",
    asset_type="shot_take",
    name="Shot 01A - Take 1",
    metadata={
        "attempt_number": 1,
        "selected": False,
        "generation_params": {...}
    },
    generation_cost=0.50
)

video1_id = await asset_service.create_asset(
    workspace_id="ws-123",
    asset_type="video",
    name="Shot 01A - Take 1 Video",
    url="https://cdn.../video1.mp4",
    duration=5.2,
    metadata={"width": 1920, "height": 1080, "fps": 24}
)

await asset_service.create_relationship(
    parent_asset_id=shot_id,
    child_asset_id=take1_id,
    relationship_type="generation_attempt",
    sequence=1
)

await asset_service.create_relationship(
    parent_asset_id=take1_id,
    child_asset_id=video1_id,
    relationship_type="generated_video"
)

# 4. Second generation attempt (edit and try again)
take2_id = ...  # Same process
# Mark take 2 as selected
await asset_service.update_asset(
    asset_id=take2_id,
    metadata={"selected": True}
)

# 5. Query: Get all takes for a shot
takes = await asset_service.get_child_assets(
    parent_asset_id=shot_id,
    relationship_type="generation_attempt",
    asset_type="shot_take"
)

# 6. Query: Get selected take video
selected_take = [t for t in takes if t['metadata'].get('selected')]
if selected_take:
    video = await asset_service.get_child_assets(
        parent_asset_id=selected_take[0]['id'],
        relationship_type="generated_video",
        asset_type="video"
    )
```

## Benefits

✅ **Clear Lineage**: Film → Shot → Take → Video hierarchy
✅ **Generation History**: All takes preserved with metadata
✅ **Flexible Editing**: Try different generations without losing data
✅ **Asset Reusability**: Characters, audio can be used in multiple shots
✅ **Production Metrics**: Track costs, attempts, quality per shot
✅ **Director Control**: Mark selected takes, add notes
✅ **Scalability**: Add scenes, additional asset types easily

## Query Patterns

### Get film structure with all shots
```sql
SELECT a.*, r.sequence
FROM assets_v2 a
JOIN asset_relationships r ON r.child_asset_id = a.id
WHERE r.parent_asset_id = :film_id
  AND r.relationship_type = 'contains_shot'
  AND a.type = 'shot'
ORDER BY r.sequence;
```

### Get all characters used in a shot
```sql
SELECT a.*
FROM assets_v2 a
JOIN asset_relationships r ON r.child_asset_id = a.id
WHERE r.parent_asset_id = :shot_id
  AND r.relationship_type = 'uses_character'
  AND a.type = 'character_ref';
```

### Get selected take video for shot
```sql
SELECT v.*
FROM assets_v2 v
JOIN asset_relationships rv ON rv.child_asset_id = v.id AND rv.relationship_type = 'generated_video'
JOIN assets_v2 take ON take.id = rv.parent_asset_id AND take.type = 'shot_take'
JOIN asset_relationships rt ON rt.child_asset_id = take.id AND rt.relationship_type = 'generation_attempt'
WHERE rt.parent_asset_id = :shot_id
  AND take.metadata->>'selected' = 'true'
  AND v.type = 'video';
```

### Get total generation cost for film
```sql
SELECT SUM(a.generation_cost) as total_cost
FROM assets_v2 a
JOIN asset_relationships r ON r.child_asset_id = a.id
WHERE r.parent_asset_id = :film_id
  AND a.generation_cost IS NOT NULL;
```
