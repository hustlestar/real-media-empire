"""
Publishing API routes - Multi-platform video publishing endpoints.
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# Import publishing system from shared library
from features.publishing.manager import PublishingManager
from features.publishing.queue import PublishingQueue, QueuedPublishConfig, QueueStatus
from features.publishing.platforms.base import PublishConfig, PublishResult, PublishStatus

# Import data models for tracking
from sqlalchemy import select, func
from data.models import PublishingPost, FilmProject
from data.async_dao import get_async_db
import uuid as uuid_lib

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (should be dependency-injected in production)
_manager: Optional[PublishingManager] = None
_queue: Optional[PublishingQueue] = None


# ============================================================================
# Helper Functions
# ============================================================================

async def create_publish_history_record(
    db: AsyncSession,
    film_project_id: Optional[str],
    film_variant_id: Optional[str],
    account_id: str,
    platform: str,
    title: str,
    description: Optional[str],
    result: PublishResult,
) -> Optional[PublishingPost]:
    """Create a PublishingPost record to track publication."""
    if not film_project_id:
        # If no film project linked, don't create history
        return None

    try:
        history = PublishingPost(
            id=str(uuid_lib.uuid4()),
            social_account_id=account_id,
            content_type="video",  # Assuming video content
            content_url=None,  # Will be set later if available
            caption=description,
            platform=platform,
            status="published" if result.success else "failed",
            published_at=datetime.utcnow() if result.success else None,
            platform_post_id=result.post_id if hasattr(result, 'post_id') else None,
            platform_url=result.post_url if hasattr(result, 'post_url') else None,
            source_id=film_project_id,
            source_type="film",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(history)

        # Update film project published fields
        if film_project_id:
            result = await db.execute(select(FilmProject).filter(FilmProject.id == film_project_id))
    film_project = result.scalar_one_or_none()
            if film_project:
                if not film_project.published_at:
                    film_project.published_at = datetime.utcnow()

                # Add platform to published_platforms if not already there
                if not film_project.published_platforms:
                    film_project.published_platforms = []
                if platform not in film_project.published_platforms:
                    film_project.published_platforms = list(film_project.published_platforms) + [platform]

        await db.flush()
        await db.refresh(history)
        return history

    except Exception as e:
        logger.error(f"Error creating publish history: {e}", exc_info=True)
        db.rollback()
        return None


def get_manager() -> PublishingManager:
    """Get publishing manager instance."""
    global _manager
    if _manager is None:
        _manager = PublishingManager()
    return _manager


def get_queue() -> PublishingQueue:
    """Get publishing queue instance."""
    global _queue
    if _queue is None:
        # TODO: Initialize with proper DB session
        raise HTTPException(status_code=500, detail="Queue not initialized")
    return _queue


# ============================================================================
# Request/Response Models
# ============================================================================

class AddAccountRequest(BaseModel):
    """Request to add new publishing account."""
    account_id: str = Field(..., description="Unique account identifier")
    platform: str = Field(..., description="Platform name (tiktok, instagram, facebook, linkedin, youtube)")
    credentials: dict = Field(..., description="Platform-specific credentials")


class PublishRequest(BaseModel):
    """Request to publish video."""
    account_id: str = Field(..., description="Account identifier")
    platforms: List[str] = Field(..., description="List of platforms to publish to")
    video_path: str = Field(..., description="Path to video file")
    title: str = Field(..., description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    tags: Optional[List[str]] = Field(None, description="Video tags")
    thumbnail_path: Optional[str] = Field(None, description="Path to thumbnail")
    platform_specific: Optional[dict] = Field(None, description="Platform-specific options")

    # Film integration fields (optional)
    film_project_id: Optional[str] = Field(None, description="Associated film project ID")
    film_variant_id: Optional[str] = Field(None, description="Associated film variant ID")


class ScheduledPublishRequest(PublishRequest):
    """Request to schedule video publish."""
    scheduled_time: datetime = Field(..., description="When to publish (UTC)")
    priority: int = Field(5, ge=1, le=10, description="Priority 1-10 (higher = more priority)")
    max_retries: int = Field(3, ge=0, le=10, description="Max retry attempts")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")


class BatchPublishRequest(BaseModel):
    """Request to publish multiple videos."""
    publishes: List[ScheduledPublishRequest] = Field(..., description="List of publish requests")


class VideoValidationRequest(BaseModel):
    """Request to validate video."""
    video_path: str = Field(..., description="Path to video file")
    platforms: List[str] = Field(..., description="Platforms to validate against")


class PublishResponse(BaseModel):
    """Response from publish operation."""
    success: bool
    results: dict  # platform -> PublishResult
    message: Optional[str] = None


class JobResponse(BaseModel):
    """Response with job information."""
    job_id: str
    status: str
    account_id: str
    platforms: List[str]
    title: str
    created_at: datetime
    scheduled_time: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# ============================================================================
# Account Management Endpoints
# ============================================================================

@router.post("/accounts", status_code=201)
async def add_account(request: AddAccountRequest, manager: PublishingManager = Depends(get_manager)):
    """
    Add new publishing account for a platform.

    Example credentials by platform:
    - TikTok: {"api_key": "...", "user": "..."}
    - Instagram: {"api_key": "...", "user": "..."}
    - Facebook: {"api_key": "...", "user": "...", "page_id": "..."}
    - LinkedIn: {"api_key": "...", "user": "..."}
    - YouTube: {"client_secrets_file": "...", "channel_name": "...", "channel_id": "..."}
    """
    try:
        manager.add_account(
            account_id=request.account_id,
            platform=request.platform,
            credentials=request.credentials
        )
        return {"message": f"Account {request.account_id} added for {request.platform}"}
    except Exception as e:
        logger.error(f"Error adding account: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/accounts/{account_id}/{platform}/authenticate")
async def authenticate_account(
    account_id: str,
    platform: str,
    manager: PublishingManager = Depends(get_manager)
):
    """Authenticate account for platform."""
    try:
        success = await manager.authenticate_account(account_id, platform)
        if success:
            return {"message": f"Authentication successful for {platform}"}
        else:
            raise HTTPException(status_code=401, detail="Authentication failed")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accounts")
async def list_accounts(manager: PublishingManager = Depends(get_manager)):
    """List all configured accounts."""
    accounts = manager.list_all_accounts()
    return {"accounts": accounts}


@router.get("/accounts/{account_id}/platforms")
async def get_account_platforms(account_id: str, manager: PublishingManager = Depends(get_manager)):
    """Get platforms configured for account."""
    platforms = manager.get_account_platforms(account_id)
    if not platforms:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    return {"account_id": account_id, "platforms": platforms}


# ============================================================================
# Publishing Endpoints
# ============================================================================

@router.post("/publish/immediate", response_model=PublishResponse)
async def publish_immediate(
    request: PublishRequest,
    manager: PublishingManager = Depends(get_manager),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Publish video immediately to specified platforms.

    This is a synchronous operation that will wait for all platforms to complete.
    For scheduled or background publishing, use /publish/scheduled endpoint.

    If film_project_id is provided, creates PublishingPost records for tracking.
    """
    try:
        # Create publish config
        config = PublishConfig(
            title=request.title,
            description=request.description,
            tags=request.tags,
            thumbnail_path=request.thumbnail_path,
            platform_specific=request.platform_specific or {}
        )

        # Publish to platforms
        results = await manager.publish_multi_platform(
            account_id=request.account_id,
            platforms=request.platforms,
            video_path=request.video_path,
            config=config
        )

        # Create publish history records if film project linked
        if request.film_project_id:
            for platform, result in results.items():
                await create_publish_history_record(
                    db=db,
                    film_project_id=request.film_project_id,
                    film_variant_id=request.film_variant_id,
                    account_id=request.account_id,
                    platform=platform,
                    title=request.title,
                    description=request.description,
                    result=result
                )

        # Convert results to dict
        results_dict = {p: r.dict() for p, r in results.items()}

        # Check overall success
        all_success = all(r.success for r in results.values())

        return PublishResponse(
            success=all_success,
            results=results_dict,
            message="All platforms succeeded" if all_success else "Some platforms failed"
        )

    except Exception as e:
        logger.error(f"Publish error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/scheduled", status_code=202)
async def publish_scheduled(
    request: ScheduledPublishRequest,
    queue: PublishingQueue = Depends(get_queue)
):
    """
    Schedule video for publishing.

    Returns job ID that can be used to check status.
    Video will be published at scheduled_time or immediately if time is in the past.
    """
    try:
        import uuid

        # Generate job ID
        job_id = f"job_{uuid.uuid4().hex[:12]}"

        # Create config
        config = PublishConfig(
            title=request.title,
            description=request.description,
            tags=request.tags,
            thumbnail_path=request.thumbnail_path,
            platform_specific=request.platform_specific or {}
        )

        # Create queued config
        queued_config = QueuedPublishConfig(
            account_id=request.account_id,
            platforms=request.platforms,
            video_path=request.video_path,
            config=config,
            scheduled_time=request.scheduled_time,
            priority=request.priority,
            max_retries=request.max_retries,
            webhook_url=request.webhook_url
        )

        # Add to queue
        job = queue.add_job(job_id, queued_config)

        return {
            "job_id": job_id,
            "message": "Job added to queue",
            "scheduled_time": request.scheduled_time.isoformat(),
            "status": job.status
        }

    except Exception as e:
        logger.error(f"Schedule error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/publish/batch", status_code=202)
async def publish_batch(
    request: BatchPublishRequest,
    queue: PublishingQueue = Depends(get_queue)
):
    """Schedule multiple videos for publishing."""
    try:
        import uuid

        job_ids = []

        for pub_request in request.publishes:
            job_id = f"job_{uuid.uuid4().hex[:12]}"

            config = PublishConfig(
                title=pub_request.title,
                description=pub_request.description,
                tags=pub_request.tags,
                thumbnail_path=pub_request.thumbnail_path,
                platform_specific=pub_request.platform_specific or {}
            )

            queued_config = QueuedPublishConfig(
                account_id=pub_request.account_id,
                platforms=pub_request.platforms,
                video_path=pub_request.video_path,
                config=config,
                scheduled_time=pub_request.scheduled_time,
                priority=pub_request.priority,
                max_retries=pub_request.max_retries,
                webhook_url=pub_request.webhook_url
            )

            queue.add_job(job_id, queued_config)
            job_ids.append(job_id)

        return {
            "job_ids": job_ids,
            "count": len(job_ids),
            "message": f"Added {len(job_ids)} jobs to queue"
        }

    except Exception as e:
        logger.error(f"Batch error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Queue Management Endpoints
# ============================================================================

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, queue: PublishingQueue = Depends(get_queue)):
    """Get status of publishing job."""
    job = queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    import json

    return JobResponse(
        job_id=job.id,
        status=job.status,
        account_id=job.account_id,
        platforms=json.loads(job.platforms),
        title=job.title,
        created_at=job.created_at,
        scheduled_time=job.scheduled_time,
        completed_at=job.completed_at,
        error_message=job.error_message
    )


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = None,
    account_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    queue: PublishingQueue = Depends(get_queue)
):
    """List jobs with optional filtering."""
    try:
        # Parse status
        status_filter = QueueStatus(status) if status else None

        jobs = queue.list_jobs(
            status=status_filter,
            account_id=account_id,
            limit=limit,
            offset=offset
        )

        import json

        return {
            "jobs": [
                {
                    "job_id": job.id,
                    "status": job.status,
                    "account_id": job.account_id,
                    "platforms": json.loads(job.platforms),
                    "title": job.title,
                    "created_at": job.created_at.isoformat(),
                    "scheduled_time": job.scheduled_time.isoformat() if job.scheduled_time else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                }
                for job in jobs
            ],
            "count": len(jobs),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"List jobs error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str, queue: PublishingQueue = Depends(get_queue)):
    """Cancel pending or scheduled job."""
    success = queue.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled (not pending/scheduled or not found)")
    return {"message": f"Job {job_id} cancelled"}


@router.get("/queue/stats")
async def get_queue_stats(queue: PublishingQueue = Depends(get_queue)):
    """Get queue statistics."""
    stats = queue.get_queue_stats()
    return {"stats": stats}


# ============================================================================
# Validation Endpoints
# ============================================================================

@router.post("/validate")
async def validate_video(
    request: VideoValidationRequest,
    manager: PublishingManager = Depends(get_manager)
):
    """
    Validate video against platform requirements.

    Returns validation results for each platform including:
    - valid: boolean
    - errors: list of validation errors
    - warnings: list of warnings
    - video_info: video properties
    """
    results = manager.validate_video_for_platforms(
        video_path=request.video_path,
        platforms=request.platforms
    )

    overall_valid = all(r['valid'] for r in results.values())

    return {
        "valid": overall_valid,
        "results": results
    }


@router.get("/platforms/{platform}/requirements")
async def get_platform_requirements(platform: str, manager: PublishingManager = Depends(get_manager)):
    """Get video requirements for platform."""
    try:
        # Create temporary publisher to get requirements
        from features.publishing.manager import PublishingManager as PM
        temp_manager = PM()
        publisher = temp_manager._create_publisher(platform.lower(), {})
        requirements = publisher.get_requirements()

        return {
            "platform": platform,
            "requirements": requirements.dict()
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Requirements error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Video Management Endpoints
# ============================================================================

@router.delete("/videos/{account_id}/{platform}/{video_id}")
async def delete_video(
    account_id: str,
    platform: str,
    video_id: str,
    manager: PublishingManager = Depends(get_manager)
):
    """Delete video from platform."""
    success = await manager.delete_video(account_id, platform, video_id)
    if not success:
        raise HTTPException(status_code=400, detail="Video deletion failed")
    return {"message": f"Video {video_id} deleted from {platform}"}


@router.get("/videos/{account_id}/{platform}/{video_id}/status")
async def check_video_status(
    account_id: str,
    platform: str,
    video_id: str,
    manager: PublishingManager = Depends(get_manager)
):
    """Check status of uploaded video."""
    status = await manager.check_video_status(account_id, platform, video_id)
    return {
        "video_id": video_id,
        "platform": platform,
        "status": status.value
    }
