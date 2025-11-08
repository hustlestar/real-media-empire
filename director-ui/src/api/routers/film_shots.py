"""
Film shot management and review API endpoints.

Provides endpoints for:
- Listing shots
- Getting shot details
- Reviewing shots (approve/reject/retake)
- Filtering shots by status
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, func
from data.async_dao import get_async_db
from data.models import FilmShot, ShotReview, FilmProject

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================


class ShotReviewRequest(BaseModel):
    """Request to review a shot"""
    status: str = Field(..., description="Review status: 'approved', 'rejected', 'needs_revision'")
    notes: Optional[str] = Field(None, description="Director's feedback and notes")
    reviewer: Optional[str] = Field(None, description="Username or email of reviewer")


class ShotReviewResponse(BaseModel):
    """Shot review information"""
    status: str
    notes: Optional[str]
    reviewer: Optional[str]
    reviewed_at: datetime

    class Config:
        from_attributes = True


class ShotResponse(BaseModel):
    """Shot information"""
    id: str
    shot_id: str
    film_project_id: str
    video_url: str
    thumbnail_url: Optional[str]
    image_url: Optional[str]
    audio_url: Optional[str]
    prompt: str
    duration: float
    sequence_order: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    review: Optional[ShotReviewResponse]

    class Config:
        from_attributes = True


class ShotsListResponse(BaseModel):
    """List of shots with pagination"""
    shots: List[ShotResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/shots", response_model=ShotsListResponse)
async def list_shots(
    film_project_id: Optional[str] = Query(None, description="Filter by film project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List all shots with optional filtering.

    Supports filtering by:
    - film_project_id: Show shots from specific film
    - status: Show shots with specific status (approved, rejected, etc.)
    """
    query = db.query(FilmShot)

    # Apply filters
    if film_project_id:
        query = query.filter(FilmShot.film_project_id == film_project_id)

    if status:
        query = query.filter(FilmShot.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    shots = query.order_by(FilmShot.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # Build response with reviews
    shot_responses = []
    for shot in shots:
        shot_dict = {
            "id": shot.id,
            "shot_id": shot.shot_id,
            "film_project_id": shot.film_project_id,
            "video_url": shot.video_url,
            "thumbnail_url": shot.thumbnail_url,
            "image_url": shot.image_url,
            "audio_url": shot.audio_url,
            "prompt": shot.prompt,
            "duration": float(shot.duration),
            "sequence_order": shot.sequence_order,
            "status": shot.status,
            "created_at": shot.created_at,
            "updated_at": shot.updated_at,
            "review": None,
        }

        # Include review if exists
        if shot.review:
            shot_dict["review"] = {
                "status": shot.review.status,
                "notes": shot.review.notes,
                "reviewer": shot.review.reviewer,
                "reviewed_at": shot.review.reviewed_at,
            }

        shot_responses.append(ShotResponse(**shot_dict))

    return ShotsListResponse(
        shots=shot_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/projects/{film_project_id}/shots", response_model=ShotsListResponse)
async def list_project_shots(
    film_project_id: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List all shots for a specific film project.

    Convenience endpoint that filters by film_project_id.
    """
    # Verify project exists
    result = await db.execute(select(FilmProject).filter(FilmProject.id == film_project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Film project '{film_project_id}' not found")

    return await list_shots(
        film_project_id=film_project_id,
        status=status,
        page=page,
        page_size=page_size,
        db=db,
    )


@router.get("/shots/{shot_id}", response_model=ShotResponse)
async def get_shot(
    shot_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get details for a specific shot.
    """
    result = await db.execute(select(FilmShot).filter(FilmShot.id == shot_id))
    shot = result.scalar_one_or_none()

    if not shot:
        raise HTTPException(status_code=404, detail=f"Shot '{shot_id}' not found")

    # Build response
    shot_dict = {
        "id": shot.id,
        "shot_id": shot.shot_id,
        "film_project_id": shot.film_project_id,
        "video_url": shot.video_url,
        "thumbnail_url": shot.thumbnail_url,
        "image_url": shot.image_url,
        "audio_url": shot.audio_url,
        "prompt": shot.prompt,
        "duration": float(shot.duration),
        "sequence_order": shot.sequence_order,
        "status": shot.status,
        "created_at": shot.created_at,
        "updated_at": shot.updated_at,
        "review": None,
    }

    # Include review if exists
    if shot.review:
        shot_dict["review"] = {
            "status": shot.review.status,
            "notes": shot.review.notes,
            "reviewer": shot.review.reviewer,
            "reviewed_at": shot.review.reviewed_at,
        }

    return ShotResponse(**shot_dict)


@router.post("/shots/{shot_id}/review", response_model=ShotResponse)
async def review_shot(
    shot_id: str,
    review: ShotReviewRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Submit a review for a shot.

    Updates or creates review record and updates shot status.
    """
    # Get shot
    result = await db.execute(select(FilmShot).filter(FilmShot.id == shot_id))
    shot = result.scalar_one_or_none()
    if not shot:
        raise HTTPException(status_code=404, detail=f"Shot '{shot_id}' not found")

    # Validate status
    valid_statuses = ['approved', 'rejected', 'needs_revision']
    if review.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{review.status}'. Must be one of: {', '.join(valid_statuses)}"
        )

    # Update or create review
    result = await db.execute(select(ShotReview).filter(ShotReview.shot_id == shot_id))
    existing_review = result.scalar_one_or_none()

    if existing_review:
        # Update existing review
        existing_review.status = review.status
        existing_review.notes = review.notes
        existing_review.reviewer = review.reviewer
        existing_review.reviewed_at = datetime.now()
    else:
        # Create new review
        new_review = ShotReview(
            shot_id=shot_id,
            status=review.status,
            notes=review.notes,
            reviewer=review.reviewer,
            reviewed_at=datetime.now(),
        )
        db.add(new_review)

    # Update shot status based on review
    shot.status = review.status
    shot.updated_at = datetime.now()

    await db.flush()
    await db.refresh(shot)

    # Build response
    shot_dict = {
        "id": shot.id,
        "shot_id": shot.shot_id,
        "film_project_id": shot.film_project_id,
        "video_url": shot.video_url,
        "thumbnail_url": shot.thumbnail_url,
        "image_url": shot.image_url,
        "audio_url": shot.audio_url,
        "prompt": shot.prompt,
        "duration": float(shot.duration),
        "sequence_order": shot.sequence_order,
        "status": shot.status,
        "created_at": shot.created_at,
        "updated_at": shot.updated_at,
        "review": None,
    }

    # Include review
    if shot.review:
        shot_dict["review"] = {
            "status": shot.review.status,
            "notes": shot.review.notes,
            "reviewer": shot.review.reviewer,
            "reviewed_at": shot.review.reviewed_at,
        }

    return ShotResponse(**shot_dict)


@router.delete("/shots/{shot_id}/review")
async def delete_shot_review(
    shot_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete a shot review (reset to un-reviewed state).
    """
    result = await db.execute(select(FilmShot).filter(FilmShot.id == shot_id))
    shot = result.scalar_one_or_none()
    if not shot:
        raise HTTPException(status_code=404, detail=f"Shot '{shot_id}' not found")

    # Delete review if exists
    result = await db.execute(select(ShotReview).filter(ShotReview.shot_id == shot_id))
    review = result.scalar_one_or_none()
    if review:
        await db.delete(review)

        # Reset shot status to completed
        shot.status = "completed"
        shot.updated_at = datetime.now()

        await db.flush()

    return {"message": "Review deleted successfully"}


@router.get("/projects/{film_project_id}/stats")
async def get_project_shot_stats(
    film_project_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get statistics for shots in a film project.

    Returns counts by status (approved, rejected, needs review, etc.).
    """
    # Verify project exists
    result = await db.execute(select(FilmProject).filter(FilmProject.id == film_project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Film project '{film_project_id}' not found")

    # Count shots by status
    result = await db.execute(select(FilmShot).filter(FilmShot.film_project_id == film_project_id))
    all_shots = list(result.scalars().all())

    stats = {
        "total": len(all_shots),
        "approved": sum(1 for s in all_shots if s.status == 'approved'),
        "rejected": sum(1 for s in all_shots if s.status == 'rejected'),
        "needs_revision": sum(1 for s in all_shots if s.status == 'needs_revision'),
        "completed": sum(1 for s in all_shots if s.status == 'completed'),
        "generating": sum(1 for s in all_shots if s.status == 'generating'),
        "pending": sum(1 for s in all_shots if s.status == 'pending'),
    }

    # Calculate review progress
    reviewed = stats["approved"] + stats["rejected"] + stats["needs_revision"]
    stats["review_progress_percent"] = round((reviewed / stats["total"] * 100) if stats["total"] > 0 else 0, 1)

    return {
        "film_project_id": film_project_id,
        "stats": stats,
    }
