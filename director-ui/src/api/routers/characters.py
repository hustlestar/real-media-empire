"""Character API router for visual consistency tracking."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os

from sqlalchemy import select, func
from data.models import Character
from data.async_dao import get_async_db
from image.fal_client import FALClient
from image.replicate_client import ReplicateClient

router = APIRouter()

# Best models for character consistency
CHARACTER_GENERATION_MODELS = {
    "flux-pro": {
        "name": "FLUX.1 Pro",
        "provider": "fal",
        "model_id": "fal-ai/flux-pro",
        "description": "Highest quality, best for photorealistic characters",
        "consistency_score": 9.5,
        "cost_per_image": 0.055
    },
    "flux-dev": {
        "name": "FLUX.1 Dev",
        "provider": "fal",
        "model_id": "fal-ai/flux/dev",
        "description": "Great quality, faster generation",
        "consistency_score": 9.0,
        "cost_per_image": 0.025
    },
    "flux-schnell": {
        "name": "FLUX.1 Schnell",
        "provider": "fal",
        "model_id": "fal-ai/flux/schnell",
        "description": "Fast generation, good for iteration",
        "consistency_score": 8.5,
        "cost_per_image": 0.003
    },
    "sdxl": {
        "name": "Stable Diffusion XL",
        "provider": "replicate",
        "model_id": "stability-ai/sdxl",
        "description": "Reliable and cost-effective",
        "consistency_score": 8.0,
        "cost_per_image": 0.002
    }
}


class CharacterType(str):
    """Character type enum."""
    HUMAN = "human"
    ANIMAL = "animal"
    ROBOT = "robot"
    CREATURE = "creature"
    ALIEN = "alien"
    FANTASY = "fantasy"
    OBJECT = "object"


class CharacterAttributes(BaseModel):
    """Flexible character attributes schema - adapts to character type."""
    # Universal fields
    character_type: str = "human"

    # Human-specific
    age: Optional[str] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    hair_color: Optional[str] = None
    hair_style: Optional[str] = None
    eye_color: Optional[str] = None
    height: Optional[str] = None
    build: Optional[str] = None
    clothing_style: Optional[str] = None

    # Animal-specific
    species: Optional[str] = None
    breed: Optional[str] = None
    fur_color: Optional[str] = None
    fur_texture: Optional[str] = None
    size: Optional[str] = None
    temperament: Optional[str] = None

    # Robot-specific
    model_type: Optional[str] = None
    material: Optional[str] = None
    power_source: Optional[str] = None
    capabilities: Optional[str] = None

    # Creature/Fantasy-specific
    creature_type: Optional[str] = None
    abilities: Optional[str] = None
    habitat: Optional[str] = None
    magic_type: Optional[str] = None

    # Alien-specific
    alien_species: Optional[str] = None
    home_planet: Optional[str] = None
    physiology: Optional[str] = None

    # Universal
    color_scheme: Optional[str] = None
    texture: Optional[str] = None
    distinctive_features: List[str] = []


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
    """Generate AI consistency prompt from character attributes based on type."""
    char_type = attributes.character_type or "human"
    features = ", ".join(attributes.distinctive_features) if attributes.distinctive_features else "none"

    # Build prompt based on character type
    if char_type == "human":
        parts = [
            f"Character: {name} (Human)",
            f"Physical Attributes:",
            attributes.age and f"- Age: {attributes.age}",
            attributes.gender and f"- Gender: {attributes.gender}",
            attributes.ethnicity and f"- Ethnicity: {attributes.ethnicity}",
            attributes.hair_color and attributes.hair_style and f"- Hair: {attributes.hair_color}, {attributes.hair_style}",
            attributes.eye_color and f"- Eyes: {attributes.eye_color}",
            attributes.height and f"- Height: {attributes.height}",
            attributes.build and f"- Build: {attributes.build}",
            attributes.clothing_style and f"- Clothing Style: {attributes.clothing_style}",
            f"- Distinctive Features: {features}",
        ]

    elif char_type == "animal":
        parts = [
            f"Character: {name} ({attributes.species or 'Animal'})",
            f"Animal Characteristics:",
            attributes.species and f"- Species: {attributes.species}",
            attributes.breed and f"- Breed: {attributes.breed}",
            attributes.fur_color and f"- Fur/Coat Color: {attributes.fur_color}",
            attributes.fur_texture and f"- Fur Texture: {attributes.fur_texture}",
            attributes.size and f"- Size: {attributes.size}",
            attributes.temperament and f"- Temperament: {attributes.temperament}",
            attributes.color_scheme and f"- Color Scheme: {attributes.color_scheme}",
            f"- Distinctive Features: {features}",
        ]

    elif char_type == "robot":
        parts = [
            f"Character: {name} (Robot/Android)",
            f"Robot Specifications:",
            attributes.model_type and f"- Model Type: {attributes.model_type}",
            attributes.material and f"- Material: {attributes.material}",
            attributes.power_source and f"- Power Source: {attributes.power_source}",
            attributes.capabilities and f"- Capabilities: {attributes.capabilities}",
            attributes.color_scheme and f"- Color Scheme: {attributes.color_scheme}",
            attributes.build and f"- Build/Form Factor: {attributes.build}",
            f"- Distinctive Features: {features}",
        ]

    elif char_type == "creature" or char_type == "fantasy":
        parts = [
            f"Character: {name} ({attributes.creature_type or 'Fantasy Creature'})",
            f"Creature Characteristics:",
            attributes.creature_type and f"- Type: {attributes.creature_type}",
            attributes.abilities and f"- Abilities: {attributes.abilities}",
            attributes.magic_type and f"- Magic Type: {attributes.magic_type}",
            attributes.habitat and f"- Habitat: {attributes.habitat}",
            attributes.size and f"- Size: {attributes.size}",
            attributes.color_scheme and f"- Color Scheme: {attributes.color_scheme}",
            attributes.texture and f"- Texture: {attributes.texture}",
            f"- Distinctive Features: {features}",
        ]

    elif char_type == "alien":
        parts = [
            f"Character: {name} ({attributes.alien_species or 'Alien Being'})",
            f"Alien Characteristics:",
            attributes.alien_species and f"- Species: {attributes.alien_species}",
            attributes.home_planet and f"- Home Planet: {attributes.home_planet}",
            attributes.physiology and f"- Physiology: {attributes.physiology}",
            attributes.abilities and f"- Abilities: {attributes.abilities}",
            attributes.color_scheme and f"- Color Scheme: {attributes.color_scheme}",
            attributes.height and f"- Height: {attributes.height}",
            f"- Distinctive Features: {features}",
        ]

    elif char_type == "object":
        parts = [
            f"Character: {name} (Animated Object)",
            f"Object Characteristics:",
            attributes.model_type and f"- Type: {attributes.model_type}",
            attributes.material and f"- Material: {attributes.material}",
            attributes.color_scheme and f"- Color Scheme: {attributes.color_scheme}",
            attributes.texture and f"- Texture: {attributes.texture}",
            attributes.size and f"- Size: {attributes.size}",
            f"- Distinctive Features: {features}",
        ]

    else:
        # Fallback for unknown types
        parts = [
            f"Character: {name}",
            f"Description: {char_type}",
            attributes.color_scheme and f"- Color Scheme: {attributes.color_scheme}",
            f"- Distinctive Features: {features}",
        ]

    # Filter out None values and join
    prompt_lines = [part for part in parts if part]
    prompt = "\n".join(prompt_lines)
    prompt += "\n\nMaintain consistent appearance across all generated images."

    return prompt


@router.post("", response_model=CharacterResponse)
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


@router.get("", response_model=Dict[str, List[CharacterResponse]])
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


@router.get("/{character_id}", response_model=CharacterResponse)
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


@router.put("/{character_id}", response_model=CharacterResponse)
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


@router.delete("/{character_id}")
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


@router.post("/{character_id}/add-project")
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


@router.get("/types/available")
async def get_available_character_types():
    """Get list of available character types with their attributes."""
    return {
        "types": {
            "human": {
                "name": "Human",
                "description": "Human characters with realistic attributes",
                "icon": "👤",
                "attributes": ["age", "gender", "ethnicity", "hair_color", "hair_style", "eye_color", "height", "build", "clothing_style"]
            },
            "animal": {
                "name": "Animal",
                "description": "Pets, wildlife, and animal characters",
                "icon": "🐾",
                "attributes": ["species", "breed", "fur_color", "fur_texture", "size", "temperament", "color_scheme"]
            },
            "robot": {
                "name": "Robot/Android",
                "description": "Mechanical and robotic characters",
                "icon": "🤖",
                "attributes": ["model_type", "material", "power_source", "capabilities", "color_scheme", "build"]
            },
            "creature": {
                "name": "Creature",
                "description": "Fantasy creatures and monsters",
                "icon": "🐉",
                "attributes": ["creature_type", "abilities", "habitat", "size", "color_scheme", "texture"]
            },
            "fantasy": {
                "name": "Fantasy",
                "description": "Fantasy beings with magical properties",
                "icon": "✨",
                "attributes": ["creature_type", "magic_type", "abilities", "habitat", "color_scheme"]
            },
            "alien": {
                "name": "Alien",
                "description": "Extraterrestrial beings",
                "icon": "👽",
                "attributes": ["alien_species", "home_planet", "physiology", "abilities", "color_scheme", "height"]
            },
            "object": {
                "name": "Animated Object",
                "description": "Inanimate objects with personality",
                "icon": "📦",
                "attributes": ["model_type", "material", "color_scheme", "texture", "size"]
            }
        },
        "default": "human"
    }


@router.get("/models/available")
async def get_available_models():
    """Get list of available models for character generation with consistency scores."""
    return {
        "models": CHARACTER_GENERATION_MODELS,
        "recommended": "flux-dev"  # Best balance of quality and cost
    }


class GenerateCharacterImageRequest(BaseModel):
    """Request schema for generating character images."""
    character_id: Optional[str] = None  # If provided, use character's consistency prompt
    prompt: Optional[str] = None  # Custom prompt or refinement instructions
    model: str = "flux-dev"  # Model to use for generation
    negative_prompt: Optional[str] = None
    num_images: int = 1  # Number of variations to generate
    seed: Optional[int] = None  # For reproducibility
    add_to_character: bool = False  # Auto-add generated image to character's reference images


class GenerateCharacterImageResponse(BaseModel):
    """Response schema for character image generation."""
    images: List[str]  # URLs of generated images
    model_used: str
    prompt_used: str
    cost: float
    generation_time: float


@router.post("/generate-image", response_model=GenerateCharacterImageResponse)
async def generate_character_image(
    request: GenerateCharacterImageRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Generate character image using AI with model selection and iteration support.

    This endpoint supports:
    - Generating images for existing characters (uses consistency prompt)
    - Standalone image generation with custom prompts
    - Multiple models with different quality/cost tradeoffs
    - Iteration with seed for reproducibility
    - Automatic addition to character reference images
    """
    import time
    start_time = time.time()

    # Validate model
    if request.model not in CHARACTER_GENERATION_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model. Available: {list(CHARACTER_GENERATION_MODELS.keys())}"
        )

    model_config = CHARACTER_GENERATION_MODELS[request.model]

    # Build final prompt
    final_prompt = request.prompt or ""

    if request.character_id:
        # Get character and use consistency prompt
        result = await db.execute(select(Character).filter(Character.id == request.character_id))
        character = result.scalar_one_or_none()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Combine consistency prompt with custom prompt/refinement
        if request.prompt:
            final_prompt = f"{character.consistency_prompt}\n\nRefinement: {request.prompt}"
        else:
            final_prompt = character.consistency_prompt
    elif not request.prompt:
        raise HTTPException(
            status_code=400,
            detail="Either character_id or prompt must be provided"
        )

    # Generate images using appropriate provider
    generated_images = []
    provider = model_config["provider"]

    try:
        if provider == "fal":
            client = FALClient()
            for i in range(request.num_images):
                image_url = await client.generate_image(
                    prompt=final_prompt,
                    model=model_config["model_id"],
                    negative_prompt=request.negative_prompt,
                    seed=request.seed + i if request.seed else None
                )
                generated_images.append(image_url)

        elif provider == "replicate":
            client = ReplicateClient()
            for i in range(request.num_images):
                image_url = await client.generate_image(
                    prompt=final_prompt,
                    model=model_config["model_id"],
                    negative_prompt=request.negative_prompt,
                    seed=request.seed + i if request.seed else None
                )
                generated_images.append(image_url)

        else:
            raise HTTPException(status_code=500, detail=f"Unsupported provider: {provider}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

    # Add to character reference images if requested
    if request.add_to_character and request.character_id:
        result = await db.execute(select(Character).filter(Character.id == request.character_id))
        character = result.scalar_one_or_none()
        if character:
            if character.reference_images is None:
                character.reference_images = []
            character.reference_images.extend(generated_images)
            character.updated_at = datetime.utcnow()
            await db.flush()

    generation_time = time.time() - start_time
    total_cost = model_config["cost_per_image"] * request.num_images

    return GenerateCharacterImageResponse(
        images=generated_images,
        model_used=request.model,
        prompt_used=final_prompt,
        cost=total_cost,
        generation_time=generation_time
    )
