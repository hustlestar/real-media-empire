# CLAUDE.md

Development guidelines for AI assistants working on the Director UI platform.

## Project Overview

Director UI is an AI-powered platform for video content creation and multi-platform publishing. It combines:
- Film generation (Minimax, Kling, Runway providers)
- HeyGen avatar video generation
- Postiz multi-platform social media publishing
- Director-level creative controls (Dailies Room, Voice Direction, Timeline Editor, etc.)

## Tech Stack

**Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL
**Frontend:** React 19, TypeScript, Vite, TailwindCSS, TanStack Query
**Package Management:** `uv` (Python), `npm` (JavaScript)

## Development Workflow

### 1. Python Package Management

Use **uv** for all Python operations:

```bash
# Initial setup
uv sync

# Add dependency
uv add <package>

# Add dev dependency
uv add --dev <package>

# Run commands
uv run python -m <module>
uv run uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
uv run pytest
uv run alembic upgrade head
```

Never use `pip` or `conda`. All dependencies in `pyproject.toml`.

### 2. Database Setup & Migrations

**Start PostgreSQL:**
```bash
docker compose up -d postgres
```

**Apply migrations:**
```bash
uv run alembic upgrade head
```

**Create new migration:**
```bash
uv run alembic revision -m "description"
# Edit alembic/versions/<new_file>.py
uv run alembic upgrade head
```

See [MIGRATIONS.md](MIGRATIONS.md) for complete documentation.

### 3. API Client Generation (Critical)

The frontend uses **auto-generated TypeScript client** from backend OpenAPI spec. This eliminates code duplication.

**Install pre-commit hook (one-time):**
```bash
cd frontend
bash scripts/install-hooks.sh
```

**Hook behavior:**
- Detects changes to `src/api/` or `src/data/models.py`
- Auto-regenerates TypeScript client on commit
- Stages generated files for commit
- Warns if backend not running

**Manual regeneration:**
```bash
cd frontend
npm run generate-api
```

**Usage in frontend:**
```typescript
import { getFilmShotsApiFilmShotsGet, type FilmShot } from '@/api/sdk.gen';
const response = await getFilmShotsApiFilmShotsGet();
```

See [OPENAPI_CLIENT.md](OPENAPI_CLIENT.md) for details.

### 4. Shared Library (mediaempire-shared)

Located at `../mediaempire-shared/`, contains shared utilities between projects.

**After modifying shared library:**
```bash
cd ../mediaempire-shared
# Make changes
cd ../director-ui
uv sync  # Reinstall from local path
```

**Dependencies:**
```toml
[project]
dependencies = [
    "mediaempire-shared @ file:///path/to/mediaempire-shared",
]
```

## Architecture Patterns

### Provider Architecture

Use **abstract base classes** for interchangeable providers:

**Video Providers:**
```python
# src/film/base_provider.py
class VideoProvider(ABC):
    @abstractmethod
    async def generate(self, *args, **kwargs) -> VideoGenerationResult:
        pass

# src/film/providers/heygen.py
class HeyGenProvider(VideoProvider):
    async def generate(self, script, avatar_id, voice_id, **kwargs):
        # Implementation
```

**Social Publishers:**
```python
# src/social/base_publisher.py
class SocialPublisher(ABC):
    @abstractmethod
    async def publish(self, content: PostContent, account_id: str) -> PublishResult:
        pass

# src/social/postiz_publisher.py
class PostizPublisher(SocialPublisher):
    async def publish(self, content, account_id):
        # Platform-specific optimization
        optimized = await self._optimize_content(content)
        # Publish
```

### Dependency Injection

Use FastAPI dependency system for singletons:

```python
# src/api/dependencies.py
_heygen_provider: Optional[HeyGenProvider] = None

async def get_heygen_provider() -> HeyGenProvider:
    global _heygen_provider
    if _heygen_provider is None:
        config = HeyGenConfig(api_key=os.getenv("HEYGEN_API_KEY"))
        _heygen_provider = HeyGenProvider(config)
    return _heygen_provider

# src/api/routers/heygen.py
@router.post("/generate")
async def generate(
    request: Request,
    provider: HeyGenProvider = Depends(get_heygen_provider)
):
    result = await provider.generate(...)
```

### Configuration with Pydantic

Use Pydantic `BaseModel` for config:

```python
class HeyGenConfig(BaseModel):
    api_key: str
    base_url: str = "https://api.heygen.com"
    max_retries: int = 3
    poll_interval: int = 10
    max_wait_time: int = 300
```

### Database Models

SQLAlchemy models in `src/data/models.py`:

```python
class AvatarVideo(Base):
    __tablename__ = "avatar_videos"

    id = Column(String, primary_key=True)
    video_id = Column(String, unique=True, nullable=False)
    script = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.current_timestamp())
```

Always create migration after model changes.

## Integration Patterns

### HeyGen Avatar Video Generation

**Wait-and-poll pattern:**
```python
async def generate(self, script, avatar_id, voice_id, **kwargs):
    # 1. Submit generation request
    response = await self.client.post("/v2/video/generate", json=request_data)
    video_id = response.json()["data"]["video_id"]

    # 2. Poll for completion
    while True:
        status_response = await self.client.get(f"/v1/video_status.get?video_id={video_id}")
        status = status_response.json()["data"]["status"]

        if status == "completed":
            return status_response.json()["data"]["video_url"]
        elif status == "failed":
            raise Exception("Generation failed")

        await asyncio.sleep(self.config.poll_interval)
```

**Aspect ratios:**
- `9:16` - TikTok, Instagram Reels (720x1280)
- `16:9` - YouTube, LinkedIn (1280x720)
- `1:1` - Instagram Feed (1080x1080)
- `4:5` - Instagram Portrait (1080x1350)

### Postiz Multi-Platform Publishing

**Platform-specific optimization:**
```python
PLATFORM_LIMITS = {
    "tiktok": PlatformLimits(max_caption_length=2200, max_hashtags=30),
    "youtube": PlatformLimits(max_caption_length=5000, max_hashtags=15),
    "instagram": PlatformLimits(max_caption_length=2200, max_hashtags=30),
    "twitter": PlatformLimits(max_caption_length=280, max_hashtags=10),
}

async def _optimize_content(self, content: PostContent) -> PostContent:
    limits = PLATFORM_LIMITS[content.platform]

    # Truncate caption
    if len(content.caption) > limits.max_caption_length:
        content.caption = content.caption[:limits.max_caption_length - 3] + "..."

    # Limit hashtags
    content.hashtags = content.hashtags[:limits.max_hashtags]

    return content
```

**Multi-platform batch publishing:**
```python
@router.post("/publish/multi-platform")
async def multi_platform_publish(
    account_ids: List[str],
    content: PostContent,
    publisher: PostizPublisher = Depends(get_postiz_publisher)
):
    results = []
    for account_id in account_ids:
        result = await publisher.publish(content, account_id)
        results.append(result)
    return results
```

## Testing Guidelines

### Test Strategy

All tests use **mocks** - no real API calls or database connections.

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_heygen_provider.py

# Run with coverage
uv run pytest --cov=src
```

### Mock HTTP Requests

```python
from unittest.mock import AsyncMock, MagicMock
import pytest

@pytest.mark.asyncio
async def test_heygen_generate(heygen_provider):
    # Mock HTTP client
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "code": 100,
        "data": {"video_id": "test-123"}
    }
    mock_client.post.return_value = mock_response
    heygen_provider.client = mock_client

    # Test
    result = await heygen_provider.generate(
        script="Test",
        avatar_id="avatar-1",
        voice_id="voice-1"
    )

    assert result.video_id == "test-123"
```

### Mock FastAPI Endpoints

```python
from fastapi.testclient import TestClient
from unittest.mock import patch

def test_generate_endpoint(client):
    with patch('api.routers.heygen.get_heygen_provider') as mock:
        mock.return_value = mock_heygen_provider

        response = client.post("/api/heygen/generate", json={
            "script": "Test",
            "avatar_id": "avatar-1",
            "voice_id": "voice-1"
        })

        assert response.status_code == 200
```

### Test Organization

```
tests/
├── test_imports.py           # Import validation
├── test_heygen_provider.py   # HeyGen provider mocks
├── test_heygen_router.py     # HeyGen API endpoints
├── test_postiz_publisher.py  # Postiz publisher mocks
├── test_postiz_router.py     # Postiz API endpoints
└── test_models.py            # Database model tests
```

## Frontend Development

### Component Organization

```
frontend/src/components/
├── video/          # Phase 1: Dailies Room
├── audio/          # Phase 2: Voice Direction
├── timeline/       # Phase 3: Timeline Editor
├── style/          # Phase 4: Visual Style Mixer
├── iteration/      # Phase 5: Iteration Loop
├── asset/          # Phase 6: Asset Studio
├── heygen/         # HeyGen Avatar Studio
└── publishing/     # Postiz Publishing Hub
```

### Using Generated API

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  getFilmShotsApiFilmShotsGet,
  createFilmShotApiFilmShotsPost,
  type FilmShot
} from '@/api/sdk.gen';

// Query
const { data: shots } = useQuery({
  queryKey: ['film-shots', filmId],
  queryFn: async () => {
    const response = await getFilmShotsApiFilmShotsGet({
      query: { film_id: filmId }
    });
    return response.data;
  }
});

// Mutation
const createShot = useMutation({
  mutationFn: async (shot: FilmShot) => {
    const response = await createFilmShotApiFilmShotsPost({
      body: shot
    });
    return response.data;
  }
});
```

## Git Workflow

### Branch Naming

Work on branches prefixed with `claude/` and ending with session ID:
```
claude/enhance-film-generation-011CUrjE7Gg4m9skvKCBttox
```

### Commit Messages

Follow conventional commits:
```
feat: Add HeyGen avatar video generation
fix: Correct platform limits for TikTok
docs: Update API client generation guide
test: Add comprehensive tests for Postiz publisher
```

### Pushing Changes

Always use `-u` flag:
```bash
git push -u origin <branch-name>
```

On network errors, retry with exponential backoff (2s, 4s, 8s, 16s).

### Pre-commit Hook

The pre-commit hook auto-regenerates API client. To bypass:
```bash
git commit --no-verify -m "message"
```

## Environment Variables

Required in `.env`:

```env
# Database
DATABASE_URL=postgresql://botuser:botpass@localhost:5432/pdf_link_youtube_to_anything_tg_bot

# AI & Video
OPENROUTER_API_KEY=your_key
HEYGEN_API_KEY=your_key

# Social Publishing
POSTIZ_API_KEY=your_key
POSTIZ_BASE_URL=https://api.postiz.com

# Optional
TELEGRAM_BOT_TOKEN=your_token
API_CORS_ORIGINS=*
LOG_LEVEL=INFO
```

## Common Tasks

### Add New API Endpoint

1. Create router function in `src/api/routers/<module>.py`
2. Register router in `src/api/app.py`
3. Start backend: `uv run uvicorn src.api.app:app --reload`
4. Frontend will auto-generate client on commit (via pre-commit hook)

### Add New Database Model

1. Add model to `src/data/models.py`
2. Create migration: `uv run alembic revision -m "add_table"`
3. Edit migration file in `alembic/versions/`
4. Apply: `uv run alembic upgrade head`

### Add New Provider

1. Create provider in `src/film/providers/<name>.py`
2. Inherit from `VideoProvider` base class
3. Implement `generate()` method
4. Add config class with Pydantic
5. Add dependency in `src/api/dependencies.py`
6. Create router in `src/api/routers/<name>.py`
7. Write tests in `tests/test_<name>_provider.py`

## Troubleshooting

### "Module not found" errors

```bash
uv sync  # Reinstall dependencies
```

### Backend not starting

Check:
1. PostgreSQL is running: `docker compose ps`
2. `.env` file exists and has `DATABASE_URL`
3. Migrations applied: `uv run alembic upgrade head`

### Frontend API client out of sync

```bash
cd frontend
npm run generate-api
```

### Tests failing

```bash
# Clear pytest cache
uv run pytest --cache-clear

# Run in verbose mode
uv run pytest -v
```

## Best Practices

1. **Never hardcode API keys** - Use environment variables
2. **Always use dependency injection** - Singleton providers via `Depends()`
3. **Mock all external calls in tests** - No real API calls
4. **Use Pydantic for validation** - Request/response models
5. **Create indexes on frequently queried columns** - In migrations
6. **Platform-specific optimization** - Different limits for each platform
7. **Commit generated files** - Frontend API client should be in git
8. **Write both upgrade() and downgrade()** - For all migrations
9. **Use async/await everywhere** - FastAPI and httpx are async
10. **Follow provider architecture** - Abstract base classes for extensibility

## References

- **Backend:** [FastAPI Docs](https://fastapi.tiangolo.com/)
- **ORM:** [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- **Migrations:** [Alembic Docs](https://alembic.sqlalchemy.org/)
- **Frontend:** [React Docs](https://react.dev/)
- **API Client:** [@hey-api/openapi-ts](https://heyapi.dev/)
- **State Management:** [TanStack Query](https://tanstack.com/query/latest)

---

For detailed documentation, see:
- [README.md](README.md) - Project overview
- [OPENAPI_CLIENT.md](OPENAPI_CLIENT.md) - API client generation
- [MIGRATIONS.md](MIGRATIONS.md) - Database setup & migrations
- [frontend/README.md](frontend/README.md) - Frontend-specific docs
