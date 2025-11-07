"""Content schemas for API."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class ContentCreateFromURL(BaseModel):
    """Schema for creating content from URL."""
    url: str = Field(..., description="Source URL (PDF, YouTube, or web page)")
    source_type: str = Field(..., description="Content type: pdf_url, youtube, or web")
    force_reprocess: bool = Field(default=False, description="Force reprocessing if content exists")
    target_language: Optional[str] = Field(None, description="Target language for extraction (en/ru/es)")


class ContentResponse(BaseModel):
    """Schema for content response."""
    id: UUID
    content_hash: str
    source_type: str
    source_url: Optional[str]
    file_reference: Optional[str]
    extracted_text_path: str
    extracted_text_paths: Optional[Dict[str, str]] = Field(None, description="Paths to extracted text by language")
    metadata: Dict[str, Any]
    user_id: int
    processing_status: str
    error_message: Optional[str]
    detected_language: Optional[str] = Field(None, description="Detected content language (en/ru/es)")
    tags: list[str] = Field(default_factory=list, description="Content tags")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentWithText(ContentResponse):
    """Content with extracted text included."""
    extracted_text: str


class ContentListResponse(BaseModel):
    """Schema for paginated content list."""
    items: list[ContentResponse]
    total: int
    page: int
    page_size: int