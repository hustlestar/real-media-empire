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


class RatingRequest(BaseModel):
    """Request to rate a generation."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")


class GenerateShotRequest(BaseModel):
    """Request to generate a shot with AI."""
    subject: Optional[str] = Field(None, description="Subject/character description")
    action: Optional[str] = Field(None, description="What's happening in the shot")
    location: Optional[str] = Field(None, description="Location/setting description")
    camera_motion: Optional[str] = Field(None, description="Camera movement type")
    shot_type: Optional[str] = Field(None, description="Shot type (close-up, wide, etc.)")
    lighting: Optional[str] = Field(None, description="Lighting description")
    emotion: Optional[str] = Field(None, description="Emotional tone")
    style: Optional[str] = Field("cinematic", description="Visual style")
    duration_seconds: Optional[float] = Field(3.0, description="Shot duration in seconds")
    workspace_id: Optional[str] = Field(None, description="Workspace for organizing shots")
    project_id: Optional[str] = Field(None, description="Project to associate with")
    film_id: Optional[str] = Field(None, description="Film/project ID for shot context")
    sequence_order: Optional[int] = Field(None, description="Order in storyboard sequence")
    ai_feedback: Optional[str] = Field(None, description="Additional AI instructions for generation")


class RefineShotRequest(BaseModel):
    """Request to refine a shot with AI feedback."""
    shot_id: str = Field(..., description="ID of shot to refine")
    ai_feedback: str = Field(..., description="Refinement instructions (e.g., 'more dramatic', 'darker mood')")


class ShotResponse(BaseModel):
    """Response with shot generation data."""
    id: str
    version: int
    parent_id: Optional[str]

    # Shot configuration
    prompt: Optional[str]
    negative_prompt: Optional[str]
    shot_type: Optional[str]
    camera_motion: Optional[str]
    lighting: Optional[str]
    emotion: Optional[str]
    duration_seconds: float

    # Input data
    input_subject: Optional[str]
    input_action: Optional[str]
    input_location: Optional[str]

    # AI feedback
    ai_feedback: Optional[str]

    # Status
    is_active: bool
    is_favorite: bool
    rating: Optional[int]

    created_at: datetime

    class Config:
        from_attributes = True


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

@router.post("/generate-from-idea")
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


@router.post("/{generation_id}/refine")
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

@router.get("/{project_id}/versions")
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


@router.get("/generation/{generation_id}")
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


@router.put("/generation/{generation_id}/activate")
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


@router.put("/generation/{generation_id}/favorite")
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


@router.put("/generation/{generation_id}/rating")
async def rate_generation(
    generation_id: str,
    request: RatingRequest,
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

        generation.rating = request.rating
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

@router.post("/generation/{generation_id}/notes")
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


@router.get("/generation/{generation_id}/notes")
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


# ============================================================================
# Shot Studio Endpoints - Fast iterative shot generation with AI
# ============================================================================

@router.post("/shot/generate", response_model=ShotResponse)
async def generate_shot(
    request: GenerateShotRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Generate a new shot with AI assistance.

    This creates the first version of a shot that can be refined
    iteratively with AI feedback.
    """
    try:
        shot_id = str(uuid.uuid4())

        # Build AI prompt from inputs
        prompt_parts = []
        if request.subject:
            prompt_parts.append(f"Subject: {request.subject}")
        if request.action:
            prompt_parts.append(f"Action: {request.action}")
        if request.location:
            prompt_parts.append(f"Location: {request.location}")
        if request.lighting:
            prompt_parts.append(f"Lighting: {request.lighting}")
        if request.emotion:
            prompt_parts.append(f"Emotion: {request.emotion}")

        base_prompt = ", ".join(prompt_parts) if prompt_parts else "Cinematic shot"

        # Add style and shot type
        if request.shot_type:
            base_prompt = f"{request.shot_type} shot, {base_prompt}"
        if request.style:
            base_prompt = f"{request.style} style, {base_prompt}"
        if request.ai_feedback:
            base_prompt = f"{base_prompt}. {request.ai_feedback}"

        # TODO: Call AI service to enhance prompt if needed

        shot = ShotGeneration(
            id=shot_id,
            workspace_id=request.workspace_id,  # Workspace organization
            scene_id=None,  # Standalone shot (not part of scene)
            film_id=request.film_id,  # Film/project association
            shot_number=1,
            sequence_order=request.sequence_order,  # Storyboard ordering
            version=1,
            parent_id=None,
            prompt=base_prompt,
            negative_prompt="blurry, low quality, distorted",
            shot_type=request.shot_type,
            camera_motion=request.camera_motion,
            lighting=request.lighting,
            emotion=request.emotion,
            shot_metadata={
                "input_subject": request.subject,
                "input_action": request.action,
                "input_location": request.location,
                "style": request.style,
                "project_id": request.project_id
            },
            duration_seconds=request.duration_seconds or 3.0,
            ai_feedback=request.ai_feedback,
            is_active=True,
            is_favorite=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(shot)
        await db.commit()
        await db.refresh(shot)

        return ShotResponse(
            id=shot.id,
            version=shot.version,
            parent_id=shot.parent_id,
            prompt=shot.prompt,
            negative_prompt=shot.negative_prompt,
            shot_type=shot.shot_type,
            camera_motion=shot.camera_motion,
            lighting=shot.lighting,
            emotion=shot.emotion,
            duration_seconds=shot.duration_seconds,
            input_subject=request.subject,
            input_action=request.action,
            input_location=request.location,
            ai_feedback=shot.ai_feedback,
            is_active=shot.is_active,
            is_favorite=shot.is_favorite,
            rating=shot.rating,
            created_at=shot.created_at
        )

    except Exception as e:
        logger.error(f"Error generating shot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shot/{shot_id}/refine", response_model=ShotResponse)
async def refine_shot(
    shot_id: str,
    request: RefineShotRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Refine an existing shot with AI feedback.

    Creates a new version based on the parent shot with refinements applied.
    """
    try:
        # Get parent shot
        result = await db.execute(
            select(ShotGeneration).where(ShotGeneration.id == shot_id)
        )
        parent_shot = result.scalar_one_or_none()

        if not parent_shot:
            raise HTTPException(status_code=404, detail="Shot not found")

        # Get next version number for this shot_number
        version_result = await db.execute(
            select(ShotGeneration.version)
            .where(ShotGeneration.shot_number == parent_shot.shot_number)
            .order_by(desc(ShotGeneration.version))
            .limit(1)
        )
        latest_version = version_result.scalar() or 0
        next_version = latest_version + 1

        # Create refined prompt
        refined_prompt = f"{parent_shot.prompt}. Refinement: {request.ai_feedback}"

        # TODO: Call AI service to apply refinements intelligently

        # Create new version
        new_shot_id = str(uuid.uuid4())
        new_shot = ShotGeneration(
            id=new_shot_id,
            scene_id=parent_shot.scene_id,
            shot_number=parent_shot.shot_number,
            version=next_version,
            parent_id=parent_shot.id,
            prompt=refined_prompt,
            negative_prompt=parent_shot.negative_prompt,
            shot_type=parent_shot.shot_type,
            camera_motion=parent_shot.camera_motion,
            lighting=parent_shot.lighting,
            emotion=parent_shot.emotion,
            shot_metadata=parent_shot.shot_metadata,
            duration_seconds=parent_shot.duration_seconds,
            ai_feedback=request.ai_feedback,
            is_active=True,
            is_favorite=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Deactivate parent
        parent_shot.is_active = False
        parent_shot.updated_at = datetime.utcnow()

        db.add(new_shot)
        await db.commit()
        await db.refresh(new_shot)

        metadata = new_shot.shot_metadata or {}

        return ShotResponse(
            id=new_shot.id,
            version=new_shot.version,
            parent_id=new_shot.parent_id,
            prompt=new_shot.prompt,
            negative_prompt=new_shot.negative_prompt,
            shot_type=new_shot.shot_type,
            camera_motion=new_shot.camera_motion,
            lighting=new_shot.lighting,
            emotion=new_shot.emotion,
            duration_seconds=new_shot.duration_seconds,
            input_subject=metadata.get("input_subject"),
            input_action=metadata.get("input_action"),
            input_location=metadata.get("input_location"),
            ai_feedback=new_shot.ai_feedback,
            is_active=new_shot.is_active,
            is_favorite=new_shot.is_favorite,
            rating=new_shot.rating,
            created_at=new_shot.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refining shot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/shot/versions")
async def list_shot_versions(
    project_id: str = "default",
    db: AsyncSession = Depends(get_async_db)
):
    """List all shot versions for a project."""
    try:
        # Get all shots (no filtering by shot_number to show all versions)
        result = await db.execute(
            select(ShotGeneration)
            .order_by(desc(ShotGeneration.created_at))
        )
        shots = result.scalars().all()

        shot_responses = []
        for shot in shots:
            metadata = shot.shot_metadata or {}
            shot_responses.append(ShotResponse(
                id=shot.id,
                version=shot.version,
                parent_id=shot.parent_id,
                prompt=shot.prompt,
                negative_prompt=shot.negative_prompt,
                shot_type=shot.shot_type,
                camera_motion=shot.camera_motion,
                lighting=shot.lighting,
                emotion=shot.emotion,
                duration_seconds=shot.duration_seconds,
                input_subject=metadata.get("input_subject"),
                input_action=metadata.get("input_action"),
                input_location=metadata.get("input_location"),
                ai_feedback=shot.ai_feedback,
                is_active=shot.is_active,
                is_favorite=shot.is_favorite,
                rating=shot.rating,
                created_at=shot.created_at
            ))

        active_shot = next((s for s in shots if s.is_active), None)

        return {
            "versions": shot_responses,  # Changed from "shots" to "versions"
            "total_count": len(shot_responses),
            "active_version_id": active_shot.id if active_shot else None  # Match frontend
        }

    except Exception as e:
        logger.error(f"Error listing shot versions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/shot/{shot_id}/activate")
async def activate_shot(
    shot_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Activate a specific shot version."""
    try:
        result = await db.execute(
            select(ShotGeneration).where(ShotGeneration.id == shot_id)
        )
        target_shot = result.scalar_one_or_none()

        if not target_shot:
            raise HTTPException(status_code=404, detail="Shot not found")

        # Deactivate all versions of this shot
        all_result = await db.execute(
            select(ShotGeneration)
            .where(ShotGeneration.shot_number == target_shot.shot_number)
        )
        all_shots = all_result.scalars().all()

        for shot in all_shots:
            shot.is_active = False
            shot.updated_at = datetime.utcnow()

        # Activate target
        target_shot.is_active = True
        target_shot.updated_at = datetime.utcnow()

        await db.commit()

        return {"id": target_shot.id, "message": "Shot activated"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating shot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/shot/{shot_id}/favorite")
async def toggle_shot_favorite(
    shot_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Toggle favorite status for a shot."""
    try:
        result = await db.execute(
            select(ShotGeneration).where(ShotGeneration.id == shot_id)
        )
        shot = result.scalar_one_or_none()

        if not shot:
            raise HTTPException(status_code=404, detail="Shot not found")

        shot.is_favorite = not shot.is_favorite
        shot.updated_at = datetime.utcnow()

        await db.commit()

        return {
            "id": shot.id,
            "is_favorite": shot.is_favorite,
            "message": "Favorite toggled"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling favorite: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/shot/{shot_id}/rating")
async def rate_shot(
    shot_id: str,
    request: RatingRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Rate a shot (1-5 stars)."""
    try:
        result = await db.execute(
            select(ShotGeneration).where(ShotGeneration.id == shot_id)
        )
        shot = result.scalar_one_or_none()

        if not shot:
            raise HTTPException(status_code=404, detail="Shot not found")

        shot.rating = request.rating
        shot.updated_at = datetime.utcnow()

        await db.commit()

        return {
            "id": shot.id,
            "rating": shot.rating,
            "message": "Rating updated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rating shot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
