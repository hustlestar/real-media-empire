"""Processing service for AI job management."""

import logging
from typing import Optional, Dict, Any, Tuple, List
from uuid import UUID
from datetime import datetime

from models.content import JobProcessingType, JobStatus
from services.file_storage import FileStorageService
from processors.ai_processor import AIProcessor

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for managing AI processing jobs."""

    def __init__(self, database, file_storage: FileStorageService, ai_processor: AIProcessor):
        """Initialize processing service.

        Args:
            database: DatabaseManager instance
            file_storage: FileStorageService instance
            ai_processor: AIProcessor instance
        """
        self.db = database
        self.file_storage = file_storage
        self.ai_processor = ai_processor

    async def create_job(
        self,
        content_id: UUID,
        processing_type: str,
        user_id: int,
        user_prompt: Optional[str] = None,
        output_language: str = "en",
        execute_immediately: bool = True
    ) -> Dict[str, Any]:
        """Create a processing job.

        Args:
            content_id: Content UUID
            processing_type: Type of processing (summary, mvp_plan, content_ideas)
            user_id: User ID
            user_prompt: Optional custom user instructions
            output_language: Output language
            execute_immediately: Execute job immediately

        Returns:
            Job dict
        """
        # Create job in database
        job_id = await self._create_job_record(
            content_id=content_id,
            processing_type=processing_type,
            user_id=user_id,
            user_prompt=user_prompt,
            output_language=output_language,
            status=JobStatus.PROCESSING.value if execute_immediately else JobStatus.PENDING.value
        )

        job = await self._get_job_by_id(job_id)

        # Execute if requested
        if execute_immediately:
            try:
                await self.execute_job(job_id)
                job = await self._get_job_by_id(job_id)
            except Exception as e:
                logger.error(f"Error executing job {job_id}: {e}")
                await self._update_job_status(
                    job_id,
                    JobStatus.FAILED.value,
                    error_message=str(e)
                )
                job = await self._get_job_by_id(job_id)

        return job

    async def create_bundle_job(
        self,
        bundle_id: UUID,
        content_ids: List[UUID],
        processing_type: str,
        user_id: int,
        user_prompt: Optional[str] = None,
        output_language: str = "en",
        execute_immediately: bool = True
    ) -> Dict[str, Any]:
        """Create a processing job for a bundle with multiple content items.

        Args:
            bundle_id: Bundle UUID
            content_ids: List of content UUIDs to process together
            processing_type: Type of processing (summary, mvp_plan, content_ideas)
            user_id: User ID
            user_prompt: Optional custom user instructions
            output_language: Output language
            execute_immediately: Execute job immediately

        Returns:
            Job dict
        """
        # Create job in database with bundle_id and content_ids
        job_id = await self._create_bundle_job_record(
            bundle_id=bundle_id,
            content_ids=content_ids,
            processing_type=processing_type,
            user_id=user_id,
            user_prompt=user_prompt,
            output_language=output_language,
            status=JobStatus.PROCESSING.value if execute_immediately else JobStatus.PENDING.value
        )

        job = await self._get_job_by_id(job_id)

        # Execute if requested
        if execute_immediately:
            try:
                await self.execute_bundle_job(job_id)
                job = await self._get_job_by_id(job_id)
            except Exception as e:
                logger.error(f"Error executing bundle job {job_id}: {e}")
                await self._update_job_status(
                    job_id,
                    JobStatus.FAILED.value,
                    error_message=str(e)
                )
                job = await self._get_job_by_id(job_id)

        return job

    async def execute_bundle_job(self, job_id: UUID) -> str:
        """Execute a bundle processing job with multiple content items.

        Args:
            job_id: Job UUID

        Returns:
            Processing result

        Raises:
            ValueError: If job not found or content not found
            Exception: If processing fails
        """
        job = await self._get_job_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        if not job.get('content_ids'):
            raise ValueError(f"Bundle job {job_id} has no content_ids")

        # Update status to processing
        await self._update_job_status(job_id, JobStatus.PROCESSING.value)

        try:
            # Fetch and combine content from all items
            combined_content = []

            for idx, content_id in enumerate(job['content_ids'], 1):
                # Ensure content_id is a UUID object
                if isinstance(content_id, str):
                    content_id = UUID(content_id)

                content = await self._get_content(content_id)
                if not content:
                    logger.warning(f"Content {content_id} not found, skipping")
                    continue

                # Ensure metadata is a dict (handle JSONB from PostgreSQL)
                if isinstance(content.get('metadata'), str):
                    import json
                    content['metadata'] = json.loads(content['metadata'])

                # Read extracted text
                text = await self.file_storage.read_extracted_text(content['extracted_text_path'])
                if not text:
                    logger.warning(f"Could not read text for content {content_id}, skipping")
                    continue

                # Add content with metadata
                metadata = content.get('metadata', {})
                title = metadata.get('title', f'Content {idx}')
                source_type = content['source_type']

                combined_content.append(f"=== {title} ===")
                combined_content.append(f"Source type: {source_type}")
                if metadata.get('url'):
                    combined_content.append(f"URL: {metadata['url']}")
                combined_content.append("")
                combined_content.append(text)
                combined_content.append("\n" + "="*80 + "\n")

            if not combined_content:
                raise ValueError("No valid content found in bundle")

            combined_text = "\n".join(combined_content)

            # Process with AI using combined content
            result = await self._process_content(
                content=combined_text,
                processing_type=job['processing_type'],
                source_type='bundle',  # Special source type for bundles
                user_id=job['user_id'],
                user_prompt=job['user_prompt'],
                language=job['output_language']
            )

            if not result:
                raise Exception("AI processing returned empty result")

            # Save result to file
            result_path = await self.file_storage.save_processing_result(job_id, result)

            # Update job status
            await self._update_job_result(
                job_id,
                JobStatus.COMPLETED.value,
                result_path=result_path
            )

            logger.info(f"Completed bundle job {job_id} with {len(job['content_ids'])} content items")
            return result

        except Exception as e:
            logger.error(f"Bundle job {job_id} failed: {e}")
            await self._update_job_status(
                job_id,
                JobStatus.FAILED.value,
                error_message=str(e)
            )
            raise

    async def execute_job(self, job_id: UUID) -> str:
        """Execute a processing job.

        Args:
            job_id: Job UUID

        Returns:
            Processing result

        Raises:
            ValueError: If job not found or content not found
            Exception: If processing fails
        """
        job = await self._get_job_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Update status to processing
        await self._update_job_status(job_id, JobStatus.PROCESSING.value)

        try:
            # Get content
            content = await self._get_content(job['content_id'])
            if not content:
                raise ValueError(f"Content {job['content_id']} not found")

            # Read extracted text
            text = await self.file_storage.read_extracted_text(content['extracted_text_path'])
            if not text:
                raise ValueError(f"Could not read extracted text for content {job['content_id']}")

            # Process with AI
            result = await self._process_content(
                content=text,
                processing_type=job['processing_type'],
                source_type=content['source_type'],
                user_id=job['user_id'],
                user_prompt=job['user_prompt'],
                language=job['output_language']
            )

            if not result:
                raise Exception("AI processing returned empty result")

            # Save result to file
            result_path = await self.file_storage.save_processing_result(job_id, result)

            # Update job status
            await self._update_job_result(
                job_id,
                JobStatus.COMPLETED.value,
                result_path=result_path
            )

            logger.info(f"Completed job {job_id}")
            return result

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            await self._update_job_status(
                job_id,
                JobStatus.FAILED.value,
                error_message=str(e)
            )
            raise

    async def _process_content(
        self,
        content: str,
        processing_type: str,
        source_type: str,
        user_id: int,
        user_prompt: Optional[str],
        language: str
    ) -> str:
        """Process content with AI.

        Args:
            content: Content text
            processing_type: Processing type
            source_type: Source type
            user_id: User ID
            user_prompt: Optional user instructions
            language: Output language

        Returns:
            AI processing result
        """
        if user_prompt:
            # Process with custom prompt
            return await self.ai_processor.process_content_with_user_prompt(
                content=content,
                processing_type=processing_type,
                source_type=source_type,
                user_id=user_id,
                user_prompt=user_prompt,
                language=language
            )
        else:
            # Process with default prompts
            return await self.ai_processor.process_content(
                content=content,
                processing_type=processing_type,
                source_type=source_type,
                user_id=user_id,
                language=language
            )

    async def get_job_result(self, job_id: UUID) -> Optional[str]:
        """Get job result.

        Args:
            job_id: Job UUID

        Returns:
            Result text or None
        """
        job = await self._get_job_by_id(job_id)
        if not job or not job['result_path']:
            return None

        return await self.file_storage.read_processing_result(job['result_path'])

    async def get_user_jobs(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        content_id: Optional[UUID] = None
    ) -> Tuple[list, int]:
        """Get user's jobs with pagination.

        Args:
            user_id: User ID
            limit: Page size
            offset: Page offset
            status: Filter by status
            content_id: Filter by content ID

        Returns:
            Tuple of (jobs_list, total_count)
        """
        async with self.db._pool.acquire() as conn:
            # Build query
            where_clauses = ["user_id = $1"]
            params = [user_id]

            if status:
                where_clauses.append(f"status = ${len(params) + 1}")
                params.append(status)

            if content_id:
                where_clauses.append(f"content_id = ${len(params) + 1}")
                params.append(content_id)

            where_clause = " AND ".join(where_clauses)

            # Get total count
            count_query = f"SELECT COUNT(*) FROM processing_jobs WHERE {where_clause}"
            total = await conn.fetchval(count_query, *params)

            # Get items
            items_query = f"""
                SELECT * FROM processing_jobs
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
            """
            params.extend([limit, offset])
            rows = await conn.fetch(items_query, *params)

            jobs = [dict(row) for row in rows]
            return jobs, total

    async def retry_job(self, job_id: UUID) -> str:
        """Retry a failed job.

        Args:
            job_id: Job UUID

        Returns:
            Processing result
        """
        # Check if this is a bundle job
        job = await self._get_job_by_id(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Execute appropriate method based on job type
        if job.get('bundle_id') or job.get('content_ids'):
            return await self.execute_bundle_job(job_id)
        else:
            return await self.execute_job(job_id)

    async def _create_job_record(
        self,
        content_id: UUID,
        processing_type: str,
        user_id: int,
        user_prompt: Optional[str],
        output_language: str,
        status: str
    ) -> UUID:
        """Create job record in database."""
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO processing_jobs (
                    content_id, processing_type, user_id, user_prompt,
                    output_language, status, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
                RETURNING id
                """,
                content_id,
                processing_type,
                user_id,
                user_prompt,
                output_language,
                status,
                datetime.utcnow()
            )
            return row['id']

    async def _create_bundle_job_record(
        self,
        bundle_id: UUID,
        content_ids: List[UUID],
        processing_type: str,
        user_id: int,
        user_prompt: Optional[str],
        output_language: str,
        status: str
    ) -> UUID:
        """Create bundle job record in database."""
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO processing_jobs (
                    bundle_id, content_ids, processing_type, user_id, user_prompt,
                    output_language, status, created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
                RETURNING id
                """,
                bundle_id,
                content_ids,
                processing_type,
                user_id,
                user_prompt,
                output_language,
                status,
                datetime.utcnow()
            )
            return row['id']

    async def _get_job_by_id(self, job_id: UUID) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM processing_jobs WHERE id = $1",
                job_id
            )
            return dict(row) if row else None

    async def _get_content(self, content_id: UUID) -> Optional[Dict[str, Any]]:
        """Get content by ID."""
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM content_items WHERE id = $1",
                content_id
            )
            return dict(row) if row else None

    async def _update_job_status(
        self,
        job_id: UUID,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """Update job status."""
        async with self.db._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE processing_jobs
                SET status = $1, error_message = $2, updated_at = $3
                WHERE id = $4
                """,
                status,
                error_message,
                datetime.utcnow(),
                job_id
            )

    async def _update_job_result(
        self,
        job_id: UUID,
        status: str,
        result_path: str
    ) -> None:
        """Update job with result."""
        async with self.db._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE processing_jobs
                SET status = $1, result_path = $2, updated_at = $3
                WHERE id = $4
                """,
                status,
                result_path,
                datetime.utcnow(),
                job_id
            )