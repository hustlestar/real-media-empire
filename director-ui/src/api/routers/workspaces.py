"""Workspace and Project management API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from data.models import Workspace, Project
from data.dao import get_db

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class WorkspaceCreate(BaseModel):
    """Workspace creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, regex=r"^[a-z0-9-]+$")
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
    slug: str = Field(..., min_length=1, max_length=100, regex=r"^[a-z0-9-]+$")
    type: str = Field("campaign", regex=r"^(campaign|brand|series|folder)$")
    parent_project_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, regex=r"^(active|archived|deleted)$")
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


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
    metadata: Dict[str, Any]
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
    db: Session = Depends(get_db)
):
    """Create a new workspace."""
    # Check if slug already exists
    existing = db.query(Workspace).filter(Workspace.slug == workspace.slug).first()
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
    db.commit()
    db.refresh(new_workspace)

    return new_workspace


@router.get("/workspaces", response_model=Dict[str, List[WorkspaceResponse]])
async def list_workspaces(
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all workspaces, optionally filtered by owner."""
    query = db.query(Workspace)

    if owner_id is not None:
        query = query.filter(Workspace.owner_id == owner_id)

    workspaces = query.order_by(Workspace.created_at.desc()).all()

    return {"workspaces": workspaces}


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific workspace by ID."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return workspace


@router.put("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    updates: WorkspaceUpdate,
    db: Session = Depends(get_db)
):
    """Update a workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
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

    db.commit()
    db.refresh(workspace)

    return workspace


@router.delete("/workspaces/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Delete a workspace and all associated content (CASCADE)."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    db.delete(workspace)
    db.commit()

    return {"message": "Workspace deleted successfully", "id": workspace_id}


# ============================================================================
# Project Endpoints
# ============================================================================

@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project within a workspace."""
    # Verify workspace exists
    workspace = db.query(Workspace).filter(Workspace.id == project.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail=f"Workspace '{project.workspace_id}' not found")

    # Check if slug already exists in this workspace
    existing = db.query(Project).filter(
        Project.workspace_id == project.workspace_id,
        Project.slug == project.slug
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Project with slug '{project.slug}' already exists in this workspace"
        )

    # Verify parent project exists if specified
    if project.parent_project_id:
        parent = db.query(Project).filter(Project.id == project.parent_project_id).first()
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
        metadata=project.metadata or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@router.get("/projects", response_model=Dict[str, List[ProjectResponse]])
async def list_projects(
    workspace_id: Optional[str] = None,
    project_type: Optional[str] = None,
    parent_project_id: Optional[str] = None,
    status: str = Query("active", regex=r"^(active|archived|deleted)$"),
    db: Session = Depends(get_db)
):
    """List all projects with optional filtering."""
    query = db.query(Project)

    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)

    if project_type:
        query = query.filter(Project.type == project_type)

    if parent_project_id:
        query = query.filter(Project.parent_project_id == parent_project_id)

    query = query.filter(Project.status == status)

    projects = query.order_by(Project.created_at.desc()).all()

    return {"projects": projects}


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields if provided
    if updates.name is not None:
        project.name = updates.name

    if updates.status is not None:
        project.status = updates.status

    if updates.description is not None:
        project.description = updates.description

    if updates.metadata is not None:
        # Merge metadata
        project.metadata = {**project.metadata, **updates.metadata}

    project.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(project)

    return project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Delete a project and all associated content (CASCADE)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully", "id": project_id}


# ============================================================================
# Workspace Statistics
# ============================================================================

@router.get("/workspaces/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get statistics for a workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Import here to avoid circular imports
    from data.models import FilmProject, Character, Asset

    # Count resources
    total_projects = db.query(Project).filter(Project.workspace_id == workspace_id).count()
    total_films = db.query(FilmProject).filter(FilmProject.workspace_id == workspace_id).count()
    total_characters = db.query(Character).filter(Character.workspace_id == workspace_id).count()
    total_assets = db.query(Asset).filter(Asset.workspace_id == workspace_id).count()

    # Calculate storage usage
    storage_query = db.query(Asset).filter(Asset.workspace_id == workspace_id).all()
    storage_bytes = sum(asset.size or 0 for asset in storage_query)
    storage_gb = storage_bytes / (1024 ** 3)

    # Calculate costs
    cost_query = db.query(FilmProject).filter(FilmProject.workspace_id == workspace_id).all()
    total_cost = sum(film.total_cost or 0 for film in cost_query)

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
