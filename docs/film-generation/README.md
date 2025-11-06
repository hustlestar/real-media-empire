# Film Generation System

Comprehensive AI-powered film generation pipeline for creating cinematic videos from text descriptions.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Cost Management](#cost-management)
- [Asset Reuse](#asset-reuse)
- [API Reference](#api-reference)
- [Examples](#examples)

## Overview

The film generation system automates the creation of cinematic films by:

1. **Image Generation**: Creating high-quality cinematic images from prompts (FAL.ai FLUX)
2. **Video Animation**: Animating images into smooth video clips (Minimax, Kling, Runway)
3. **Audio Synthesis**: Generating dialogue with natural voices (OpenAI TTS, ElevenLabs)
4. **Asset Caching**: Reusing identical assets to minimize costs
5. **Cost Tracking**: Real-time budget monitoring and enforcement
6. **Metadata Indexing**: Multi-dimensional asset discovery and reuse

### Key Features

✅ **Provider Flexibility**: Choose between cheap and premium providers per asset type
✅ **Content-Based Caching**: Identical prompts reuse cached assets (huge cost savings!)
✅ **Budget Enforcement**: Set spending limits, get cost estimates before generation
✅ **Rich Metadata**: Index by character, landscape, style, mood for easy asset discovery
✅ **DRY Architecture**: Single provider interface, extensible design
✅ **Async Processing**: Concurrent generation with configurable limits
✅ **Database Tracking**: Full audit trail of assets, projects, and costs

## Architecture

```
src/film/
├── models.py              # Pydantic data models
├── cache.py               # Content-addressed asset cache
├── metadata.py            # Multi-dimensional metadata index
├── cost_tracker.py        # Budget tracking and enforcement
└── providers/
    ├── base.py            # Abstract provider interfaces
    ├── image_providers.py # FAL, Replicate
    ├── video_providers.py # Minimax, Kling, Runway
    └── audio_providers.py # OpenAI TTS, ElevenLabs

src/pipelines/
├── film_generation.py     # Main pipeline + CLI
├── steps/
│   └── film_steps.py      # ZenML pipeline steps
├── tasks/
│   └── film_tasks.py      # Business logic layer
└── params/
    └── film_params.py     # Pipeline parameters

src/data/
└── film_models.py         # SQLAlchemy database models
```

### Data Flow

```
Shot Definitions (JSON)
    ↓
Load & Configure
    ↓
Cost Estimation ← [Budget Check]
    ↓
Image Generation → [Cache Check] → Image
    ↓
Video Animation → [Cache Check] → Video
    ↓
Audio Synthesis → [Cache Check] → Audio (if has dialogue)
    ↓
Metadata Indexing
    ↓
Cost Recording
    ↓
[Future: Film Composition]
```

## Getting Started

### Prerequisites

1. **Python Environment**: Use `uv` for package management
2. **API Keys**: Obtain keys from providers
3. **Database**: PostgreSQL (for asset tracking)

### Installation

```bash
# Already done during uv migration!
uv sync

# Verify httpx is installed (required for async API calls)
uv add httpx
```

### Configuration

1. **Copy environment template**:
```bash
cp .env_template .env
```

2. **Add API keys to `.env`**:
```env
# Required
FAL_API_KEY=your_fal_key_here
OPEN_AI_API_KEY=your_openai_key_here

# Optional (for premium providers)
REPLICATE_API_KEY=your_replicate_key
RUNWAY_API_KEY=your_runway_key
ELEVENLABS_API_KEY=your_elevenlabs_key

# Storage
FILM_GALLERY_DIR=E:/FILM_GALLERY
FILM_DEFAULT_BUDGET_USD=10.00
```

3. **Get API Keys**:

| Provider | Purpose | Cost | Get Key |
|----------|---------|------|---------|
| FAL.ai | Image gen + Video animation | ~$0.053/shot | https://fal.ai/dashboard/keys |
| OpenAI | Audio synthesis | ~$0.001/shot | https://platform.openai.com/api-keys |
| ElevenLabs | Premium audio | ~$0.01/shot | https://elevenlabs.io/ |
| Replicate | Alt image gen | Varies | https://replicate.com/account |
| Runway | Ultra premium video | $1.20/second! | https://runwayml.com/ |

### Database Setup

```bash
# Run database migrations (if not already done)
cd src
uv run python -c "from data.film_models import Base; from data.dao import engine; Base.metadata.create_all(engine)"
```

## Usage

### 1. Create Shot Definitions

Create a JSON file with your shot definitions:

```json
[
  {
    "shot_id": "shot_001",
    "shot_number": 1,
    "shot_type": "wide",
    "enhanced_prompt": "8K cinematic film production, professional Hollywood color grading, wide shot, Dusty Victorian attic interior, wooden beams, afternoon sunlight",
    "negative_prompt": "cartoon, anime, low quality, amateur",
    "duration": 5,
    "dialogue": null,
    "characters": ["emma"],
    "landscapes": ["attic", "interior"],
    "styles": ["cinematic", "victorian"],
    "mood": "nostalgic",
    "time_of_day": "afternoon"
  },
  {
    "shot_id": "shot_002",
    "shot_number": 2,
    "shot_type": "medium",
    "enhanced_prompt": "8K cinematic, medium shot from waist up, Emma slowly opening attic door, looking curious and nostalgic, dust particles in light",
    "negative_prompt": "cartoon, anime, low quality",
    "duration": 5,
    "dialogue": "I haven't been up here in years...",
    "characters": ["emma"],
    "landscapes": ["attic", "doorway"],
    "styles": ["cinematic", "emotional"],
    "mood": "curious",
    "time_of_day": "afternoon"
  }
]
```

### 2. Run the Pipeline

**Basic usage (cheap providers)**:
```bash
cd src
uv run python -m pipelines.film_generation \
  --film_id "my_first_film" \
  --shots_json_path "../shots.json"
```

**With budget limit**:
```bash
uv run python -m pipelines.film_generation \
  --film_id "budget_film" \
  --shots_json_path "../shots.json" \
  --budget_limit 5.00
```

**Premium providers**:
```bash
uv run python -m pipelines.film_generation \
  --film_id "premium_film" \
  --shots_json_path "../shots.json" \
  --video_provider kling \
  --audio_provider elevenlabs \
  --budget_limit 20.00
```

**Disable caching** (force regeneration):
```bash
uv run python -m pipelines.film_generation \
  --film_id "fresh_film" \
  --shots_json_path "../shots.json" \
  --no_cache
```

### 3. Programmatic Usage

```python
from pipelines.film_generation import run_film_pipeline

final_film = run_film_pipeline(
    film_id="programmatic_test",
    shots_json_path="./shots.json",
    budget_limit=10.00,
    default_video_provider="minimax",
    use_cache=True,
)

print(f"Film generated: {final_film}")
```

## Cost Management

### Provider Cost Comparison

| Asset | Provider | Quality | Cost | Speed |
|-------|----------|---------|------|-------|
| **Image** | FAL (FLUX) | High | $0.003 | Fast (~15s) |
| | Replicate | Varies | $0.005+ | Varies |
| **Video** | Minimax | Good | $0.05/6s | Fast (~60s) |
| | Kling | Better | $1.84/10s | Slow (~180s) |
| | Runway | Best | $1.20/s | Very slow |
| **Audio** | OpenAI TTS | Good | $0.015/1K chars | Fast |
| | ElevenLabs | Excellent | $0.30/1K chars | Fast |

### Typical Shot Costs

**Budget Tier (Minimax + OpenAI)**:
- Image: $0.003
- Video (5s): $0.05
- Audio (20 words): ~$0.001
- **Total per shot: ~$0.054**

**Premium Tier (Kling + ElevenLabs)**:
- Image: $0.003
- Video (5s): $0.92
- Audio (20 words): ~$0.01
- **Total per shot: ~$0.933**

### Budget Strategies

1. **Start Cheap**: Use Minimax + OpenAI for initial iterations
2. **Selective Premium**: Upgrade to Kling only for important shots
3. **Cache Heavily**: Reuse characters, locations, styles across projects
4. **Set Limits**: Always use `--budget_limit` to prevent overspend

### Cost Tracking

View monthly costs:
```python
from film.cost_tracker import get_monthly_costs

costs = get_monthly_costs(2025, 11)
print(f"November 2025 total: ${costs['total_cost']}")
print(f"Projects: {costs['project_count']}")
```

View project costs:
```python
from data.film_models import get_project_cost_summary
from data.dao import SessionLocal

db = SessionLocal()
summary = get_project_cost_summary(db, "my_film_001")
print(summary)
```

## Asset Reuse

### Content-Based Caching

Assets are cached by a hash of their generation parameters:
- Identical prompt + settings = cached asset reused
- Saves money and time
- Automatic cache hit/miss logging

### Metadata Indexing

Find existing assets by criteria:

```python
from film.metadata import MetadataIndex

index = MetadataIndex()

# Find all images of Emma in Victorian attic
assets = index.find_assets(
    characters=['emma'],
    landscapes=['attic'],
    styles=['victorian'],
    asset_type='image'
)

print(f"Found {len(assets)} matching assets")
for asset in assets:
    print(f"- {asset.asset_id}: {asset.prompt[:50]}...")
    print(f"  Used {asset.reuse_count} times, saved ${asset.cost_usd * asset.reuse_count}")
```

### Discover What's Available

```python
# See all characters in your asset library
characters = index.get_all_characters()
print(f"Characters: {characters}")

# See all landscapes
landscapes = index.get_all_landscapes()
print(f"Landscapes: {landscapes}")

# Get index statistics
stats = index.get_index_stats()
print(f"Total assets: {stats['total_assets']}")
```

### Most Reused Assets

```python
from film.metadata import MetadataIndex

index = MetadataIndex()
top_assets = index.get_most_reused_assets(limit=10)

for asset in top_assets:
    roi = asset.cost_usd * (asset.reuse_count - 1)  # Savings from reuse
    print(f"{asset.reuse_count}x: {asset.prompt[:50]}... (ROI: ${roi:.2f})")
```

## API Reference

### Core Classes

#### FilmGenerationTask
```python
from pipelines.tasks.film_tasks import FilmGenerationTask

task = FilmGenerationTask(
    project_id="my_project",
    api_keys={'fal': 'key', 'openai': 'key'},
    use_cache=True
)

# Generate single shot
completed_shot = await task.generate_shot(shot_config)
```

#### AssetCache
```python
from film.cache import AssetCache

cache = AssetCache()

# Check cache stats
stats = cache.get_cache_stats()
print(f"Hit rate: {stats['hit_rate_percent']}%")
print(f"Saved: ${stats['total_cost_saved_usd']}")
```

#### CostTracker
```python
from film.cost_tracker import CostTracker

tracker = CostTracker(
    project_id="my_project",
    budget_limit_usd=Decimal('10.00')
)

# Estimate before generation
estimate = tracker.estimate_project_cost(shot_configs)

# Check if within budget
tracker.check_budget(estimate.total_estimated_cost)  # Raises BudgetExceededError if over
```

#### MetadataIndex
```python
from film.metadata import MetadataIndex

index = MetadataIndex()

# Index an asset
index.index_asset(asset_metadata)

# Find assets
assets = index.find_assets(
    characters=['emma'],
    mood='nostalgic'
)
```

## Examples

### Example 1: 3-Shot Scene (Budget)

**shots.json**:
```json
[
  {"shot_id": "shot_001", "shot_type": "wide", "enhanced_prompt": "...", "duration": 5},
  {"shot_id": "shot_002", "shot_type": "medium", "enhanced_prompt": "...", "duration": 5, "dialogue": "Hello"},
  {"shot_id": "shot_003", "shot_type": "close-up", "enhanced_prompt": "...", "duration": 5}
]
```

**Command**:
```bash
uv run python -m pipelines.film_generation \
  --film_id "scene_001" \
  --shots_json_path "shots.json" \
  --budget_limit 1.00
```

**Expected Cost**: ~$0.16 (3 shots × ~$0.054)
**Time**: ~5 minutes

### Example 2: High-Quality Trailer (Premium)

```bash
uv run python -m pipelines.film_generation \
  --film_id "trailer_v1" \
  --shots_json_path "trailer_shots.json" \
  --video_provider kling \
  --audio_provider elevenlabs \
  --budget_limit 50.00
```

### Example 3: Asset Discovery & Reuse

```python
# Find existing assets of a character
from film.metadata import MetadataIndex

index = MetadataIndex()
emma_assets = index.find_assets(
    characters=['emma'],
    shot_type='close-up'
)

# Reuse in new shot definition
if emma_assets:
    # Use prompt from existing asset
    existing_prompt = emma_assets[0].prompt
    new_shot = {
        "shot_id": "shot_reuse_001",
        "enhanced_prompt": existing_prompt,  # Will hit cache!
        # ...
    }
```

## Troubleshooting

### Common Issues

**1. Missing API Keys**
```
Error: Missing required API keys in .env: FAL_API_KEY
```
Solution: Add keys to `.env` file

**2. Budget Exceeded**
```
BudgetExceededError: Budget exceeded: $12.50 > $10.00
```
Solution: Increase budget or use cheaper providers

**3. httpx Not Found**
```
ModuleNotFoundError: No module named 'httpx'
```
Solution: `uv add httpx`

**4. ZenML Import Errors**
```
ImportError: cannot import name 'BaseParameters'
```
This is expected - the pipeline works without ZenML or with newer ZenML versions

### Performance Tips

1. **Use caching**: First run is slow, subsequent runs with same prompts are instant
2. **Limit concurrency**: Default is 3 concurrent generations (adjustable)
3. **Start small**: Test with 1-2 shots before running full film
4. **Monitor costs**: Check `cost_tracking/` directory regularly

## Future Enhancements

### Planned Features

- [ ] **Film Composition**: FFmpeg integration to assemble shots into final film
- [ ] **Transitions**: Crossfades, cuts, wipes between shots
- [ ] **Audio Mixing**: Background music, sound effects, dialogue mixing
- [ ] **Prompt Templates**: Reusable style templates
- [ ] **Vector Search**: Semantic similarity search for prompts
- [ ] **Web UI**: Browser-based interface for shot definition
- [ ] **YouTube Integration**: Auto-upload finished films

### Contributing

To add a new provider:

1. Inherit from base provider class
2. Implement `generate()`, `estimate_cost()`, `poll_status()`
3. Add to provider registry
4. Update documentation

Example:
```python
from film.providers.base import BaseVideoProvider

class MyVideoProvider(BaseVideoProvider):
    async def generate(self, image_url, prompt, config):
        # Your implementation
        pass

    def estimate_cost(self, config):
        return Decimal('0.10')
```

## Support

- **Documentation**: This file + inline code comments
- **Examples**: See `examples/` directory (TODO)
- **Issues**: Create issue in repo

---

**Built with**:
- Python 3.9+
- Pydantic for validation
- httpx for async HTTP
- SQLAlchemy for database
- ZenML for pipelines (optional)
- uv for package management
