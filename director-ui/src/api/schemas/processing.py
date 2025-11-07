"""Processing job schemas for API."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class JobCreate(BaseModel):
    """Schema for creating a processing job."""
    content_id: UUID = Field(..., description="Content UUID to process")
    processing_type: str = Field(..., description="Type: summary, mvp_plan, or content_ideas")
    user_prompt: Optional[str] = Field(None, description="Custom user instructions")
    output_language: str = Field(default="en", description="Output language: en, ru, or es")
    execute_immediately: bool = Field(default=True, description="Execute job immediately")


class JobResponse(BaseModel):
    """Schema for job response."""
    id: UUID
    content_id: Optional[UUID] = None  # Null for bundle jobs
    processing_type: str
    status: str
    result_path: Optional[str]
    user_prompt: Optional[str]
    output_language: str
    error_message: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime
    bundle_id: Optional[UUID] = None  # Set for bundle jobs
    content_ids: Optional[list[UUID]] = None  # Set for bundle jobs

    class Config:
        from_attributes = True


class JobWithResult(JobResponse):
    """Job with result included."""
    result: Optional[str] = Field(None, description="Processing result text")


class JobListResponse(BaseModel):
    """Schema for paginated job list."""
    items: list[JobResponse]
    total: int
    page: int
    page_size: int