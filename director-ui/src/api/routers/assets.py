"""Asset API router for media file tracking and management."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import shutil
from pathlib import Path

from data.models import Asset
from data.dao import get_db

router = APIRouter()


class AssetCreate(BaseModel):
    """Asset creation schema."""
    name: str
    type: str  # image, video, audio
    url: str
    file_path: Optional[str] = None
    size: Optional[int] = None
    duration: Optional[float] = None
    thumbnail_url: Optional[str] = None
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = {}
    is_favorite: bool = False


class AssetUpdate(BaseModel):
    """Asset update schema."""
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class AssetResponse(BaseModel):
    """Asset response schema."""
    id: str
    name: str
    type: str
    url: str
    file_path: Optional[str]
    size: Optional[int]
    duration: Optional[float]
    thumbnail_url: Optional[str]
    tags: List[str]
    metadata: Dict[str, Any]
    is_favorite: bool
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


@router.post("/assets", response_model=AssetResponse)
async def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db)
):
    """Create a new asset record."""
    new_asset = Asset(
        id=str(uuid.uuid4()),
        name=asset.name,
        type=asset.type,
        url=asset.url,
        file_path=asset.file_path,
        size=asset.size,
        duration=asset.duration,
        thumbnail_url=asset.thumbnail_url,
        tags=asset.tags,
        metadata=asset.metadata or {},
        is_favorite=asset.is_favorite,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return new_asset


@router.post("/assets/upload", response_model=AssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    tags: Optional[str] = Query(None),  # Comma-separated tags
    is_favorite: bool = False,
    db: Session = Depends(get_db)
):
    """Upload a new asset file."""
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
        name=file.filename,
        type=asset_type,
        url=f"/uploads/assets/{unique_filename}",
        file_path=str(file_path),
        size=file_size,
        tags=tag_list,
        metadata={
            "original_filename": file.filename,
            "content_type": file.content_type
        },
        is_favorite=is_favorite,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return new_asset


@router.get("/assets", response_model=AssetListResponse)
async def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    favorite_only: bool = False,
    sort_by: str = Query("created_at", regex="^(created_at|name|size|updated_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """List assets with filtering, search, and pagination."""
    query = db.query(Asset)

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

    if favorite_only:
        query = query.filter(Asset.is_favorite == True)

    # Get total count
    total = query.count()

    # Apply sorting
    sort_column = getattr(Asset, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    offset = (page - 1) * page_size
    assets = query.offset(offset).limit(page_size).all()

    return {
        "assets": assets,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific asset by ID."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.put("/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    updates: AssetUpdate,
    db: Session = Depends(get_db)
):
    """Update an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update fields if provided
    if updates.name is not None:
        asset.name = updates.name

    if updates.tags is not None:
        asset.tags = updates.tags

    if updates.is_favorite is not None:
        asset.is_favorite = updates.is_favorite

    if updates.metadata is not None:
        # Merge metadata
        asset.metadata = {**asset.metadata, **updates.metadata}

    asset.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(asset)

    return asset


@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    delete_file: bool = False,
    db: Session = Depends(get_db)
):
    """Delete an asset and optionally delete the file."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
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

    db.delete(asset)
    db.commit()

    return {"message": "Asset deleted successfully", "id": asset_id}


@router.post("/assets/bulk-delete")
async def bulk_delete_assets(
    asset_ids: List[str],
    delete_files: bool = False,
    db: Session = Depends(get_db)
):
    """Bulk delete assets."""
    deleted_count = 0
    errors = []

    for asset_id in asset_ids:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
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

        db.delete(asset)
        deleted_count += 1

    db.commit()

    return {
        "deleted_count": deleted_count,
        "errors": errors,
        "total_requested": len(asset_ids)
    }


@router.post("/assets/{asset_id}/toggle-favorite", response_model=AssetResponse)
async def toggle_favorite(
    asset_id: str,
    db: Session = Depends(get_db)
):
    """Toggle favorite status of an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset.is_favorite = not asset.is_favorite
    asset.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(asset)

    return asset


@router.get("/assets/stats/summary")
async def get_assets_stats(
    db: Session = Depends(get_db)
):
    """Get asset statistics summary."""
    total_assets = db.query(Asset).count()
    total_images = db.query(Asset).filter(Asset.type == "image").count()
    total_videos = db.query(Asset).filter(Asset.type == "video").count()
    total_audio = db.query(Asset).filter(Asset.type == "audio").count()
    total_favorites = db.query(Asset).filter(Asset.is_favorite == True).count()

    # Calculate total storage size
    total_size = db.query(Asset).with_entities(Asset.size).all()
    total_storage = sum(size[0] for size in total_size if size[0])

    return {
        "total_assets": total_assets,
        "by_type": {
            "image": total_images,
            "video": total_videos,
            "audio": total_audio,
            "other": total_assets - total_images - total_videos - total_audio
        },
        "total_favorites": total_favorites,
        "total_storage_bytes": total_storage,
        "total_storage_mb": round(total_storage / (1024 * 1024), 2)
    }
