"""FastAPI application setup."""

import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import BotConfig

# Configure logging to console with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Set specific loggers to DEBUG for more detailed output
logging.getLogger("api").setLevel(logging.DEBUG)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # Reduce SQL query spam

logger = logging.getLogger(__name__)

# Load configuration
config = BotConfig.from_env()

# Create FastAPI app
app = FastAPI(
    title="Content Processing API",
    description="API for managing PDF, YouTube, and web content extraction with AI processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and status endpoints"
        },
        {
            "name": "content",
            "description": "Content upload, extraction, and management"
        },
        {
            "name": "processing",
            "description": "AI processing jobs (summaries, MVP plans, content ideas)"
        },
        {
            "name": "bundles",
            "description": "Content bundles and multi-content processing"
        },
        {
            "name": "tags",
            "description": "Content tags and tagging management"
        },
        {
            "name": "prompts",
            "description": "System prompts for AI processing"
        },
        {
            "name": "film",
            "description": "Film and video generation with AI providers"
        },
        {
            "name": "pptx",
            "description": "PowerPoint presentation generation"
        },
        {
            "name": "publishing",
            "description": "Multi-platform content publishing and scheduling"
        },
        {
            "name": "characters",
            "description": "Character library for visual consistency tracking"
        },
        {
            "name": "assets",
            "description": "Media asset management and tracking"
        },
        {
            "name": "workspaces",
            "description": "Workspace and project management for multi-tenant organization"
        },
        {
            "name": "audio",
            "description": "Audio generation with TTS provider-specific optimization, pronunciation control, and multi-take comparison"
        },
        {
            "name": "editing",
            "description": "Video editing operations: trim, split, merge, transitions, and export"
        },
        {
            "name": "style",
            "description": "Visual style management: style mixing, color palettes, camera settings, and presets"
        },
        {
            "name": "heygen",
            "description": "HeyGen AI avatar video generation with custom voices and backgrounds"
        },
        {
            "name": "postiz",
            "description": "Multi-platform social media publishing via Postiz with content optimization"
        },
        {
            "name": "veed",
            "description": "VEED.io AI talking avatar video generation from photos and audio with lip-sync"
        },
        {
            "name": "trends",
            "description": "Trend research, hashtag optimization, and content strategy via Perplexity AI"
        },
        {
            "name": "stock-videos",
            "description": "Stock video search from Pexels and Pixabay for avatar backgrounds"
        },
        {
            "name": "ai-enhancement",
            "description": "AI-powered content enhancement via OpenRouter with multiple model support"
        },
        {
            "name": "storyboard",
            "description": "Shot storyboard organization, sequencing, and visualization for film production planning"
        },
    ]
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests."""
    logger.info(f"🔵 Incoming request: {request.method} {request.url.path}")
    logger.info(f"   Headers: {dict(request.headers)}")

    # Get request body for POST/PUT requests
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        logger.info(f"   Body: {body.decode('utf-8') if body else 'empty'}")
        # Re-create request with body for downstream processing
        from starlette.requests import Request

        async def receive():
            return {"type": "http.request", "body": body}

        request = Request(request.scope, receive)

    response = await call_next(request)
    logger.info(f"🟢 Response: {request.method} {request.url.path} → {response.status_code}")
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from api.routers import health, content, processing, bundles, tags, prompts, film, pptx, publishing, characters, assets, workspaces, style, heygen, postiz, veed, trends, stock_videos, film_shots, audio_generation, editing, script_writer, ai_enhancement, shot_storyboard

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(processing.router, prefix="/api/v1", tags=["processing"])
app.include_router(bundles.router, prefix="/api/v1", tags=["bundles"])
app.include_router(tags.router, prefix="/api/v1", tags=["tags"])
app.include_router(prompts.router, prefix="/api/v1", tags=["prompts"])
app.include_router(workspaces.router, prefix="/api", tags=["workspaces"])
app.include_router(film.router, prefix="/api/film", tags=["film"])
app.include_router(film_shots.router, prefix="/api/film", tags=["film"])
app.include_router(script_writer.router, prefix="/api/script", tags=["script-writer"])
app.include_router(shot_storyboard.router, prefix="/api/storyboard", tags=["storyboard"])
app.include_router(pptx.router, prefix="/api/pptx", tags=["pptx"])
app.include_router(publishing.router, prefix="/api/publishing", tags=["publishing"])
app.include_router(characters.router, prefix="/api/characters", tags=["characters"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(audio_generation.router, prefix="/api/audio", tags=["audio"])
app.include_router(editing.router, prefix="/api/editing", tags=["editing"])
app.include_router(style.router, prefix="/api/style", tags=["style"])
app.include_router(heygen.router, prefix="/api/heygen", tags=["heygen"])
app.include_router(postiz.router, prefix="/api/postiz", tags=["postiz"])
app.include_router(veed.router, prefix="/api/veed", tags=["veed"])
app.include_router(trends.router, prefix="/api/trends", tags=["trends"])
app.include_router(stock_videos.router, prefix="/api/stock-videos", tags=["stock-videos"])
app.include_router(ai_enhancement.router, prefix="/api/ai", tags=["ai-enhancement"])

# Mount WebSocket app
from websocket.manager import socket_app
app.mount("/ws", socket_app)

# Register error handlers
from api.error_handlers import register_error_handlers
register_error_handlers(app)

async def run_database_migrations():
    """Run alembic database migrations on startup."""
    try:
        from alembic.config import Config
        from alembic import command
        import asyncio
        from pathlib import Path

        # Get project root (director-ui/) from current file location
        # This file is at: director-ui/src/api/app.py
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent  # Go up 3 levels: api/ -> src/ -> director-ui/
        alembic_ini_path = project_root / "alembic.ini"

        if not alembic_ini_path.exists():
            logger.warning(f"⚠ alembic.ini not found at {alembic_ini_path}, skipping migrations")
            return

        # Get the alembic.ini config
        alembic_cfg = Config(str(alembic_ini_path))

        # Set the script location to the alembic directory
        alembic_cfg.set_main_option('script_location', str(project_root / 'alembic'))

        # Suppress alembic's INFO logging to reduce noise
        import logging as stdlib_logging
        stdlib_logging.getLogger('alembic').setLevel(stdlib_logging.WARNING)

        # Run migrations to head in a thread since alembic command interface is sync
        # but it triggers async code internally
        logger.info("Running database migrations...")
        logger.info(f"  Alembic config: {alembic_ini_path}")
        logger.info(f"  Script location: {project_root / 'alembic'}")
        logger.info(f"  Timeout: {config.migration_timeout} seconds")

        try:
            await asyncio.wait_for(
                asyncio.to_thread(command.upgrade, alembic_cfg, "head"),
                timeout=float(config.migration_timeout)
            )
            logger.info("✓ Database migrations completed successfully")
        except asyncio.TimeoutError:
            logger.error(f"⚠ Database migration timed out after {config.migration_timeout} seconds")
            logger.warning("⚠ Application will continue but database schema may be outdated")
            logger.warning("⚠ Try running migrations manually: cd director-ui && alembic upgrade head")

    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}", exc_info=True)
        logger.warning("⚠ Application will continue but database schema may be outdated")


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting Content Processing API on {config.api_host}:{config.api_port}")
    logger.info(f"API Documentation: http://{config.api_host}:{config.api_port}/docs")
    logger.info(f"WebSocket endpoint: ws://{config.api_host}:{config.api_port}/ws/socket.io/")
    logger.info(f"Storage path: {config.storage_base_path}")

    # Log configuration with secrets masked
    logger.info("=== Configuration ===")
    config_dict = config.__dict__
    for key, value in sorted(config_dict.items()):
        # Mask sensitive values
        if any(secret_key in key.lower() for secret_key in ['password', 'secret', 'token', 'key', 'api']):
            if value:
                masked_value = f"{str(value)[:4]}{'*' * (len(str(value)) - 4)}" if len(str(value)) > 4 else "****"
                logger.info(f"  {key}: {masked_value}")
            else:
                logger.info(f"  {key}: <not set>")
        else:
            logger.info(f"  {key}: {value}")
    logger.info("=" * 50)

    # Run database migrations if enabled
    if config.auto_migrate:
        await run_database_migrations()
    else:
        logger.info("⏭  Skipping database migrations (auto_migrate=False)")

    # Initialize publishing queue if Redis is configured
    try:
        from api.routers.publishing import initialize_queue
        await initialize_queue()
        logger.info("✓ Publishing queue initialized")
    except Exception as e:
        logger.warning(f"Publishing queue not initialized: {e}")
        logger.warning("  Publishing queue features will be disabled")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down Content Processing API")