"""Character API router for visual consistency tracking."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from sqlalchemy import select, func
from data.models import Character
from data.async_dao import get_async_db

router = APIRouter()


class CharacterAttributes(BaseModel):
    """Character attributes schema."""
    age: str
    gender: str
    ethnicity: str
    hair_color: str
    hair_style: str
    eye_color: str
    height: str
    build: str
    clothing_style: str
    distinctive_features: List[str]


class CharacterCreate(BaseModel):
    """Character creation schema."""
    workspace_id: str
    name: str
    description: str
    reference_images: List[str] = []
    attributes: CharacterAttributes
    projects_used: List[str] = []  # Deprecated: Use shot_characters table instead


class CharacterUpdate(BaseModel):
    """Character update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    reference_images: Optional[List[str]] = None
    attributes: Optional[CharacterAttributes] = None
    projects_used: Optional[List[str]] = None


class CharacterResponse(BaseModel):
    """Character response schema."""
    id: str
    workspace_id: str
    name: str
    description: str
    reference_images: List[str]
    attributes: Dict[str, Any]
    consistency_prompt: str
    projects_used: List[str]  # Deprecated: Use shot_characters table instead
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


def generate_consistency_prompt(name: str, attributes: CharacterAttributes) -> str:
    """Generate AI consistency prompt from character attributes."""
    features = ", ".join(attributes.distinctive_features) if attributes.distinctive_features else "none"

    prompt = f"""Character: {name}
Physical Attributes:
- Age: {attributes.age}
- Gender: {attributes.gender}
- Ethnicity: {attributes.ethnicity}
- Hair: {attributes.hair_color}, {attributes.hair_style}
- Eyes: {attributes.eye_color}
- Height: {attributes.height}
- Build: {attributes.build}
- Clothing Style: {attributes.clothing_style}
- Distinctive Features: {features}

Maintain consistent appearance across all generated images."""

    return prompt


@router.post("/characters", response_model=CharacterResponse)
async def create_character(
    character: CharacterCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new character within a workspace."""
    # Verify workspace exists
    from data.models import Workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == character.workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{character.workspace_id}' not found")

    # Check if character with same name exists in this workspace
    result = await db.execute(select(Character).filter(
        Character.workspace_id == character.workspace_id,
        Character.name == character.name
    ))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Character with name '{character.name}' already exists in this workspace"
        )

    # Generate consistency prompt
    consistency_prompt = generate_consistency_prompt(character.name, character.attributes)

    # Create new character
    new_character = Character(
        id=str(uuid.uuid4()),
        workspace_id=character.workspace_id,
        name=character.name,
        description=character.description,
        reference_images=character.reference_images,
        attributes=character.attributes.dict(),
        consistency_prompt=consistency_prompt,
        projects_used=character.projects_used,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_character)
    await db.flush()
    await db.refresh(new_character)

    return new_character


@router.get("/characters", response_model=Dict[str, List[CharacterResponse]])
async def list_characters(
    workspace_id: Optional[str] = None,
    search: Optional[str] = None,
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """List all characters with optional filtering.

    Args:
        workspace_id: Filter by workspace (recommended for multi-tenant isolation)
        search: Search in character name or description
        project_id: Filter by project_id in projects_used array (deprecated)
    """
    query = select(Character)

    # Filter by workspace (recommended)
    if workspace_id:
        query = query.filter(Character.workspace_id == workspace_id)

    if search:
        query = query.filter(
            (Character.name.ilike(f"%{search}%")) |
            (Character.description.ilike(f"%{search}%"))
        )

    if project_id:
        # Filter by project_id in projects_used JSON array (deprecated)
        # TODO: Use shot_characters table instead
        query = query.filter(Character.projects_used.contains([project_id]))

    query = query.order_by(Character.created_at.desc())
    result = await db.execute(query)
    characters = list(result.scalars().all())

    return {"characters": characters}


@router.get("/characters/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific character by ID."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return character


@router.put("/characters/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    updates: CharacterUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a character."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Update fields if provided
    if updates.name is not None:
        # Check for name conflicts
        result = await db.execute(select(Character).filter(
            Character.name == updates.name,
            Character.id != character_id
        ))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail=f"Character with name '{updates.name}' already exists")
        character.name = updates.name

    if updates.description is not None:
        character.description = updates.description

    if updates.reference_images is not None:
        character.reference_images = updates.reference_images

    if updates.attributes is not None:
        character.attributes = updates.attributes.dict()
        # Regenerate consistency prompt
        character.consistency_prompt = generate_consistency_prompt(
            character.name,
            updates.attributes
        )

    if updates.projects_used is not None:
        character.projects_used = updates.projects_used

    character.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(character)

    return character


@router.delete("/characters/{character_id}")
async def delete_character(
    character_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a character."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    await db.delete(character)
    await db.flush()

    return {"message": "Character deleted successfully", "id": character_id}


@router.post("/characters/{character_id}/add-project")
async def add_character_to_project(
    character_id: str,
    project_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Add a character to a project."""
    result = await db.execute(select(Character).filter(Character.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if character.projects_used is None:
        character.projects_used = []

    if project_id not in character.projects_used:
        character.projects_used.append(project_id)
        character.updated_at = datetime.utcnow()
        await db.flush()

    return {"message": "Character added to project", "character_id": character_id, "project_id": project_id}
