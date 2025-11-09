"""
Shot Storyboard API - Organize, sequence, and visualize shots.

This router provides endpoints for:
- Getting shots by film/workspace
- Updating shot sequence order
- Batch reordering for drag-and-drop
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_async_db
from data.models import ShotGeneration

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ShotSequenceUpdate(BaseModel):
    """Update sequence order for a shot."""
    shot_id: str
    sequence_order: int


class BatchSequenceUpdateRequest(BaseModel):
    """Batch update sequence orders (for drag-and-drop reordering)."""
    updates: List[ShotSequenceUpdate]


class ShotSummary(BaseModel):
    """Summary of a shot for storyboard display."""
    id: str
    workspace_id: Optional[str]
    film_id: Optional[str]
    sequence_order: Optional[int]
    version: int
    prompt: str
    shot_type: Optional[str]
    camera_motion: Optional[str]
    lighting: Optional[str]
    emotion: Optional[str]
    duration_seconds: float
    is_active: bool
    is_favorite: bool
    rating: Optional[int]
    created_at: datetime


# ============================================================================
# Shot Storyboard Endpoints
# ============================================================================

@router.get("/shots/by-film/{film_id}", response_model=List[ShotSummary])
async def get_shots_by_film(
    film_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all shots for a specific film, ordered by sequence."""
    try:
        result = await db.execute(
            select(ShotGeneration)
            .where(ShotGeneration.film_id == film_id)
            .order_by(asc(ShotGeneration.sequence_order), desc(ShotGeneration.created_at))
        )
        shots = result.scalars().all()

        return [
            ShotSummary(
                id=shot.id,
                workspace_id=shot.workspace_id,
                film_id=shot.film_id,
                sequence_order=shot.sequence_order,
                version=shot.version,
                prompt=shot.prompt,
                shot_type=shot.shot_type,
                camera_motion=shot.camera_motion,
                lighting=shot.lighting,
                emotion=shot.emotion,
                duration_seconds=shot.duration_seconds,
                is_active=shot.is_active,
                is_favorite=shot.is_favorite,
                rating=shot.rating,
                created_at=shot.created_at
            )
            for shot in shots
        ]

    except Exception as e:
        logger.error(f"Error getting shots by film: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shots/by-workspace/{workspace_id}", response_model=List[ShotSummary])
async def get_shots_by_workspace(
    workspace_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all shots for a specific workspace, ordered by sequence."""
    try:
        result = await db.execute(
            select(ShotGeneration)
            .where(ShotGeneration.workspace_id == workspace_id)
            .order_by(asc(ShotGeneration.sequence_order), desc(ShotGeneration.created_at))
        )
        shots = result.scalars().all()

        return [
            ShotSummary(
                id=shot.id,
                workspace_id=shot.workspace_id,
                film_id=shot.film_id,
                sequence_order=shot.sequence_order,
                version=shot.version,
                prompt=shot.prompt,
                shot_type=shot.shot_type,
                camera_motion=shot.camera_motion,
                lighting=shot.lighting,
                emotion=shot.emotion,
                duration_seconds=shot.duration_seconds,
                is_active=shot.is_active,
                is_favorite=shot.is_favorite,
                rating=shot.rating,
                created_at=shot.created_at
            )
            for shot in shots
        ]

    except Exception as e:
        logger.error(f"Error getting shots by workspace: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/shots/{shot_id}/sequence")
async def update_shot_sequence(
    shot_id: str,
    sequence_order: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Update the sequence order for a single shot."""
    try:
        result = await db.execute(
            select(ShotGeneration).where(ShotGeneration.id == shot_id)
        )
        shot = result.scalar_one_or_none()

        if not shot:
            raise HTTPException(status_code=404, detail="Shot not found")

        shot.sequence_order = sequence_order
        shot.updated_at = datetime.utcnow()

        await db.commit()

        return {
            "id": shot.id,
            "sequence_order": shot.sequence_order,
            "message": "Sequence order updated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating shot sequence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/shots/batch-sequence")
async def batch_update_sequences(
    request: BatchSequenceUpdateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Batch update sequence orders for multiple shots (for drag-and-drop)."""
    try:
        updated_count = 0

        for update in request.updates:
            result = await db.execute(
                select(ShotGeneration).where(ShotGeneration.id == update.shot_id)
            )
            shot = result.scalar_one_or_none()

            if shot:
                shot.sequence_order = update.sequence_order
                shot.updated_at = datetime.utcnow()
                updated_count += 1

        await db.commit()

        return {
            "updated_count": updated_count,
            "total_requested": len(request.updates),
            "message": f"Updated sequence for {updated_count} shots"
        }

    except Exception as e:
        logger.error(f"Error batch updating sequences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
