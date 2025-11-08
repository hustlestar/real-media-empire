# Development Setup Guide

## Quick Start

### 1. Set Up Environment Variables

```bash
cd /home/user/real-media-empire/director-ui

# Copy the example .env file
cp .env.example .env

# Edit .env with your values
```

**For Local Development (Easiest):**
Use SQLite - no PostgreSQL installation required:
```bash
# In .env file:
TELEGRAM_BOT_TOKEN=dummy_token_for_api_only
DATABASE_URL=sqlite:///./mediaempire.db
```

**For Production/PostgreSQL:**
```bash
# In .env file:
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://user:password@localhost:5432/director_ui
# IMPORTANT: Use postgresql:// NOT postgresql+asyncpg://
# The codebase uses synchronous SQLAlchemy (sessionmaker, not AsyncSession)
```

### 2. Run Database Migrations (Optional for SQLite)

If using **SQLite**, tables are created automatically - skip this step.

If using **PostgreSQL**:
```bash
# Make sure PostgreSQL is running
# Then run migrations to create all tables
uv run alembic upgrade head
```

### 3. Start the Backend API

```bash
# From director-ui directory
PYTHONPATH=src uv run python -m api.main
```

The API will start on **http://localhost:10000**

You should see:
```
Starting Content Processing API
Host: 0.0.0.0
Port: 10000
Documentation: http://0.0.0.0:10000/docs
```

### 4. Start the Frontend

```bash
# In a new terminal
cd frontend
npm install  # First time only
npm run dev
```

The frontend will start on **http://localhost:5173**

You should see:
```
VITE v7.1.7  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 5. Access the Application

Open your browser to: **http://localhost:5173**

The frontend will proxy API requests from `/api/*` to `http://localhost:10000/api/*`

## API Documentation

Once the backend is running, you can access:
- Swagger UI: http://localhost:10000/docs
- ReDoc: http://localhost:10000/redoc

## Troubleshooting

### Backend 500 Errors

If you see 500 errors for `/api/workspaces/workspaces` or `/api/v1/content`:

**Cause:** Database tables don't exist yet

**Fix:**
```bash
cd /home/user/real-media-empire/director-ui
uv run alembic upgrade head
```

### Backend Not Connecting

**Check if backend is running:**
```bash
curl http://localhost:10000/api/health
# Should return: {"status":"healthy"}
```

**Check the port:**
```bash
lsof -i :10000
# Should show python/uvicorn process
```

### Frontend Can't Connect to Backend

**Verify proxy configuration in `frontend/vite.config.ts`:**
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:10000',  // Must match backend port
      changeOrigin: true,
    },
  },
}
```

### Database Connection Issues

**Check PostgreSQL is running:**
```bash
pg_isready
```

**Verify DATABASE_URL in .env:**
```
DATABASE_URL=postgresql://user:password@localhost:5432/director_ui
```

**Test database connection:**
```bash
uv run python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://user:password@localhost:5432/director_ui'); engine.connect(); print('✅ Connected')"
```

### SQLAlchemy MissingGreenlet Error

**Error:**
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
```

**Cause:** The DATABASE_URL is using an async driver (`postgresql+asyncpg://`) but the codebase uses synchronous SQLAlchemy.

**Fix:** Update your DATABASE_URL in `.env` to use the synchronous driver:
```bash
# ❌ Wrong (will cause greenlet error):
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/director_ui

# ✅ Correct:
DATABASE_URL=postgresql://user:password@localhost:5432/director_ui
# Or explicitly:
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/director_ui
```

The codebase uses `sessionmaker` and `Session` (synchronous), NOT `AsyncSession`.

## Running with Docker

If using Docker Compose, you need to expose the API port:

```yaml
# Add to docker-compose.yml under the 'bot' service:
services:
  bot:
    ports:
      - "10000:10000"  # Expose API port
```

Then:
```bash
docker-compose up -d
```

## Development Workflow

1. **Backend changes:** The server will need to be restarted manually (or set `reload=True` in `src/api/main.py`)
2. **Frontend changes:** Vite hot-reloads automatically
3. **Database schema changes:**
   ```bash
   # Create migration
   uv run alembic revision -m "description"

   # Edit the migration file

   # Apply migration
   uv run alembic upgrade head
   ```

## Environment Variables Reference

### Required
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `DATABASE_URL` - PostgreSQL connection string

### Optional
- `API_PORT` - Backend port (default: 10000)
- `API_HOST` - Backend host (default: 0.0.0.0)
- `OPENROUTER_API_KEY` - For AI features
- `HEYGEN_API_KEY` - For avatar generation
- `POSTIZ_API_KEY` - For social publishing

See `.env.example` for complete list.
