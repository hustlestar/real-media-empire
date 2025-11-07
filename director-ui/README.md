# Director UI

**AI-powered director's platform for video content creation and multi-platform publishing.**

Film generation, avatar videos, social media publishing, and director-level creative controls — all in one platform.

## Features

### 🎬 Film Generation
- AI-powered video creation with multiple providers (Minimax, Kling, Runway)
- Shot-by-shot generation from text prompts
- Cost tracking and budget management
- Asset caching and metadata indexing

### 🎭 HeyGen Avatar Studio
- AI avatar video generation with custom voices
- Multiple aspect ratios (TikTok, YouTube, Instagram)
- Background customization (color, image, video)
- Voice control (speed, pitch, emotion)
- Real-time generation status tracking

### 📢 Multi-Platform Publishing
- Publish to TikTok, YouTube, Instagram, Facebook, Twitter, LinkedIn
- Platform-specific content optimization
- Scheduled posting support
- Analytics and performance tracking
- Batch publishing across platforms

### 🎨 Director Creative Controls
1. **Dailies Room** - Shot review and approval workflow
2. **Voice Direction** - Audio customization and voice selection
3. **Timeline Editor** - Video sequencing and editing
4. **Visual Style Mixer** - Color grading and visual effects
5. **Iteration Loop** - Feedback and regeneration workflow
6. **Asset Studio** - Visual search, semantic search, lineage tracking

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url>
cd director-ui
uv sync

# 2. Database setup
docker compose up -d postgres
cp .env.example .env
# Edit .env with your API keys

# 3. Run migrations
uv run alembic upgrade head

# 4. Start backend
uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# 5. Start frontend (in another terminal)
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

## Environment Variables

Required in `.env`:

```env
# Database
DATABASE_URL=postgresql://botuser:botpass@localhost:5432/pdf_link_youtube_to_anything_tg_bot

# AI & Video Generation
OPENROUTER_API_KEY=your_key
HEYGEN_API_KEY=your_key

# Social Publishing
POSTIZ_API_KEY=your_key
POSTIZ_BASE_URL=https://api.postiz.com

# Optional
TELEGRAM_BOT_TOKEN=your_token
```

## Project Structure

```
director-ui/
├── src/                    # Backend (Python/FastAPI)
│   ├── api/               # API routes and app
│   ├── film/              # Film generation providers
│   ├── social/            # Social media publishing
│   ├── data/              # Database models
│   └── config/            # Configuration
├── frontend/              # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Page components
│   │   └── api/           # Auto-generated API client
│   └── scripts/           # Build scripts
├── alembic/               # Database migrations
└── tests/                 # Python tests
```

## Development

### Backend

```bash
# Start with hot reload
uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Create migration
uv run alembic revision -m "description"
uv run alembic upgrade head
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Install git hooks (auto-generates API client)
bash scripts/install-hooks.sh

# Generate API client
npm run generate-api

# Start dev server
npm run dev

# Build for production
npm run build
```

### API Client Generation

The frontend uses **auto-generated TypeScript client** from backend OpenAPI spec:

```bash
# Automatic via pre-commit hook (recommended)
bash frontend/scripts/install-hooks.sh

# Manual regeneration
cd frontend && npm run generate-api
```

See [OPENAPI_CLIENT.md](OPENAPI_CLIENT.md) for details.

## Testing

```bash
# Python tests (115+ tests, all mocked)
cd director-ui
uv run pytest

# Test categories
uv run pytest tests/test_imports.py          # Import validation
uv run pytest tests/test_heygen_provider.py  # HeyGen provider
uv run pytest tests/test_postiz_publisher.py # Postiz publisher
uv run pytest tests/test_models.py           # Database models
```

## Documentation

- **[OPENAPI_CLIENT.md](OPENAPI_CLIENT.md)** - API client generation
- **[MIGRATIONS.md](MIGRATIONS.md)** - Database setup & migrations
- **[CLAUDE.md](CLAUDE.md)** - Development guidelines for AI assistants
- **[frontend/README.md](frontend/README.md)** - Frontend-specific docs

## Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (async API framework)
- SQLAlchemy (ORM)
- Alembic (migrations)
- PostgreSQL
- httpx (async HTTP client)

**Frontend:**
- React 19
- TypeScript
- Vite
- TailwindCSS
- TanStack Query
- @hey-api/openapi-ts (API client generation)

**Integrations:**
- HeyGen API (avatar videos)
- Postiz API (social publishing)
- OpenRouter (AI models)
- Minimax, Kling, Runway (video generation)

## License

MIT

## Author

Jack Ma - hustlequeen@mail.ru
