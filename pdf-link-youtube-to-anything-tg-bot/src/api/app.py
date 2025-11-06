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
from api.routers import health, content, processing, bundles, tags, prompts

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(content.router, prefix="/api/v1", tags=["content"])
app.include_router(processing.router, prefix="/api/v1", tags=["processing"])
app.include_router(bundles.router, prefix="/api/v1", tags=["bundles"])
app.include_router(tags.router, prefix="/api/v1", tags=["tags"])
app.include_router(prompts.router, prefix="/api/v1", tags=["prompts"])

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting Content Processing API on {config.api_host}:{config.api_port}")
    logger.info(f"API Documentation: http://{config.api_host}:{config.api_port}/docs")
    logger.info(f"Storage path: {config.storage_base_path}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down Content Processing API")