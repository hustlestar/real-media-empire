"""Workspace and Project management API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from data.models import Workspace, Project
from data.async_dao import get_async_db

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class WorkspaceCreate(BaseModel):
    """Workspace creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    owner_id: int = Field(...)
    storage_quota_gb: int = Field(100, ge=1)
    monthly_budget_usd: float = Field(1000.0, ge=0)
    settings: Optional[Dict[str, Any]] = {}


class WorkspaceUpdate(BaseModel):
    """Workspace update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    storage_quota_gb: Optional[int] = Field(None, ge=1)
    monthly_budget_usd: Optional[float] = Field(None, ge=0)
    settings: Optional[Dict[str, Any]] = None


class WorkspaceResponse(BaseModel):
    """Workspace response schema."""
    id: str
    name: str
    slug: str
    owner_id: int
    storage_quota_gb: int
    monthly_budget_usd: float
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    """Project creation schema."""
    workspace_id: str
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    type: str = Field("campaign", pattern=r"^(campaign|brand|series|folder)$")
    parent_project_id: Optional[str] = None
    description: Optional[str] = None
    project_metadata: Optional[Dict[str, Any]] = {}


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern=r"^(active|archived|deleted)$")
    description: Optional[str] = None
    project_metadata: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    """Project response schema."""
    id: str
    workspace_id: str
    name: str
    slug: str
    type: str
    parent_project_id: Optional[str]
    status: str
    description: Optional[str]
    project_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Workspace Endpoints
# ============================================================================

@router.post("/workspaces", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    workspace: WorkspaceCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new workspace."""
    # Check if slug already exists
    result = await db.execute(select(Workspace).filter(Workspace.slug == workspace.slug))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail=f"Workspace with slug '{workspace.slug}' already exists")

    new_workspace = Workspace(
        id=str(uuid.uuid4()),
        name=workspace.name,
        slug=workspace.slug,
        owner_id=workspace.owner_id,
        storage_quota_gb=workspace.storage_quota_gb,
        monthly_budget_usd=workspace.monthly_budget_usd,
        settings=workspace.settings or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_workspace)
    await db.flush()
    await db.refresh(new_workspace)

    return new_workspace


@router.get("/workspaces", response_model=Dict[str, List[WorkspaceResponse]])
async def list_workspaces(
    owner_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """List all workspaces, optionally filtered by owner."""
    query = select(Workspace)

    if owner_id is not None:
        query = query.filter(Workspace.owner_id == owner_id)

    query = query.order_by(Workspace.created_at.desc())
    result = await db.execute(query)
    workspaces = result.scalars().all()

    return {"workspaces": list(workspaces)}


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific workspace by ID."""
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.put("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    updates: WorkspaceUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a workspace."""
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Update fields if provided
    if updates.name is not None:
        workspace.name = updates.name

    if updates.storage_quota_gb is not None:
        workspace.storage_quota_gb = updates.storage_quota_gb

    if updates.monthly_budget_usd is not None:
        workspace.monthly_budget_usd = updates.monthly_budget_usd

    if updates.settings is not None:
        # Merge settings
        workspace.settings = {**workspace.settings, **updates.settings}

    workspace.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(workspace)

    return workspace


@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a workspace and all associated content (CASCADE)."""
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    await db.delete(workspace)

    return {"message": "Workspace deleted successfully", "id": workspace_id}


# ============================================================================
# Project Endpoints
# ============================================================================

@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new project within a workspace."""
    # Verify workspace exists
    result = await db.execute(select(Workspace).filter(Workspace.id == project.workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{project.workspace_id}' not found")

    # Check if slug already exists in this workspace
    result = await db.execute(
        select(Project).filter(
            Project.workspace_id == project.workspace_id,
            Project.slug == project.slug
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Project with slug '{project.slug}' already exists in this workspace"
        )

    # Verify parent project exists if specified
    if project.parent_project_id:
        result = await db.execute(select(Project).filter(Project.id == project.parent_project_id))
        parent = result.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=404, detail=f"Parent project '{project.parent_project_id}' not found")
        if parent.workspace_id != project.workspace_id:
            raise HTTPException(status_code=400, detail="Parent project must be in the same workspace")

    new_project = Project(
        id=str(uuid.uuid4()),
        workspace_id=project.workspace_id,
        name=project.name,
        slug=project.slug,
        type=project.type,
        parent_project_id=project.parent_project_id,
        status="active",
        description=project.description,
        project_metadata=project.project_metadata or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_project)
    await db.flush()
    await db.refresh(new_project)

    return new_project


@router.get("/projects", response_model=Dict[str, List[ProjectResponse]])
async def list_projects(
    workspace_id: Optional[str] = None,
    project_type: Optional[str] = None,
    parent_project_id: Optional[str] = None,
    status: str = Query("active", pattern=r"^(active|archived|deleted)$"),
    db: AsyncSession = Depends(get_async_db)
):
    """List all projects with optional filtering."""
    query = select(Project)

    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)

    if project_type:
        query = query.filter(Project.type == project_type)

    if parent_project_id:
        query = query.filter(Project.parent_project_id == parent_project_id)

    query = query.filter(Project.status == status)
    query = query.order_by(Project.created_at.desc())

    result = await db.execute(query)
    projects = result.scalars().all()

    return {"projects": list(projects)}


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific project by ID."""
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update a project."""
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields if provided
    if updates.name is not None:
        project.name = updates.name

    if updates.status is not None:
        project.status = updates.status

    if updates.description is not None:
        project.description = updates.description

    if updates.project_metadata is not None:
        # Merge metadata
        project.project_metadata = {**(project.project_metadata or {}), **updates.project_metadata}

    project.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(project)

    return project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a project and all associated content (CASCADE)."""
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    await db.delete(project)

    return {"message": "Project deleted successfully", "id": project_id}


# ============================================================================
# Workspace Statistics
# ============================================================================

@router.get("/workspaces/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get statistics for a workspace."""
    result = await db.execute(select(Workspace).filter(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Import here to avoid circular imports
    from data.models import FilmProject, Character, Asset

    # Count resources
    total_projects_result = await db.execute(
        select(func.count()).select_from(Project).filter(Project.workspace_id == workspace_id)
    )
    total_projects = total_projects_result.scalar()

    total_films_result = await db.execute(
        select(func.count()).select_from(FilmProject).filter(FilmProject.workspace_id == workspace_id)
    )
    total_films = total_films_result.scalar()

    total_characters_result = await db.execute(
        select(func.count()).select_from(Character).filter(Character.workspace_id == workspace_id)
    )
    total_characters = total_characters_result.scalar()

    total_assets_result = await db.execute(
        select(func.count()).select_from(Asset).filter(Asset.workspace_id == workspace_id)
    )
    total_assets = total_assets_result.scalar()

    # Calculate storage usage
    storage_result = await db.execute(select(Asset).filter(Asset.workspace_id == workspace_id))
    storage_assets = storage_result.scalars().all()
    storage_bytes = sum(asset.size or 0 for asset in storage_assets)
    storage_gb = storage_bytes / (1024 ** 3)

    # Calculate costs
    cost_result = await db.execute(select(FilmProject).filter(FilmProject.workspace_id == workspace_id))
    films = cost_result.scalars().all()
    total_cost = sum(film.total_cost or 0 for film in films)

    return {
        "workspace_id": workspace_id,
        "workspace_name": workspace.name,
        "totals": {
            "projects": total_projects,
            "films": total_films,
            "characters": total_characters,
            "assets": total_assets
        },
        "storage": {
            "used_gb": round(storage_gb, 2),
            "quota_gb": workspace.storage_quota_gb,
            "percent_used": round((storage_gb / workspace.storage_quota_gb) * 100, 1) if workspace.storage_quota_gb > 0 else 0
        },
        "costs": {
            "total_spent_usd": round(total_cost, 2),
            "monthly_budget_usd": workspace.monthly_budget_usd,
            "percent_used": round((total_cost / workspace.monthly_budget_usd) * 100, 1) if workspace.monthly_budget_usd > 0 else 0
        }
    }
