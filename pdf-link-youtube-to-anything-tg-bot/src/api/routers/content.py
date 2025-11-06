"""Content management API endpoints."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status

from api.dependencies import get_content_service, get_current_user_id
from api.schemas.content import (
    ContentCreateFromURL,
    ContentResponse,
    ContentWithText,
    ContentListResponse
)
from services.content_service import ContentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/from-url", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_from_url(
    data: ContentCreateFromURL,
    content_service: ContentService = Depends(get_content_service),
    user_id: int = Depends(get_current_user_id)
):
    """Create content from URL (PDF, YouTube, or web page).

    - Calculates content hash from URL
    - Returns existing content if already processed (unless force_reprocess=True)
    - Extracts and stores text if new content
    """
    try:
        content, is_new = await content_service.get_or_create_from_url(
            url=data.url,
            source_type=data.source_type,
            user_id=user_id,
            force_reprocess=data.force_reprocess,
            target_language=data.target_language
        )

        if not is_new:
            logger.info(f"Returned existing content {content['id']} for URL {data.url}")
        else:
            logger.info(f"Created new content {content['id']} from URL {data.url}")

        return content
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating content from URL: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process content")


@router.post("/upload", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def upload_content(
    file: UploadFile = File(...),
    force_reprocess: bool = False,
    content_service: ContentService = Depends(get_content_service),
    user_id: int = Depends(get_current_user_id)
):
    """Upload PDF file for processing.

    - Calculates content hash from file content
    - Returns existing content if already processed (unless force_reprocess=True)
    - Saves file and extracts text if new content
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )

    try:
        content, is_new = await content_service.get_or_create_from_file(
            file=file.file,
            filename=file.filename,
            user_id=user_id,
            force_reprocess=force_reprocess
        )

        if not is_new:
            logger.info(f"Returned existing content {content['id']} for file {file.filename}")
        else:
            logger.info(f"Created new content {content['id']} from file {file.filename}")

        return content
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading content: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process file")


@router.get("", response_model=ContentListResponse)
async def list_content(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    content_service: ContentService = Depends(get_content_service),
    user_id: int = Depends(get_current_user_id)
):
    """List user's content with pagination.

    - Returns paginated list of content items
    - Can filter by source type
    - Ordered by creation date (newest first)
    """
    try:
        offset = (page - 1) * page_size
        items, total = await content_service.get_user_content(
            user_id=user_id,
            limit=page_size,
            offset=offset,
            source_type=source_type
        )

        return ContentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing content: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list content")


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    content_service: ContentService = Depends(get_content_service),
    user_id: int = Depends(get_current_user_id)
):
    """Get content by ID.

    - Returns content metadata and references
    - Does not include extracted text (use /text endpoint)
    """
    try:
        content = await content_service.get_content_by_id(content_id, user_id)
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

        return content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve content")


@router.get("/{content_id}/text", response_model=ContentWithText)
async def get_content_with_text(
    content_id: UUID,
    language: Optional[str] = Query(None, description="Language code (en/ru/es) for specific language version"),
    content_service: ContentService = Depends(get_content_service),
    user_id: int = Depends(get_current_user_id)
):
    """Get content with extracted text included.

    - Returns content metadata with full extracted text
    - Text is read from file storage
    - If language is specified, returns text in that language (if available)
    """
    try:
        content = await content_service.get_content_with_text(content_id, user_id, language=language)
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

        return content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content with text: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve content text")


@router.patch("/{content_id}/language", response_model=ContentResponse)
async def update_content_language(
    content_id: UUID,
    language: str = Query(..., description="Language code (en/ru/es)"),
    content_service: ContentService = Depends(get_content_service),
    user_id: int = Depends(get_current_user_id)
):
    """Update detected language for content.

    - Updates only the detected_language field
    - Does not modify file references or extracted text
    - Useful for correcting incorrect language detection
    """
    try:
        success = await content_service.update_detected_language(content_id, language, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

        # Return updated content
        content = await content_service.get_content_by_id(content_id, user_id)
        logger.info(f"Updated language to {language} for content {content_id}")
        return content
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content language: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update language")


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: UUID,
    content_service: ContentService = Depends(get_content_service),
    user_id: int = Depends(get_current_user_id)
):
    """Delete content and associated files.

    - Deletes content record from database
    - Deletes associated files (extracted text, uploaded file)
    - Cascades to delete associated processing jobs
    """
    try:
        success = await content_service.delete_content(content_id, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")

        logger.info(f"Deleted content {content_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete content")