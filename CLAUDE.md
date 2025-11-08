# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Media Empire is a Python-based automated content creation system for generating and publishing YouTube videos and shorts. It uses ZenML for pipeline orchestration, MoviePy for video editing, OpenAI/ChatGPT for content generation, and integrates with various TTS providers and YouTube API.

The project now includes a comprehensive **Production Platform** with 21 professional features for automated video production, editing, and optimization. See `docs/PRODUCTION_PLATFORM_SUMMARY.md` for complete details.

## Documentation

All project documentation should be placed in the `docs/` directory:

```
docs/
├── PRODUCTION_PLATFORM_SUMMARY.md  # Complete production platform overview
└── [other documentation files]
```

**Documentation Guidelines:**
- ✅ **DO** place all new documentation in `docs/` directory
- ✅ **DO** use descriptive filenames (UPPER_SNAKE_CASE.md)
- ✅ **DO** keep CLAUDE.md and README.md in project root
- ❌ **DON'T** create documentation files in project root
- ❌ **DON'T** create temporary analysis or status files

## Core Architecture

### Pipeline System (ZenML-based)

The project is organized around ZenML pipelines that orchestrate multi-step workflows:

- **Pipeline definitions**: `src/pipelines/` - Main pipeline entry points
- **Steps**: `src/pipelines/steps/` - Reusable atomic operations (video, audio, GPT, publishing, quotes)
- **Tasks**: `src/pipelines/tasks/` - Business logic components
- **Parameters**: `src/pipelines/params/` - Pipeline configuration via `PipelineParams` class

Key pipelines:
- `shorts_pipeline.py` - Complete end-to-end shorts generation and upload
- `quotes_shorts_generate.py` - Generate quote-based shorts videos
- `shorts_generate.py` - Generate shorts from swamp (staging area)
- `shorts_publish.py` - Publish shorts to YouTube from swamp
- `publish_pipeline.py` - Generic publishing pipeline
- `film_generation.py` - AI-powered film/video generation with multiple providers
- `pptx_generation.py` - AI-powered PowerPoint presentation generation

### Data Flow Pattern

The system follows a "data lake" pattern:
- **SWAMP**: Staging area for generated videos before publishing
- **LAKE**: Archive of published content
- Videos move from generation → swamp → YouTube → lake

### Key Modules

1. **Video Processing** (`src/video/`)
   - `new.py` - Text animation effects using MoviePy
   - `video_transitions.py` - Transition effects between clips
   - `_shorts.py` - Core shorts video creation
   - `movie.py` - Full-length video editing
   - Uses MoviePy (imported as `from moviepy.editor import *`)

2. **Audio** (`src/audio/`)
   - Multiple TTS integrations: Google TTS, ElevenLabs, CyberVoice, Descript
   - Base interface: `text_to_speech.py` with `TextToSpeech` ABC
   - `audio_processor.py` - Audio manipulation and effects

3. **Text/Content** (`src/text/`)
   - `chat_gpt.py` - OpenAI integration for content generation
   - `gpt_templates.py` - Prompt templates
   - `helpers.py` - Text utilities

4. **Social Publishing** (`src/social/`)
   - `you_tube.py` - YouTube API integration via `YouTubeUploader` class
   - OAuth2 credentials stored in `jack/oath/`

5. **Data Layer** (`src/data/`)
   - `dao.py` - SQLAlchemy-based database access
   - `models.py` - Channel, Author, and other models
   - PostgreSQL backend via SQLAlchemy

6. **Image Generation** (`src/image/`)
   - Thumbnail creation, text-to-image, video frame extraction

7. **Film Generation** (`src/film/`)
   - AI-powered video generation with provider abstraction
   - Image providers: FAL (FLUX), Replicate
   - Video providers: Minimax, Kling, Runway
   - Audio providers: OpenAI TTS, ElevenLabs
   - Asset caching and metadata indexing
   - Cost tracking and budget enforcement

8. **PPTX Generation** (`src/pptx_gen/`)
   - AI-powered PowerPoint presentation creation
   - Content provider: OpenAI GPT (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
   - Template support (custom or auto-generated)
   - Content caching and cost optimization
   - Multiple slide layouts and styling options

9. **Production Features** (`src/features/`)
   - **Video Processing** (`features/video/`) - Subtitles, formatting, cropping, hooks, thumbnails
   - **Workflow** (`features/workflow/`) - Repurposing, templates, branding, calendar
   - **Editing** (`features/editing/`) - B-roll insertion, timeline editor, post-production
   - **Platform** (`features/platform/`) - Platform optimization, virality, storytelling
   - **Production** (`features/production/`) - VFX, film grain, color LUTs, Director AI
   - See `docs/PRODUCTION_PLATFORM_SUMMARY.md` for complete feature list

## Environment Setup

### Required Environment Variables (.env file)

Configuration is loaded via `src/config.py` using `dotenv_values()`.

Key variables (see `.env_template`):
```
MEDIA_GALLERY_DIR=        # Main media storage directory
DOWNLOAD_DIR=             # Downloaded media
TMP_DIR=                  # Temporary files
OPEN_AI_API_KEY=          # OpenAI API key
GOOGLE_TEXT_TO_SPEECH_API_KEY_PATH=  # Path to Google TTS credentials
YOUTUBE_CHANNEL_CONFIG_FILES=  # Channel configuration paths
OAUTH_2_DIR=              # OAuth credentials directory
CYBERVOICE_API_KEY=       # CyberVoice TTS API
ELEVEN_LABS_API_KEY=      # ElevenLabs TTS API
IMAGEMAGICK_BINARY=       # ImageMagick path for MoviePy
JDBC_HOST=                # PostgreSQL host
JDBC_PORT=                # PostgreSQL port
JDBC_USER_NAME=           # PostgreSQL username
JDBC_PASSWORD=            # PostgreSQL password
JDBC_DATABASE=            # PostgreSQL database name
```

### Python Package Management

This project uses **uv** for Python package management:

**Initial Setup:**
```bash
uv sync
```

**Common Commands:**
- Install all dependencies: `uv sync`
- Add a new dependency: `uv add <package>`
- Add a dev dependency: `uv add --dev <package>`
- Run a Python script: `uv run python <script.py>`
- Run a module: `uv run python -m <module>`
- Activate the virtual environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)

**Important Notes:**
- The virtual environment is created in `.venv/`
- Dependencies are defined in `pyproject.toml`
- Lock file: `uv.lock` (auto-generated, commit to git)
- All Python commands should be prefixed with `uv run` when not in the virtual environment

## Import Guidelines

**CRITICAL: Never use `sys.path.insert()` or path manipulation in code!**

### Proper Import Patterns

**✅ DO:**
```python
# Direct imports (assumes proper package structure)
from features.video.subtitles import SubtitleGenerator
from features.video.formatter import PlatformVideoFormatter

# For shared code that needs to be accessible from multiple places,
# use the mediaempire-shared package structure
```

**❌ DON'T:**
```python
# NEVER do this!
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### Running Examples

Examples should be run from the project root with proper Python path:

```bash
# From project root
cd /home/user/real-media-empire

# Run example
PYTHONPATH=src uv run python examples/subtitles_example.py

# Or activate venv first
source .venv/bin/activate
PYTHONPATH=src python examples/subtitles_example.py
```

### API Imports

API routers should import from the proper package structure. If code needs to be shared between `src/` and `director-ui/src/`, use the `mediaempire-shared` library approach.

## Running Pipelines

**IMPORTANT:** The project's ZenML pipelines were built with ZenML 0.40.x API which used `BaseParameters`. Modern ZenML (0.60+) has removed this class. The pipelines will need code updates before they can run. See "Known Issues" section below.

Pipelines should be executed from the `src/` directory:

### Generate Quote Shorts
```bash
cd src
uv run python -m pipelines.quotes_shorts_generate \
  --channel_config_path <path> \
  --author "Author Name" \
  --number_of_videos 5 \
  --is_split_quote  # Optional flag
```

### Generate Generic Shorts
```bash
cd src
uv run python -m pipelines.shorts_generate \
  --channel_config_path <path> \
  --number_of_videos 1
```

### Publish Shorts
```bash
cd src
uv run python -m pipelines.shorts_publish \
  --channel_config_path <path>
```

### Generate Film/Video (AI-Powered)
```bash
cd src
uv run python -m pipelines.film_generation \
  --film-id "my_film_001" \
  --shots-json-path "./shots.json" \
  --budget-limit 10.00 \
  --video-provider minimax
```

### Generate PowerPoint Presentation (AI-Powered)
```bash
cd src
uv run python -m pipelines.pptx_generation \
  --presentation-id "sales_q3_2025" \
  --topic "Q3 Sales Review" \
  --brief "Quarterly achievements and goals" \
  --num-slides 10 \
  --budget-limit 1.00 \
  --model gpt-4o-mini
```

### Recovery Mode
All pipelines support `--recover` flag to resume failed runs:
```bash
uv run python -m pipelines.<pipeline_name> --recover -r
```

## Webserver API

Flask-based REST API in `webserver/app.py` (runs on port 10101):

- **POST /commands** - Execute shell commands asynchronously
- **GET /commands/<id>** - Check command status
- **GET /commands** - List all commands with pagination
- Swagger UI available at `/swagger`
- Uses SQLite for command status tracking

Start server:
```bash
uv run python webserver/app.py
```

## Testing

Tests are located in `tests/` directory:
- `test_you_tube.py` - YouTube integration tests
- `text_test.py` - Text processing tests
- `txt_clip_test.py` - Text clip rendering tests

Run tests:
```bash
uv run python -m pytest tests/
```

## Channel Configuration

YouTube channels are configured via YAML files referenced in `YOUTUBE_CHANNEL_CONFIG_FILES`.
Each channel needs:
- OAuth2 credentials in `jack/oath/<channel_name>_oauth2.json`
- Client secrets file for YouTube API
- Channel ID and name

## Important Patterns

1. **All paths use `CONFIG.get()` not hardcoded values** - Configuration centralized in environment variables
2. **Pipeline parameters passed via `PipelineParams`** - Type-safe parameter passing with Click
3. **ZenML caching enabled** - `@pipeline(enable_cache=True)` for step result reuse
4. **YouTube OAuth stored per channel** - Credentials in `OAUTH_2_DIR` with channel-specific naming
5. **ImageMagick required** - MoviePy depends on ImageMagick for text rendering

## Database Schema

PostgreSQL database tracks:
- **Channel** - YouTube channel metadata
- **Author** - Quote authors and content creators
- Many-to-many relationships between channels and authors

Access via `src.data.dao` functions:
- `get_or_create(db, model, **kwargs)`
- `add_author(db, name)`
- `add_channel(db, name)`

## Video Content Sources

- Quotes stored in `jack/quotes/` (JSON files by category/author)
- Motivation topics in `jack/motivation_topics.json`
- Downloaded video assets in configured `DOWNLOAD_DIR`

## Known Issues and Migration Notes

### ZenML API Breaking Changes

The project was originally built with ZenML 0.40.x which has incompatible APIs with modern ZenML (0.60+):

**Key Breaking Changes:**
1. `BaseParameters` class removed from `zenml.steps` - Used in `src/pipelines/params/params_for_pipeline.py`
2. Pipeline decorator and step function signatures changed

**To Fix:**
- Replace `BaseParameters` with Pydantic `BaseModel` or standard dataclasses
- Update pipeline parameter passing to use modern ZenML patterns
- Consult ZenML migration guide: https://docs.zenml.io/

**Workaround:**
For now, non-pipeline code (YouTube uploaders, video processing, etc.) works fine with `uv run`.

### Old Conda Environments

The following files are legacy and can be ignored:
- `environment.yaml` - Old conda environment (replaced by pyproject.toml)
- `flask.yaml` - Old Flask conda environment (replaced by pyproject.toml)
- `stable-diffusion/requirements.txt` - Use `uv add --optional stable-diffusion <package>` instead

### Running Code Without Pipelines

Most functionality can be accessed directly without ZenML:
```bash
cd src
uv run python -c "from social.you_tube import YouTubeUploader; print('Works!')"
```
