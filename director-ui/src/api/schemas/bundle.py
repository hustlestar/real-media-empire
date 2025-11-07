"""Bundle schemas for API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class BundleCreate(BaseModel):
    """Schema for creating a bundle."""
    name: Optional[str] = Field(None, description="Optional bundle name")
    content_ids: List[UUID] = Field(..., description="List of content UUIDs to include in bundle")


class BundleUpdate(BaseModel):
    """Schema for updating a bundle."""
    name: Optional[str] = Field(None, description="Optional bundle name")
    content_ids: Optional[List[UUID]] = Field(None, description="List of content UUIDs")


class ContentItemSummary(BaseModel):
    """Summary of a content item for bundle responses."""
    id: UUID
    source_type: str
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class BundleResponse(BaseModel):
    """Schema for bundle response."""
    id: UUID
    user_id: int
    name: Optional[str]
    content_ids: List[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BundleDetailResponse(BundleResponse):
    """Bundle response with additional details."""
    attempt_count: int = Field(0, description="Number of processing attempts")
    content_items: List[ContentItemSummary] = Field(default_factory=list, description="Content item details")


class BundleListResponse(BaseModel):
    """Schema for paginated bundle list."""
    items: List[BundleResponse]
    total: int
    page: int
    page_size: int


class BundleProcessConfig(BaseModel):
    """Configuration for processing a bundle."""
    processing_type: str = Field(..., description="Type: summary, mvp_plan, or content_ideas")
    output_language: str = Field(default="en", description="Output language: en, ru, or es")
    custom_instructions: Optional[str] = Field(None, description="Custom user instructions")
    system_prompt: str = Field(..., description="Full system prompt to use")
    user_prompt: Optional[str] = Field(None, description="User prompt template")
    combined_content_preview: Optional[str] = Field(None, description="Preview of combined content")


class BundleAttemptResponse(BaseModel):
    """Schema for bundle attempt response."""
    id: UUID
    bundle_id: UUID
    attempt_number: int
    processing_type: str
    output_language: str
    system_prompt: str
    user_prompt: Optional[str]
    combined_content_preview: Optional[str]
    custom_instructions: Optional[str]
    result_path: Optional[str]
    job_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


class BundleAttemptWithResult(BundleAttemptResponse):
    """Bundle attempt with result included."""
    result: Optional[str] = Field(None, description="Processing result text")


class BundleAttemptComparison(BaseModel):
    """Comparison details for an attempt in diff."""
    id: str
    attempt_number: int
    processing_type: str
    output_language: str
    custom_instructions: Optional[str]
    created_at: str


class BundleAttemptChanges(BaseModel):
    """Changes between two attempts."""
    processing_type_changed: bool
    language_changed: bool
    custom_instructions_changed: bool
    system_prompt_changed: bool


class BundleAttemptDiff(BaseModel):
    """Schema for bundle attempt diff response."""
    attempt_1: BundleAttemptComparison
    attempt_2: BundleAttemptComparison
    changes: BundleAttemptChanges
