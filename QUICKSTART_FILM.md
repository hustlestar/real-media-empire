# Film Generation Quick Start

Get your first AI-generated film running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- `uv` package manager (already set up)
- FAL.ai API key (required)
- OpenAI API key (required)

## Step 1: Get API Keys

### FAL.ai (Required for image + video)
1. Go to https://fal.ai/dashboard/keys
2. Sign up or log in
3. Click "Create API Key"
4. Copy the key (starts with `fal_`)

### OpenAI (Required for audio)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

## Step 2: Configure Environment

1. **Copy the environment template**:
```bash
cp .env_template .env
```

2. **Edit `.env` and add your keys**:
```env
# Required API keys
FAL_API_KEY=fal_your_key_here
OPEN_AI_API_KEY=sk-your_key_here

# Storage directory (will be created automatically)
FILM_GALLERY_DIR=E:/FILM_GALLERY

# Budget limit (optional, default $10)
FILM_DEFAULT_BUDGET_USD=10.00
```

3. **Save the file**

## Step 3: Set Up Database

Run this once to create the necessary database tables:

```bash
cd src
uv run python -c "from data.film_models import Base; from data.dao import engine; Base.metadata.create_all(engine)"
```

## Step 4: Run Your First Film!

We've provided an example with 5 shots - a short cinematic scene in a Victorian attic.

### Preview the shots:
```bash
# View the shot definitions
cat examples/example_shots.json
```

### Generate the film (budget mode):
```bash
cd src
uv run python -m pipelines.film_generation \
  --film_id "my_first_film" \
  --shots_json_path "../examples/example_shots.json" \
  --budget_limit 1.00
```

**Expected outcome**:
- **Cost**: ~$0.30 (5 shots × ~$0.054 per shot with budget providers)
- **Time**: ~8-10 minutes (image + video generation for 5 shots)
- **Output**: Video files in `E:/FILM_GALLERY/my_first_film/`

### What you'll see:

```
🎬 Starting film generation for: my_first_film
📊 Loaded 5 shot definitions
💰 Estimated cost: $0.27 (within budget of $1.00)

Generating shot 1/5 (shot_001)...
  ✓ Image generated: film_001_img.png ($0.003)
  ✓ Video animated: film_001_vid.mp4 ($0.050)
  Shot 1 complete: $0.053 total

Generating shot 2/5 (shot_002)...
  ✓ Image generated: film_002_img.png ($0.003)
  ✓ Video animated: film_002_vid.mp4 ($0.050)
  ✓ Audio synthesized: film_002_audio.mp3 ($0.001)
  Shot 2 complete: $0.054 total

[... continues for all shots ...]

✅ Film generation complete!
📁 Output: E:/FILM_GALLERY/my_first_film/
💵 Total cost: $0.268
⚡ Cache hits: 0 (first run)
```

## Step 5: Try Premium Quality

Once you've verified it works, try the premium providers for higher quality:

```bash
cd src
uv run python -m pipelines.film_generation \
  --film_id "my_premium_film" \
  --shots_json_path "../examples/example_shots.json" \
  --video_provider kling \
  --budget_limit 5.00
```

**Note**: Premium video (Kling) costs ~$0.92/shot vs $0.05/shot for Minimax.

## Next Steps

### Create Your Own Shots

1. **Copy the example**:
```bash
cp examples/example_shots.json my_custom_shots.json
```

2. **Edit `my_custom_shots.json`** with your own:
   - `enhanced_prompt`: Describe the visual scene
   - `negative_prompt`: What to avoid
   - `dialogue`: Optional spoken words
   - `characters`, `landscapes`, `styles`: For metadata indexing
   - `duration`: Seconds of video

3. **Run your custom film**:
```bash
cd src
uv run python -m pipelines.film_generation \
  --film_id "my_story" \
  --shots_json_path "../my_custom_shots.json"
```

### Understand Your Costs

Each shot typically costs:

**Budget Mode** (Minimax video + OpenAI audio):
- Image: $0.003
- Video (5s): $0.050
- Audio: ~$0.001
- **Total: ~$0.054 per shot**

**Premium Mode** (Kling video + OpenAI audio):
- Image: $0.003
- Video (5s): $0.920
- Audio: ~$0.001
- **Total: ~$0.924 per shot**

### Reuse Assets (Save Money!)

The system automatically caches assets. If you use the same prompt twice, the second time is FREE and INSTANT!

```bash
# First run: generates everything (~$0.30, 10 minutes)
uv run python -m pipelines.film_generation \
  --film_id "film_v1" \
  --shots_json_path "../examples/example_shots.json"

# Second run with same shots: uses cache (FREE, 30 seconds)
uv run python -m pipelines.film_generation \
  --film_id "film_v2" \
  --shots_json_path "../examples/example_shots.json"
```

You'll see:
```
✓ CACHE HIT: saved $0.053 (shot_001)
✓ CACHE HIT: saved $0.053 (shot_002)
...
Total cache savings: $0.268
```

## Troubleshooting

### "Missing API keys"
- Check your `.env` file has `FAL_API_KEY` and `OPEN_AI_API_KEY`
- Make sure there are no spaces around the `=` sign
- Keys should not be in quotes

### "httpx not found"
```bash
uv add httpx
```

### "Budget exceeded"
- Increase `--budget_limit` value
- Or reduce number of shots in your JSON
- Or use cheaper providers (default is already cheapest)

### "Database error"
- Make sure you ran the database setup (Step 3)
- Check PostgreSQL is running
- Verify `.env` has correct `JDBC_*` settings

## Get Help

- **Full documentation**: See `FILM_GENERATION.md`
- **Project overview**: See `CLAUDE.md`
- **Example shots**: See `examples/example_shots.json`

## Estimated First Run

For the included 5-shot example:

| Item | Value |
|------|-------|
| Shots | 5 |
| Total duration | 22 seconds |
| Estimated cost | $0.27 |
| Generation time | 8-10 minutes |
| Cache hits (first run) | 0 |
| Output files | 15 (5 images, 5 videos, 5 audio) |

**Total first-run cost**: Under $0.30 ✅

Enjoy creating AI-generated films! 🎬
