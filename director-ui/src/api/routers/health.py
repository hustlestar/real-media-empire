"""Health check endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from config.settings import BotConfig
from datetime import datetime
from data.async_dao import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os

router = APIRouter()
config = BotConfig.from_env()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.

    Returns API status and version information.
    """
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/db")
async def database_health(db: AsyncSession = Depends(get_async_db)):
    """
    Check database connectivity.

    Returns database status and connection information.
    """
    try:
        # Execute simple query
        result = await db.execute(text("SELECT 1"))
        result.scalar()

        # Get database stats
        result = await db.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        tables_count = result.scalar()

        return {
            "status": "healthy",
            "database": "connected",
            "tables_count": tables_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


@router.get("/health/storage")
async def storage_health():
    """
    Check storage accessibility.

    Returns storage status and path information.
    """
    storage_paths = {
        "base": config.storage_base_path,
        "extracted": config.extracted_text_path,
        "results": config.processing_results_path,
        "uploads": config.uploads_path
    }

    accessible_paths = {}
    inaccessible_paths = []

    for name, path in storage_paths.items():
        if os.path.exists(path):
            accessible_paths[name] = {
                "path": path,
                "exists": True,
                "writable": os.access(path, os.W_OK)
            }
        else:
            inaccessible_paths.append(name)

    if inaccessible_paths:
        return {
            "status": "degraded",
            "accessible": accessible_paths,
            "inaccessible": inaccessible_paths,
            "message": "Some storage paths are not accessible",
            "timestamp": datetime.utcnow().isoformat()
        }

    return {
        "status": "healthy",
        "storage": accessible_paths,
        "timestamp": datetime.utcnow().isoformat()
    }