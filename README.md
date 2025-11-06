# Media Empire

Automated AI-powered content creation system for YouTube videos, shorts, and cinematic films.

## Features

### 🎬 Film Generation (NEW!)
AI-powered cinematic film generation with:
- **Scenario Generation**: Convert text descriptions to shot definitions using LLMs (OpenRouter)
- Text-to-image generation (FAL.ai FLUX, Replicate)
- Image-to-video animation (Minimax, Kling, Runway)
- Text-to-speech synthesis (OpenAI TTS, ElevenLabs)
- Intelligent asset caching and reuse
- Multi-dimensional metadata indexing
- Budget tracking and cost optimization

**Quick Start**: See [QUICKSTART_FILM.md](QUICKSTART_FILM.md)
**Scenario Generation**: See [SCENARIO_GENERATION.md](SCENARIO_GENERATION.md)
**Full Documentation**: See [FILM_GENERATION.md](FILM_GENERATION.md)

### 📱 YouTube Shorts Pipeline
Automated generation and publishing of YouTube shorts using ZenML pipelines:
- Quote-based shorts
- Motivation content
- Text animation effects
- Multi-channel publishing
- Swamp-to-lake workflow

### 🎥 Video Editing
Professional video editing powered by [MoviePy](https://github.com/Zulko/moviepy):
- Text animations and transitions
- Audio processing and mixing
- Video effects and composition

### 🔊 Multi-Provider TTS
Integration with multiple text-to-speech providers:
- Google TTS
- ElevenLabs
- CyberVoice
- Descript
- OpenAI TTS

### 📊 Content Management
- Database tracking (PostgreSQL + SQLAlchemy)
- YouTube API integration
- Channel management
- Author tracking

## Getting Started

### Prerequisites
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL database

### Installation

1. **Install dependencies**:
```bash
uv sync
```

2. **Configure environment**:
```bash
cp .env_template .env
# Edit .env with your API keys and settings
```

3. **Set up database**:
```bash
cd src
uv run python -c "from data.film_models import Base; from data.dao import engine; Base.metadata.create_all(engine)"
```

## Quick Start Guides

- **Scenario Generation**: [QUICKSTART_SCENARIO.md](QUICKSTART_SCENARIO.md) - **NEW!** Text to shots in 60 seconds
- **Film Generation**: [QUICKSTART_FILM.md](QUICKSTART_FILM.md) - Generate cinematic films with AI
- **Project Overview**: [CLAUDE.md](CLAUDE.md) - Architecture and development guide
- **Migration Notes**: [MIGRATION.md](MIGRATION.md) - Conda to UV migration

## Usage Examples

### Generate Scenario from Description (NEW!)
```bash
cd src
uv run python -m pipelines.scenario_generation \
  --description "A detective enters a dimly lit office at night" \
  --output ../my_shots.json \
  --num-shots 7 \
  --style "film noir" \
  --model claude-3-haiku
```

### Generate AI Film from Shots
```bash
cd src
uv run python -m pipelines.film_generation \
  --film_id "my_first_film" \
  --shots_json_path "../my_shots.json" \
  --budget_limit 1.00
```

### Generate Quote Shorts
```bash
cd src
uv run python -m pipelines.quotes_shorts_generate \
  --channel_config_path <path> \
  --author "Author Name" \
  --number_of_videos 5
```

### Publish Shorts
```bash
cd src
uv run python -m pipelines.shorts_publish \
  --channel_config_path <path>
```

## Documentation

- [SCENARIO_GENERATION.md](SCENARIO_GENERATION.md) - **NEW!** LLM-powered shot generation
- [FILM_GENERATION.md](FILM_GENERATION.md) - Complete film generation documentation
- [CLAUDE.md](CLAUDE.md) - Project architecture and patterns
- [MIGRATION.md](MIGRATION.md) - Package management migration guide
- [examples/README.md](examples/README.md) - Example shot definitions
- [examples/example_scenarios.txt](examples/example_scenarios.txt) - **NEW!** Example scene descriptions

## Project Structure

```
media-empire/
├── src/
│   ├── film/              # Film generation system (NEW!)
│   │   ├── models.py      # Data models
│   │   ├── cache.py       # Asset caching
│   │   ├── metadata.py    # Metadata indexing
│   │   ├── cost_tracker.py # Budget tracking
│   │   └── providers/     # AI provider integrations
│   ├── pipelines/         # ZenML pipelines
│   │   ├── film_generation.py
│   │   ├── quotes_shorts_generate.py
│   │   └── shorts_publish.py
│   ├── video/             # Video editing (MoviePy)
│   ├── audio/             # TTS providers
│   ├── text/              # ChatGPT integration
│   ├── social/            # YouTube API
│   └── data/              # Database models
├── examples/              # Example configurations
├── webserver/            # Flask API
└── tests/                # Test suite
```

## Development

### Using UV Package Manager

This project uses `uv` for fast, reliable Python package management:

```bash
# Install all dependencies
uv sync

# Add a new package
uv add <package>

# Run Python scripts
uv run python <script.py>

# Run modules
uv run python -m <module>
```

### Running Tests
```bash
uv run python -m pytest tests/
```

### Web API Server
```bash
uv run python webserver/app.py
# Server runs on http://localhost:10101
# Swagger UI: http://localhost:10101/swagger
```

## Cost Management

### Film Generation Costs (per shot)

**Budget Mode** (Minimax + OpenAI):
- Image: $0.003
- Video (5s): $0.050
- Audio: ~$0.001
- **Total: ~$0.054/shot**

**Premium Mode** (Kling + ElevenLabs):
- Image: $0.003
- Video (5s): $0.920
- Audio: ~$0.010
- **Total: ~$0.933/shot**

Use `--budget_limit` to prevent overspending!

## Known Issues

- **ZenML Migration**: Original pipelines built with ZenML 0.40.x (deprecated `BaseParameters`). Film generation pipeline uses modern approach compatible with ZenML 0.60+.
- **Legacy Conda Files**: Ignore `environment.yaml` and `flask.yaml` - use `pyproject.toml` instead

## Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and architecture patterns.

## License

[Add your license here]

## Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/media-empire/issues)
- **Documentation**: See docs in this repository