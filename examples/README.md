# Film Generation Examples

This directory contains example shot definitions to help you get started with the film generation pipeline.

## Example Files

### `example_shots.json`

A 5-shot cinematic scene set in a Victorian attic. This example demonstrates:

- **Multiple shot types**: Wide, medium, close-up, extreme close-up
- **Character continuity**: Emma appears throughout the scene
- **Location consistency**: All shots in the same attic setting
- **Emotional progression**: Nostalgia → Curiosity → Anticipation → Mystery → Emotion
- **Dialogue integration**: Some shots include spoken words
- **Metadata richness**: Characters, landscapes, styles, mood, time of day

**Story Summary**: Emma explores her grandmother's attic after years away and discovers her late mother's locket in an old jewelry box.

**Shot Breakdown**:
1. **Wide establishing shot** (5s) - Sets the scene in the dusty attic
2. **Medium shot with dialogue** (5s) - Emma opens the door
3. **Close-up** (4s) - Her hand reaching for the jewelry box
4. **Extreme close-up with dialogue** (3s) - Opening the box latch
5. **Medium close-up with dialogue** (5s) - Emma's emotional reaction

**Total Duration**: 22 seconds
**Estimated Cost** (budget mode): ~$0.27
**Generation Time**: ~8-10 minutes

## How to Use

### 1. Run the Example

```bash
cd src
uv run python -m pipelines.film_generation \
  --film_id "example_attic_scene" \
  --shots_json_path "../examples/example_shots.json" \
  --budget_limit 1.00
```

### 2. Customize the Example

Copy and modify for your own story:

```bash
cp examples/example_shots.json my_story.json
# Edit my_story.json with your prompts
```

### 3. Create From Scratch

Use this template for each shot:

```json
{
  "shot_id": "shot_001",
  "shot_number": 1,
  "shot_type": "wide",
  "enhanced_prompt": "Your detailed visual description here",
  "negative_prompt": "Things to avoid (cartoon, anime, low quality, etc)",
  "duration": 5,
  "dialogue": "Optional spoken words or null",
  "characters": ["character_name"],
  "landscapes": ["location_type"],
  "styles": ["cinematic", "style_tags"],
  "mood": "emotional_tone",
  "time_of_day": "morning/afternoon/evening/night"
}
```

## Shot Types Guide

| Type | Description | Use When |
|------|-------------|----------|
| `wide` | Shows full scene/location | Establishing shots, context |
| `medium` | Waist-up or full body | Character actions, movement |
| `close-up` | Shoulders up | Emotional reactions, detail |
| `extreme-close-up` | Face/object detail | Dramatic emphasis, objects |

## Prompt Writing Tips

### Enhanced Prompt

Start with quality tags, then describe the shot:

```
8K cinematic film production, professional Hollywood color grading,
[shot type], [subject description], [action], [lighting],
[mood/atmosphere], photorealistic, film grain
```

**Good example**:
```
8K cinematic medium shot, Emma a young woman in her 30s with brown hair,
opening an ornate wooden door with curious expression, soft afternoon
light through window, warm amber tones, shallow depth of field,
photorealistic
```

**Bad example** (too vague):
```
A woman opening a door
```

### Negative Prompt

List what you DON'T want:

```
cartoon, anime, low quality, amateur, blurry, distorted, ugly,
deformed, [specific issues like 'extra fingers', 'multiple people']
```

## Dialogue Guidelines

- Keep it natural and concise (under 20 words per shot)
- Match the emotion of the visual
- Consider pacing (audio synthesis adds ~1 second per 10 words)

**Good dialogue**:
- "I haven't been up here in years..."
- "What secrets are you hiding?"
- "Oh my god... it's mother's locket..."

**Bad dialogue** (too long):
- "I can't believe I'm standing here in this dusty old attic after all these years, it brings back so many memories from my childhood..."

## Metadata Best Practices

### Characters
Use consistent names across shots:
```json
"characters": ["emma"]  // NOT ["Emma", "emma", "EMMA"]
```

### Landscapes
Be specific and hierarchical:
```json
"landscapes": ["attic", "interior", "victorian"]
```

### Styles
Mix technical and aesthetic tags:
```json
"styles": ["cinematic", "nostalgic", "dramatic", "realistic"]
```

### Mood
One word that captures the emotion:
```json
"mood": "nostalgic"  // or "tense", "joyful", "mysterious", etc.
```

## Cost Optimization

### Reuse Patterns

The example shots are designed to demonstrate caching:

- Character consistency (Emma) allows reusing character renders
- Same location (attic) allows reusing background elements
- Similar lighting (afternoon) allows reusing light settings

If you run this example twice, the second run will be FREE due to caching!

### Budget vs Premium

**Budget mode** (default: Minimax + OpenAI):
```bash
# Total cost: ~$0.27
uv run python -m pipelines.film_generation \
  --film_id "budget" \
  --shots_json_path "../examples/example_shots.json"
```

**Premium mode** (Kling + ElevenLabs):
```bash
# Total cost: ~$4.70 (17x more expensive!)
uv run python -m pipelines.film_generation \
  --film_id "premium" \
  --shots_json_path "../examples/example_shots.json" \
  --video_provider kling \
  --audio_provider elevenlabs \
  --budget_limit 10.00
```

## Expected Output

After running the example, you'll have:

```
E:/FILM_GALLERY/example_attic_scene/
├── shots/
│   ├── shot_001_image.png
│   ├── shot_001_video.mp4
│   ├── shot_002_image.png
│   ├── shot_002_video.mp4
│   ├── shot_002_audio.mp3
│   ├── shot_003_image.png
│   ├── shot_003_video.mp4
│   ├── shot_004_image.png
│   ├── shot_004_video.mp4
│   ├── shot_004_audio.mp3
│   ├── shot_005_image.png
│   ├── shot_005_video.mp4
│   └── shot_005_audio.mp3
├── metadata/
│   ├── shot_001_metadata.json
│   ├── shot_002_metadata.json
│   ├── shot_003_metadata.json
│   ├── shot_004_metadata.json
│   └── shot_005_metadata.json
└── project_summary.json
```

## Next Steps

1. **Run the example** to verify your setup works
2. **Modify one shot** in the example to see how changes affect output
3. **Create your own story** using this as a template
4. **Experiment with providers** to find your quality/cost sweet spot
5. **Explore metadata queries** to find and reuse your favorite assets

## Need Help?

- **Quick start guide**: See `../QUICKSTART_FILM.md`
- **Full documentation**: See `../FILM_GENERATION.md`
- **Project overview**: See `../CLAUDE.md`

---

**Tip**: Start with 1-2 shots to test, then scale up to full scenes once you're comfortable with the system!
