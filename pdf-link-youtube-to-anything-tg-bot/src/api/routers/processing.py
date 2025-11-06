"""Processing job API endpoints."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_processing_service, get_current_user_id
from api.schemas.processing import (
    JobCreate,
    JobResponse,
    JobWithResult,
    JobListResponse
)
from services.processing_service import ProcessingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/processing", tags=["processing"])


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    processing_service: ProcessingService = Depends(get_processing_service),
    user_id: int = Depends(get_current_user_id)
):
    """Create a processing job.

    - Creates AI processing job for content (summary, MVP plan, or content ideas)
    - Can execute immediately or queue for later
    - Supports custom user prompts and output language selection
    """
    try:
        job = await processing_service.create_job(
            content_id=data.content_id,
            processing_type=data.processing_type,
            user_id=user_id,
            user_prompt=data.user_prompt,
            output_language=data.output_language,
            execute_immediately=data.execute_immediately
        )

        logger.info(f"Created job {job['id']} for content {data.content_id}")
        return job
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating job: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create job")


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    processing_service: ProcessingService = Depends(get_processing_service),
    user_id: int = Depends(get_current_user_id)
):
    """Get job status and metadata.

    - Returns job information without result content
    - Use /jobs/{job_id}/result to get the actual AI output
    """
    try:
        job = await processing_service._get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        # Verify ownership
        if job['user_id'] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve job")


@router.get("/jobs/{job_id}/result", response_model=JobWithResult)
async def get_job_with_result(
    job_id: UUID,
    processing_service: ProcessingService = Depends(get_processing_service),
    user_id: int = Depends(get_current_user_id)
):
    """Get job with result included.

    - Returns job metadata with full AI processing result
    - Result is read from file storage
    - Returns null for result if job not completed
    """
    try:
        job = await processing_service._get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        # Verify ownership
        if job['user_id'] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Get result if available
        result = None
        if job['result_path']:
            result = await processing_service.get_job_result(job_id)

        job['result'] = result
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job result: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve job result")


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    content_id: Optional[UUID] = Query(None, description="Filter by content ID"),
    processing_service: ProcessingService = Depends(get_processing_service),
    user_id: int = Depends(get_current_user_id)
):
    """List user's processing jobs with pagination.

    - Returns paginated list of jobs
    - Can filter by status (pending, processing, completed, failed)
    - Can filter by content_id to see all jobs for specific content
    - Ordered by creation date (newest first)
    """
    try:
        offset = (page - 1) * page_size
        items, total = await processing_service.get_user_jobs(
            user_id=user_id,
            limit=page_size,
            offset=offset,
            status=status,
            content_id=content_id
        )

        return JobListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing jobs: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list jobs")


@router.post("/jobs/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: UUID,
    processing_service: ProcessingService = Depends(get_processing_service),
    user_id: int = Depends(get_current_user_id)
):
    """Retry a failed or completed job.

    - Re-executes AI processing for the job
    - Useful for failed jobs or to regenerate results
    - Updates job status and result
    """
    try:
        job = await processing_service._get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        # Verify ownership
        if job['user_id'] != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Retry job
        await processing_service.retry_job(job_id)
        job = await processing_service._get_job_by_id(job_id)

        logger.info(f"Retried job {job_id}")
        return job
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrying job: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retry job")