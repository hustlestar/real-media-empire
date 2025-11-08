"""FastAPI application setup."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import BotConfig

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
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from api.routers import health, content, processing, bundles, tags, prompts, film, pptx, publishing, characters, assets, workspaces, style, heygen, postiz, veed, trends, stock_videos, film_shots, audio_generation, editing

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(processing.router, prefix="/api/v1", tags=["processing"])
app.include_router(bundles.router, prefix="/api/v1", tags=["bundles"])
app.include_router(tags.router, prefix="/api/v1", tags=["tags"])
app.include_router(prompts.router, prefix="/api/v1", tags=["prompts"])
app.include_router(workspaces.router, prefix="/api/workspaces", tags=["workspaces"])
app.include_router(film.router, prefix="/api/film", tags=["film"])
app.include_router(film_shots.router, prefix="/api/film", tags=["film"])
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

# Mount WebSocket app
from websocket.manager import socket_app
app.mount("/ws", socket_app)

# Register error handlers
from api.error_handlers import register_error_handlers
register_error_handlers(app)

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting Content Processing API on {config.api_host}:{config.api_port}")
    logger.info(f"API Documentation: http://{config.api_host}:{config.api_port}/docs")
    logger.info(f"WebSocket endpoint: ws://{config.api_host}:{config.api_port}/ws/socket.io/")
    logger.info(f"Storage path: {config.storage_base_path}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down Content Processing API")