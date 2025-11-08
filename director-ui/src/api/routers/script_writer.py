"""
Script Writer API - AI-powered script/scene/shot generation with version control.

This router provides endpoints for:
- Generating scripts from ideas with AI
- Creating scenes with AI assistance
- Generating shots with version control
- Refining generations with AI feedback
- Managing version history and switching between attempts
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_async_db
from data.models import ScriptGeneration, Scene, ShotGeneration, GenerationNote

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateScriptFromIdeaRequest(BaseModel):
    """Request to generate script from idea using AI."""
    idea: str = Field(..., description="High-level idea or concept for the script")
    genre: Optional[str] = Field(None, description="Genre (action, drama, comedy, etc.)")
    style: Optional[str] = Field("hollywood_blockbuster", description="Cinematic style")
    project_id: Optional[str] = Field(None, description="Project to associate with")
    ai_feedback: Optional[str] = Field(None, description="Additional AI instructions")


class GenerateSceneRequest(BaseModel):
    """Request to generate scene with AI."""
    scene_description: str = Field(..., description="Description of the scene")
    characters: List[str] = Field(default_factory=list, description="Characters in scene")
    location: Optional[str] = Field(None, description="Location/setting")
    mood: Optional[str] = Field(None, description="Mood or atmosphere")
    pacing: Optional[str] = Field("medium", description="Scene pacing")
    style: Optional[str] = Field("hollywood_blockbuster", description="Cinematic style")
    project_id: Optional[str] = Field(None, description="Project to associate with")


class RefineGenerationRequest(BaseModel):
    """Request to refine existing generation with AI feedback."""
    generation_id: str = Field(..., description="ID of generation to refine")
    ai_feedback: str = Field(..., description="Refinement instructions (e.g., 'make it darker', 'add more tension')")
    regenerate_fields: Optional[List[str]] = Field(None, description="Which fields to regenerate (prompt, scene, etc.)")


class GenerationResponse(BaseModel):
    """Response with generation data."""
    id: str
    generation_type: str
    version: int
    parent_id: Optional[str]

    # Input data
    input_data: dict

    # Output data
    output_prompt: Optional[str]
    output_negative_prompt: Optional[str]
    output_metadata: Optional[dict]

    # Status
    is_active: bool
    is_favorite: bool
    rating: Optional[int]
    ai_feedback: Optional[str]

    created_at: datetime

    class Config:
        from_attributes = True


class VersionListResponse(BaseModel):
    """List of all versions for a generation."""
    generations: List[GenerationResponse]
    total_count: int
    active_version: Optional[str]


class NoteRequest(BaseModel):
    """Request to add note to generation."""
    note: str = Field(..., description="Note content")


# ============================================================================
# Script Generation Endpoints
# ============================================================================

@router.post("/script/generate-from-idea")
async def generate_script_from_idea(
    request: GenerateScriptFromIdeaRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Generate a complete script from a high-level idea using AI.

    This creates the first version of a script generation that can be
    refined iteratively with AI feedback.
    """
    try:
        # TODO: Call AI to generate script from idea
        # For now, create a placeholder generation

        generation_id = str(uuid.uuid4())

        script_gen = ScriptGeneration(
            id=generation_id,
            project_id=request.project_id,
            generation_type="script",
            version=1,
            parent_id=None,

            # Input
            input_idea=request.idea,
            input_genre=request.genre,
            input_style=request.style,
            input_partial_data={},

            # AI feedback
            ai_feedback=request.ai_feedback,
            ai_enhancement_enabled=True,

            # Output (placeholder - will be filled by AI)
            output_prompt=f"Generated script for: {request.idea}",
            output_metadata={"genre": request.genre, "style": request.style},
            output_full_data={
                "script": {
                    "title": "AI Generated Script",
                    "logline": request.idea,
                    "scenes": []
                }
            },

            # Status
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(script_gen)
        await db.commit()
        await db.refresh(script_gen)

        return {
            "id": script_gen.id,
            "generation_type": script_gen.generation_type,
            "version": script_gen.version,
            "output_prompt": script_gen.output_prompt,
            "output_metadata": script_gen.output_metadata,
            "message": "Script generation created. AI implementation pending."
        }

    except Exception as e:
        logger.error(f"Error generating script from idea: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/script/{generation_id}/refine")
async def refine_script_generation(
    generation_id: str,
    request: RefineGenerationRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Refine an existing generation with AI feedback.

    Creates a new version with the parent_id pointing to the original.
    User can provide instructions like "make it darker", "add more tension", etc.
    """
    try:
        # Get parent generation
        result = await db.execute(
            select(ScriptGeneration).where(ScriptGeneration.id == generation_id)
        )
        parent_gen = result.scalar_one_or_none()

        if not parent_gen:
            raise HTTPException(status_code=404, detail="Generation not found")

        # Get next version number
        result = await db.execute(
            select(ScriptGeneration.version)
            .where(and_(
                ScriptGeneration.project_id == parent_gen.project_id,
                ScriptGeneration.generation_type == parent_gen.generation_type
            ))
            .order_by(desc(ScriptGeneration.version))
            .limit(1)
        )
        latest_version = result.scalar()
        next_version = (latest_version or 0) + 1

        # Create new version with AI feedback
        new_gen = ScriptGeneration(
            id=str(uuid.uuid4()),
            project_id=parent_gen.project_id,
            workspace_id=parent_gen.workspace_id,
            user_id=parent_gen.user_id,
            generation_type=parent_gen.generation_type,
            version=next_version,
            parent_id=parent_gen.id,

            # Copy input data
            input_subject=parent_gen.input_subject,
            input_action=parent_gen.input_action,
            input_location=parent_gen.input_location,
            input_style=parent_gen.input_style,
            input_genre=parent_gen.input_genre,
            input_idea=parent_gen.input_idea,
            input_partial_data=parent_gen.input_partial_data,

            # Add AI feedback
            ai_feedback=request.ai_feedback,
            ai_enhancement_enabled=True,

            # TODO: Call AI to refine based on feedback
            # For now, copy output with note about refinement
            output_prompt=f"{parent_gen.output_prompt}\n\n[Refined with: {request.ai_feedback}]",
            output_negative_prompt=parent_gen.output_negative_prompt,
            output_metadata=parent_gen.output_metadata,
            output_full_data=parent_gen.output_full_data,

            # Deactivate parent, activate new version
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Deactivate parent version
        parent_gen.is_active = False
        parent_gen.updated_at = datetime.utcnow()

        db.add(new_gen)
        await db.commit()
        await db.refresh(new_gen)

        return {
            "id": new_gen.id,
            "generation_type": new_gen.generation_type,
            "version": new_gen.version,
            "parent_id": new_gen.parent_id,
            "ai_feedback": new_gen.ai_feedback,
            "output_prompt": new_gen.output_prompt,
            "message": "Refined version created. AI implementation pending."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refining generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Version Management Endpoints
# ============================================================================

@router.get("/script/{project_id}/versions")
async def list_script_versions(
    project_id: str,
    generation_type: str = "script",
    db: AsyncSession = Depends(get_async_db)
):
    """
    List all versions of a script/scene/shot for a project.

    Returns version history so user can see all attempts and switch between them.
    """
    try:
        result = await db.execute(
            select(ScriptGeneration)
            .where(and_(
                ScriptGeneration.project_id == project_id,
                ScriptGeneration.generation_type == generation_type
            ))
            .order_by(desc(ScriptGeneration.created_at))
        )
        generations = result.scalars().all()

        # Find active version
        active_id = next((g.id for g in generations if g.is_active), None)

        # Convert to response format
        generation_responses = []
        for gen in generations:
            generation_responses.append(GenerationResponse(
                id=gen.id,
                generation_type=gen.generation_type,
                version=gen.version,
                parent_id=gen.parent_id,
                input_data={
                    "subject": gen.input_subject,
                    "action": gen.input_action,
                    "location": gen.input_location,
                    "style": gen.input_style,
                    "genre": gen.input_genre,
                    "idea": gen.input_idea,
                    "partial_data": gen.input_partial_data
                },
                output_prompt=gen.output_prompt,
                output_negative_prompt=gen.output_negative_prompt,
                output_metadata=gen.output_metadata,
                is_active=gen.is_active,
                is_favorite=gen.is_favorite,
                rating=gen.rating,
                ai_feedback=gen.ai_feedback,
                created_at=gen.created_at
            ))

        return VersionListResponse(
            generations=generation_responses,
            total_count=len(generation_responses),
            active_version=active_id
        )

    except Exception as e:
        logger.error(f"Error listing versions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/script/generation/{generation_id}")
async def get_generation(
    generation_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get specific generation by ID."""
    try:
        result = await db.execute(
            select(ScriptGeneration).where(ScriptGeneration.id == generation_id)
        )
        generation = result.scalar_one_or_none()

        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")

        return GenerationResponse(
            id=generation.id,
            generation_type=generation.generation_type,
            version=generation.version,
            parent_id=generation.parent_id,
            input_data={
                "subject": generation.input_subject,
                "action": generation.input_action,
                "location": generation.input_location,
                "style": generation.input_style,
                "genre": generation.input_genre,
                "idea": generation.input_idea,
                "partial_data": generation.input_partial_data
            },
            output_prompt=generation.output_prompt,
            output_negative_prompt=generation.output_negative_prompt,
            output_metadata=generation.output_metadata,
            is_active=generation.is_active,
            is_favorite=generation.is_favorite,
            rating=generation.rating,
            ai_feedback=generation.ai_feedback,
            created_at=generation.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/script/generation/{generation_id}/activate")
async def activate_generation(
    generation_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Switch to a different version (activate it).

    Deactivates all other versions of the same generation and activates this one.
    """
    try:
        # Get the target generation
        result = await db.execute(
            select(ScriptGeneration).where(ScriptGeneration.id == generation_id)
        )
        target_gen = result.scalar_one_or_none()

        if not target_gen:
            raise HTTPException(status_code=404, detail="Generation not found")

        # Deactivate all versions of this generation
        result = await db.execute(
            select(ScriptGeneration)
            .where(and_(
                ScriptGeneration.project_id == target_gen.project_id,
                ScriptGeneration.generation_type == target_gen.generation_type
            ))
        )
        all_versions = result.scalars().all()

        for gen in all_versions:
            gen.is_active = False
            gen.updated_at = datetime.utcnow()

        # Activate target version
        target_gen.is_active = True
        target_gen.updated_at = datetime.utcnow()

        await db.commit()

        return {
            "id": target_gen.id,
            "version": target_gen.version,
            "is_active": target_gen.is_active,
            "message": f"Version {target_gen.version} activated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/script/generation/{generation_id}/favorite")
async def toggle_favorite(
    generation_id: str,
    is_favorite: bool,
    db: AsyncSession = Depends(get_async_db)
):
    """Mark/unmark generation as favorite."""
    try:
        result = await db.execute(
            select(ScriptGeneration).where(ScriptGeneration.id == generation_id)
        )
        generation = result.scalar_one_or_none()

        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")

        generation.is_favorite = is_favorite
        generation.updated_at = datetime.utcnow()

        await db.commit()

        return {
            "id": generation.id,
            "is_favorite": generation.is_favorite,
            "message": "Favorite status updated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling favorite: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/script/generation/{generation_id}/rating")
async def rate_generation(
    generation_id: str,
    rating: int = Field(..., ge=1, le=5),
    db: AsyncSession = Depends(get_async_db)
):
    """Rate a generation (1-5 stars)."""
    try:
        result = await db.execute(
            select(ScriptGeneration).where(ScriptGeneration.id == generation_id)
        )
        generation = result.scalar_one_or_none()

        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")

        generation.rating = rating
        generation.updated_at = datetime.utcnow()

        await db.commit()

        return {
            "id": generation.id,
            "rating": generation.rating,
            "message": "Rating updated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Notes/Collaboration Endpoints
# ============================================================================

@router.post("/script/generation/{generation_id}/notes")
async def add_note(
    generation_id: str,
    request: NoteRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Add a note/comment to a generation."""
    try:
        # Verify generation exists
        result = await db.execute(
            select(ScriptGeneration).where(ScriptGeneration.id == generation_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Generation not found")

        note = GenerationNote(
            id=str(uuid.uuid4()),
            generation_id=generation_id,
            generation_table="script_generations",
            note=request.note,
            created_at=datetime.utcnow()
        )

        db.add(note)
        await db.commit()

        return {
            "id": note.id,
            "generation_id": note.generation_id,
            "note": note.note,
            "created_at": note.created_at
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding note: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/script/generation/{generation_id}/notes")
async def get_notes(
    generation_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get all notes for a generation."""
    try:
        result = await db.execute(
            select(GenerationNote)
            .where(and_(
                GenerationNote.generation_id == generation_id,
                GenerationNote.generation_table == "script_generations"
            ))
            .order_by(desc(GenerationNote.created_at))
        )
        notes = result.scalars().all()

        return {
            "notes": [
                {
                    "id": note.id,
                    "note": note.note,
                    "created_at": note.created_at
                }
                for note in notes
            ]
        }

    except Exception as e:
        logger.error(f"Error getting notes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
