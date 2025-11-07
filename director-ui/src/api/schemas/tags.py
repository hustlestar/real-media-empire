"""API schemas for tags."""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class TagResponse(BaseModel):
    """Tag response schema."""

    id: UUID = Field(..., description="Tag ID")
    name: str = Field(..., description="Tag name")
    created_at: datetime = Field(..., description="Creation timestamp")
    usage_count: int = Field(..., description="Number of content items with this tag")

    class Config:
        from_attributes = True


class TagsListResponse(BaseModel):
    """Response for tags list."""

    tags: list[TagResponse] = Field(..., description="List of tags")
    total: int = Field(..., description="Total number of tags")
