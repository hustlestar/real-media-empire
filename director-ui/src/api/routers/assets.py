"""Asset API router for media file tracking and management."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import shutil
from pathlib import Path

from sqlalchemy import select, func
from data.models import Asset
from data.async_dao import get_async_db

router = APIRouter()


class AssetCreate(BaseModel):
    """Asset creation schema."""
    workspace_id: str
    name: str
    type: str  # image, video, audio, script, text, shot, shot_take, film, character_ref, scene
    url: Optional[str] = None
    file_path: Optional[str] = None
    size: Optional[int] = None
    duration: Optional[float] = None
    tags: List[str] = []
    asset_metadata: Optional[Dict[str, Any]] = {}
    source: Optional[str] = None  # upload, generation, import, derivative
    generation_cost: Optional[float] = None
    generation_metadata: Optional[Dict[str, Any]] = None


class AssetUpdate(BaseModel):
    """Asset update schema."""
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    asset_metadata: Optional[Dict[str, Any]] = None


class AssetResponse(BaseModel):
    """Asset response schema - matches database model."""
    id: str
    workspace_id: Optional[str]
    name: str
    type: str
    url: Optional[str]
    file_path: Optional[str]
    size: Optional[int]
    duration: Optional[float]
    tags: List[str]
    asset_metadata: Dict[str, Any]
    source: Optional[str]
    generation_cost: Optional[float]
    generation_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Asset list response with pagination."""
    assets: List[AssetResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=AssetResponse)
async def create_asset(
    asset: AssetCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new asset record within a workspace."""
    # Verify workspace exists
    from data.models import Workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == asset.workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{asset.workspace_id}' not found")

    new_asset = Asset(
        id=str(uuid.uuid4()),
        workspace_id=asset.workspace_id,
        name=asset.name,
        type=asset.type,
        url=asset.url,
        file_path=asset.file_path,
        size=asset.size,
        duration=asset.duration,
        tags=asset.tags,
        asset_metadata=asset.asset_metadata or {},
        source=asset.source,
        generation_cost=asset.generation_cost,
        generation_metadata=asset.generation_metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_asset)
    await db.flush()
    await db.refresh(new_asset)

    return new_asset


@router.post("/upload", response_model=AssetResponse)
async def upload_asset(
    workspace_id: str = Query(..., description="Workspace ID"),
    file: UploadFile = File(...),
    tags: Optional[str] = Query(None),  # Comma-separated tags
    db: AsyncSession = Depends(get_async_db)
):
    """Upload a new asset file to a workspace."""
    # Verify workspace exists
    from data.models import Workspace
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found")
    # Create upload directory
    upload_dir = Path("uploads/assets")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    # Determine asset type from extension
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    video_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    audio_extensions = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}

    if file_extension.lower() in image_extensions:
        asset_type = "image"
    elif file_extension.lower() in video_extensions:
        asset_type = "video"
    elif file_extension.lower() in audio_extensions:
        asset_type = "audio"
    else:
        asset_type = "other"

    # Get file size
    file_size = file_path.stat().st_size

    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []

    # Create asset record
    new_asset = Asset(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        name=file.filename,
        type=asset_type,
        url=f"/uploads/assets/{unique_filename}",
        file_path=str(file_path),
        size=file_size,
        tags=tag_list,
        asset_metadata={
            "original_filename": file.filename,
            "content_type": file.content_type
        },
        source="upload",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_asset)
    await db.flush()
    await db.refresh(new_asset)

    return new_asset


@router.get("", response_model=AssetListResponse)
async def list_assets(
    workspace_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    sort_by: str = Query("created_at", regex="^(created_at|name|size|updated_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_async_db)
):
    """List assets with filtering, search, and pagination.

    Args:
        workspace_id: Filter by workspace (recommended for multi-tenant isolation)
    """
    query = select(Asset)

    # Filter by workspace (recommended)
    if workspace_id:
        query = query.filter(Asset.workspace_id == workspace_id)

    # Apply filters
    if type:
        query = query.filter(Asset.type == type)

    if search:
        query = query.filter(
            (Asset.name.ilike(f"%{search}%"))
        )

    if tags:
        # Filter by tags (any match)
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.filter(Asset.tags.contains([tag]))

    # Get total count
    count_query = select(func.count()).select_from(Asset)
    if workspace_id:
        count_query = count_query.filter(Asset.workspace_id == workspace_id)
    if type:
        count_query = count_query.filter(Asset.type == type)
    if search:
        count_query = count_query.filter(Asset.name.ilike(f"%{search}%"))
    if tags:
        for tag in tag_list:
            count_query = count_query.filter(Asset.tags.contains([tag]))

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Apply sorting
    sort_column = getattr(Asset, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    assets = list(result.scalars().all())

    return {
        "assets": assets,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific asset by ID."""
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    updates: AssetUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update an asset."""
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update fields if provided
    if updates.name is not None:
        asset.name = updates.name

    if updates.tags is not None:
        asset.tags = updates.tags

    if updates.is_favorite is not None:
        asset.is_favorite = updates.is_favorite

    if updates.asset_metadata is not None:
        # Merge metadata
        asset.asset_metadata = {**(asset.asset_metadata or {}), **updates.asset_metadata}

    asset.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(asset)

    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    delete_file: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete an asset and optionally delete the file."""
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Delete physical file if requested and exists
    if delete_file and asset.file_path:
        file_path = Path(asset.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    await db.delete(asset)
    await db.flush()

    return {"message": "Asset deleted successfully", "id": asset_id}


@router.post("/bulk-delete")
async def bulk_delete_assets(
    asset_ids: List[str],
    delete_files: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """Bulk delete assets."""
    deleted_count = 0
    errors = []

    for asset_id in asset_ids:
        result = await db.execute(select(Asset).filter(Asset.id == asset_id))
        asset = result.scalar_one_or_none()
        if not asset:
            errors.append({"id": asset_id, "error": "Asset not found"})
            continue

        # Delete physical file if requested
        if delete_files and asset.file_path:
            file_path = Path(asset.file_path)
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    errors.append({"id": asset_id, "error": f"Failed to delete file: {str(e)}"})
                    continue

        await db.delete(asset)
        deleted_count += 1

    await db.flush()

    return {
        "deleted_count": deleted_count,
        "errors": errors,
        "total_requested": len(asset_ids)
    }


@router.post("/{asset_id}/toggle-favorite", response_model=AssetResponse)
async def toggle_favorite(
    asset_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Toggle favorite status of an asset (stored in asset_metadata)."""
    result = await db.execute(select(Asset).filter(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Store favorite status in asset_metadata
    metadata = asset.asset_metadata or {}
    metadata['is_favorite'] = not metadata.get('is_favorite', False)
    asset.asset_metadata = metadata
    asset.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(asset)

    return asset


@router.get("/stats/summary")
async def get_assets_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """Get asset statistics summary."""
    result = await db.execute(select(func.count()).select_from(Asset))
    total_assets = result.scalar()
    result = await db.execute(select(func.count()).select_from(Asset).filter(Asset.type == "image"))
    total_images = result.scalar()
    result = await db.execute(select(func.count()).select_from(Asset).filter(Asset.type == "video"))
    total_videos = result.scalar()
    result = await db.execute(select(func.count()).select_from(Asset).filter(Asset.type == "audio"))
    total_audio = result.scalar()

    # Calculate total storage size
    size_result = await db.execute(select(Asset.size))
    total_sizes = size_result.scalars().all()
    total_storage = sum(size for size in total_sizes if size)

    return {
        "total_assets": total_assets,
        "by_type": {
            "image": total_images,
            "video": total_videos,
            "audio": total_audio,
            "other": total_assets - total_images - total_videos - total_audio
        },
        "total_storage_bytes": total_storage,
        "total_storage_mb": round(total_storage / (1024 * 1024), 2)
    }
