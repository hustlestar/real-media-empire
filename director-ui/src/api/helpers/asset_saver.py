"""
Asset Saver Helper - Save all generated content using unified Asset model.

This module ensures that all AI-generated content (images, videos, scripts, audio, etc.)
is saved as assets with proper relationships for reusability, cost tracking, and audit trail.

Uses SQLAlchemy ORM directly for database operations.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncSession

from data.models import Asset, AssetRelationship

if TYPE_CHECKING:
    from uuid import UUID


async def save_generation_as_asset(
    db: AsyncSession,
    workspace_id: str,
    name: str,
    asset_type: str,  # 'image', 'video', 'audio', 'text', 'script'
    url: str,
    source: str = "generation",
    character_id: Optional[str] = None,
    generation_cost: Optional[float] = None,
    generation_metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    file_path: Optional[str] = None,
    size: Optional[int] = None,
    duration: Optional[float] = None,
    thumbnail_url: Optional[str] = None,  # Deprecated - use asset_metadata
    asset_metadata: Optional[Dict[str, Any]] = None
) -> "UUID":
    """
    Save a generated asset using SQLAlchemy ORM with proper relationships.

    Args:
        db: Database session
        workspace_id: Workspace this asset belongs to
        name: Asset name (descriptive)
        asset_type: Type of asset (image, video, audio, text, script)
        url: URL or path to the asset
        source: Source of asset (default: 'generation', can be 'upload', 'import')
        character_id: Optional character this asset is related to (creates relationship)
        generation_cost: Cost in USD to generate this asset
        generation_metadata: Generation details (model, prompt, provider, etc.)
        tags: List of tags for categorization
        file_path: Local file path if applicable
        size: File size in bytes
        duration: Duration for video/audio assets in seconds
        thumbnail_url: DEPRECATED - use asset_metadata instead
        asset_metadata: Additional metadata (dimensions, codec, thumbnail_url, etc.)

    Returns:
        Created Asset UUID
    """
    # Handle deprecated thumbnail_url
    if thumbnail_url and asset_metadata is None:
        asset_metadata = {"thumbnail_url": thumbnail_url}
    elif thumbnail_url and asset_metadata and "thumbnail_url" not in asset_metadata:
        asset_metadata["thumbnail_url"] = thumbnail_url

    # Initialize metadata if not provided
    if asset_metadata is None:
        asset_metadata = {}
    if generation_metadata is None:
        generation_metadata = {}
    if tags is None:
        tags = []

    # Create asset
    asset_id = str(uuid.uuid4())
    asset = Asset(
        id=asset_id,
        workspace_id=workspace_id,
        type=asset_type,
        name=name,
        url=url,
        file_path=file_path,
        size=size,
        duration=duration,
        asset_metadata=asset_metadata,
        tags=tags,
        source=source,
        generation_cost=generation_cost,
        generation_metadata=generation_metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(asset)
    await db.flush()  # Flush to ensure the asset is persisted before creating relationships

    # Create relationship to character if provided
    if character_id:
        relationship = AssetRelationship(
            id=str(uuid.uuid4()),
            parent_asset_id=character_id,
            child_asset_id=asset_id,
            relationship_type="reference_for",
            relationship_metadata={},
            created_at=datetime.utcnow()
        )
        db.add(relationship)
        await db.flush()

    return uuid.UUID(asset_id)


async def save_script_as_asset(
    db: AsyncSession,
    workspace_id: str,
    script_id: str,
    script_title: str,
    script_content: str,
    generation_cost: Optional[float] = None,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
    genre: Optional[str] = None,
    style: Optional[str] = None
) -> "UUID":
    """
    Save a generated script as a text asset.

    Args:
        db: Database session
        workspace_id: Workspace ID
        script_id: Script generation ID
        script_title: Title of the script
        script_content: Full script text content
        generation_cost: Cost to generate the script
        model: AI model used
        prompt: Prompt used for generation
        genre: Script genre
        style: Script style

    Returns:
        Created Asset UUID
    """
    return await save_generation_as_asset(
        db=db,
        workspace_id=workspace_id,
        name=f"Script: {script_title}",
        asset_type="script",
        url=f"script://{script_id}",  # Virtual URL for database-stored content
        source="generation",
        generation_cost=generation_cost,
        generation_metadata={
            "script_id": script_id,
            "model": model,
            "prompt": prompt,
            "genre": genre,
            "style": style,
            "content_length": len(script_content) if script_content else 0,
            "generated_at": datetime.utcnow().isoformat()
        },
        tags=["ai-generated", "script", genre or "unknown-genre"],
        asset_metadata={
            "content": script_content,  # Store full script content
            "type": "script",
            "format": "text"
        }
    )


async def save_shot_as_asset(
    db: AsyncSession,
    workspace_id: str,
    shot_id: str,
    shot_name: str,
    video_url: Optional[str] = None,
    image_url: Optional[str] = None,
    audio_url: Optional[str] = None,
    prompt: Optional[str] = None,
    generation_cost: Optional[float] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    duration: Optional[float] = None,
    thumbnail_url: Optional[str] = None,
    character_ids: Optional[List[str]] = None
) -> List["UUID"]:
    """
    Save a generated shot's outputs (video, image, audio) as assets.

    A shot can produce multiple assets (video, reference image, audio).
    This function saves each one separately for reusability.

    Args:
        db: Database session
        workspace_id: Workspace ID
        shot_id: Shot generation ID
        shot_name: Descriptive name for the shot
        video_url: Generated video URL
        image_url: Generated image/frame URL
        audio_url: Generated audio URL
        prompt: Prompt used for generation
        generation_cost: Total cost for the shot
        provider: Provider used (minimax, kling, runway, etc.)
        model: Model used
        duration: Video duration in seconds
        thumbnail_url: Thumbnail URL
        character_ids: List of character IDs appearing in this shot

    Returns:
        List of created Asset UUIDs
    """
    assets = []

    # Calculate cost per asset (distribute evenly if not specified per type)
    cost_per_asset = generation_cost / 3 if generation_cost else None

    base_metadata = {
        "shot_id": shot_id,
        "prompt": prompt,
        "provider": provider,
        "model": model,
        "character_ids": character_ids or [],
        "generated_at": datetime.utcnow().isoformat()
    }

    base_tags = ["ai-generated", "shot", provider or "unknown-provider"]

    # Save video asset
    if video_url:
        video_asset = await save_generation_as_asset(
            db=db,
            workspace_id=workspace_id,
            name=f"Shot Video: {shot_name}",
            asset_type="video",
            url=video_url,
            source="generation",
            generation_cost=cost_per_asset,
            generation_metadata={**base_metadata, "asset_type": "video"},
            tags=[*base_tags, "video"],
            duration=duration,
            thumbnail_url=thumbnail_url
        )
        assets.append(video_asset)

    # Save image asset
    if image_url:
        image_asset = await save_generation_as_asset(
            db=db,
            workspace_id=workspace_id,
            name=f"Shot Image: {shot_name}",
            asset_type="image",
            url=image_url,
            source="generation",
            generation_cost=cost_per_asset,
            generation_metadata={**base_metadata, "asset_type": "image"},
            tags=[*base_tags, "image", "reference-frame"]
        )
        assets.append(image_asset)

    # Save audio asset
    if audio_url:
        audio_asset = await save_generation_as_asset(
            db=db,
            workspace_id=workspace_id,
            name=f"Shot Audio: {shot_name}",
            asset_type="audio",
            url=audio_url,
            source="generation",
            generation_cost=cost_per_asset,
            generation_metadata={**base_metadata, "asset_type": "audio"},
            tags=[*base_tags, "audio"],
            duration=duration
        )
        assets.append(audio_asset)

    return assets


async def save_film_as_asset(
    db: AsyncSession,
    workspace_id: str,
    film_id: str,
    film_title: str,
    video_url: str,
    generation_cost: float,
    duration: Optional[float] = None,
    thumbnail_url: Optional[str] = None,
    provider: Optional[str] = None,
    shots_count: Optional[int] = None,
    character_ids: Optional[List[str]] = None
) -> "UUID":
    """
    Save a complete generated film as a video asset.

    Args:
        db: Database session
        workspace_id: Workspace ID
        film_id: Film project ID
        film_title: Title of the film
        video_url: Final compiled video URL
        generation_cost: Total cost to generate the film
        duration: Total duration in seconds
        thumbnail_url: Thumbnail URL
        provider: Provider used for generation
        shots_count: Number of shots in the film
        character_ids: List of character IDs appearing in the film

    Returns:
        Created Asset UUID
    """
    return await save_generation_as_asset(
        db=db,
        workspace_id=workspace_id,
        name=f"Film: {film_title}",
        asset_type="video",
        url=video_url,
        source="generation",
        generation_cost=generation_cost,
        generation_metadata={
            "film_id": film_id,
            "provider": provider,
            "shots_count": shots_count,
            "character_ids": character_ids or [],
            "type": "complete_film",
            "generated_at": datetime.utcnow().isoformat()
        },
        tags=["ai-generated", "film", "complete", provider or "unknown-provider"],
        duration=duration,
        thumbnail_url=thumbnail_url,
        asset_metadata={
            "type": "film",
            "shots_count": shots_count
        }
    )


async def save_audio_as_asset(
    db: AsyncSession,
    workspace_id: str,
    name: str,
    audio_url: str,
    generation_cost: Optional[float] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    text: Optional[str] = None,
    voice_id: Optional[str] = None,
    duration: Optional[float] = None,
    character_id: Optional[str] = None
) -> "UUID":
    """
    Save generated audio (TTS, voice clone, etc.) as an audio asset.

    Args:
        db: Database session
        workspace_id: Workspace ID
        name: Asset name
        audio_url: Audio file URL
        generation_cost: Cost to generate
        provider: Provider used (elevenlabs, openai, google, etc.)
        model: Model used
        text: Text that was converted to speech
        voice_id: Voice ID used
        duration: Audio duration in seconds
        character_id: Character this voice belongs to

    Returns:
        Created Asset UUID
    """
    return await save_generation_as_asset(
        db=db,
        workspace_id=workspace_id,
        character_id=character_id,
        name=name,
        asset_type="audio",
        url=audio_url,
        source="generation",
        generation_cost=generation_cost,
        generation_metadata={
            "provider": provider,
            "model": model,
            "text": text,
            "text_length": len(text) if text else 0,
            "voice_id": voice_id,
            "generated_at": datetime.utcnow().isoformat()
        },
        tags=["ai-generated", "audio", "tts", provider or "unknown-provider"],
        duration=duration
    )
