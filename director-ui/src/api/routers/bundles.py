"""Bundle API endpoints."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_bundle_service, get_processing_service, get_current_user_id
from api.schemas.bundle import (
    BundleCreate,
    BundleUpdate,
    BundleResponse,
    BundleDetailResponse,
    BundleListResponse,
    BundleProcessConfig,
    BundleAttemptResponse,
    BundleAttemptDiff
)
from services.bundle_service import BundleService
from services.processing_service import ProcessingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bundles", tags=["bundles"])


@router.post("", response_model=BundleResponse, status_code=status.HTTP_201_CREATED)
async def create_bundle(
    data: BundleCreate,
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """Create a new bundle.

    - Bundles can contain one or more content items
    - Optional name for easy identification
    - Content IDs must exist and belong to the user
    """
    try:
        bundle = await bundle_service.create_bundle(
            user_id=user_id,
            content_ids=data.content_ids,
            name=data.name
        )
        logger.info(f"Created bundle {bundle['id']} for user {user_id}")
        return bundle
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating bundle: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create bundle")


@router.get("", response_model=BundleListResponse)
async def list_bundles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """List user's bundles with pagination.

    - Returns all bundles created by the user
    - Ordered by creation date (newest first)
    - Includes bundle metadata but not content details
    """
    try:
        offset = (page - 1) * page_size
        bundles, total = await bundle_service.get_user_bundles(
            user_id=user_id,
            limit=page_size,
            offset=offset
        )

        return BundleListResponse(
            items=bundles,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing bundles: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list bundles")


@router.get("/{bundle_id}", response_model=BundleDetailResponse)
async def get_bundle(
    bundle_id: UUID,
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """Get bundle details with content items and attempt count.

    - Returns bundle with full content item details
    - Includes count of processing attempts
    - Only accessible by bundle owner
    """
    try:
        bundle = await bundle_service.get_bundle_with_details(bundle_id, user_id)
        if not bundle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found")

        return bundle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bundle: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve bundle")


@router.put("/{bundle_id}", response_model=BundleResponse)
async def update_bundle(
    bundle_id: UUID,
    data: BundleUpdate,
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """Update bundle name or content items.

    - Can update bundle name
    - Can update the list of content items
    - Only accessible by bundle owner
    """
    try:
        success = await bundle_service.update_bundle(
            bundle_id=bundle_id,
            user_id=user_id,
            name=data.name,
            content_ids=data.content_ids
        )

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found")

        bundle = await bundle_service.get_bundle_by_id(bundle_id, user_id)
        logger.info(f"Updated bundle {bundle_id}")
        return bundle
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating bundle: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update bundle")


@router.delete("/{bundle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bundle(
    bundle_id: UUID,
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """Delete bundle and associated attempts.

    - Deletes bundle record
    - Cascades to delete all processing attempts
    - Does not delete the content items themselves
    - Only accessible by bundle owner
    """
    try:
        success = await bundle_service.delete_bundle(bundle_id, user_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found")

        logger.info(f"Deleted bundle {bundle_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bundle: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete bundle")


@router.post("/{bundle_id}/process", response_model=BundleAttemptResponse, status_code=status.HTTP_201_CREATED)
async def process_bundle(
    bundle_id: UUID,
    config: BundleProcessConfig,
    bundle_service: BundleService = Depends(get_bundle_service),
    processing_service: ProcessingService = Depends(get_processing_service),
    user_id: int = Depends(get_current_user_id)
):
    """Process bundle with AI - creates a new attempt.

    - Creates a bundle processing attempt with full prompt storage
    - Creates and executes a processing job
    - Stores all configuration for reproducibility
    - Returns the attempt record (job runs in background)
    """
    try:
        # Verify bundle exists and belongs to user
        bundle = await bundle_service.get_bundle_by_id(bundle_id, user_id)
        if not bundle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found")

        # Create processing job for the bundle
        job = await processing_service.create_bundle_job(
            bundle_id=bundle_id,
            content_ids=bundle['content_ids'],
            processing_type=config.processing_type,
            user_id=user_id,
            user_prompt=config.custom_instructions,
            output_language=config.output_language,
            execute_immediately=True
        )

        # Create bundle attempt record
        attempt = await bundle_service.create_bundle_attempt(
            bundle_id=bundle_id,
            processing_type=config.processing_type,
            output_language=config.output_language,
            system_prompt=config.system_prompt,
            user_prompt=config.user_prompt,
            combined_content_preview=config.combined_content_preview,
            custom_instructions=config.custom_instructions,
            job_id=job['id']
        )

        logger.info(f"Created bundle attempt {attempt['id']} for bundle {bundle_id}")
        return attempt
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing bundle: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process bundle")


@router.get("/{bundle_id}/attempts", response_model=list[BundleAttemptResponse])
async def get_bundle_attempts(
    bundle_id: UUID,
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """Get all processing attempts for a bundle.

    - Returns attempt history in chronological order
    - Includes all configuration and prompts used
    - Links to associated processing jobs
    - Only accessible by bundle owner
    """
    try:
        attempts = await bundle_service.get_bundle_attempts(bundle_id, user_id)
        return attempts
    except Exception as e:
        logger.error(f"Error getting bundle attempts: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve attempts")


@router.get("/attempts/{attempt_id}", response_model=BundleAttemptResponse)
async def get_bundle_attempt(
    attempt_id: UUID,
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific bundle attempt by ID.

    - Returns full attempt details including prompts
    - Only accessible by bundle owner
    """
    try:
        attempt = await bundle_service.get_bundle_attempt_by_id(attempt_id, user_id)
        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")

        return attempt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bundle attempt: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve attempt")


@router.get("/attempts/{attempt_id_1}/diff/{attempt_id_2}", response_model=BundleAttemptDiff)
async def get_bundle_attempt_diff(
    attempt_id_1: UUID,
    attempt_id_2: UUID,
    bundle_service: BundleService = Depends(get_bundle_service),
    user_id: int = Depends(get_current_user_id)
):
    """Compare two bundle attempts.

    - Shows differences in configuration between attempts
    - Useful for understanding what changed between runs
    - Both attempts must belong to the same bundle
    - Only accessible by bundle owner
    """
    try:
        diff = await bundle_service.get_bundle_attempt_diff(attempt_id_1, attempt_id_2, user_id)
        if not diff:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attempts not found or belong to different bundles"
            )

        return diff
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bundle attempt diff: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve diff")
