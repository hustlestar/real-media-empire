"""
Comprehensive DAO tests for ProcessingService with SQLite.

Tests all database operations for processing jobs including CRUD, execution, and bundle jobs.
"""

import pytest
from uuid import UUID, uuid4
import json


@pytest.mark.asyncio
class TestProcessingServiceDAO:
    """Test ProcessingService database operations."""

    async def test_create_job_record(self, processing_service, test_content, test_user):
        """Test creating a processing job record."""
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt="Custom prompt",
            output_language="en",
            status="pending"
        )

        assert job_id is not None
        assert isinstance(job_id, str)

        # Verify job was created
        job = await processing_service._get_job_by_id(job_id)
        assert job is not None
        assert job['content_id'] == test_content
        assert job['processing_type'] == "summary"
        assert job['user_prompt'] == "Custom prompt"
        assert job['status'] == "pending"

    async def test_get_job_by_id_existing(self, processing_service, test_content, test_user):
        """Test retrieving job by ID when it exists."""
        # Create job
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="mvp_plan",
            user_id=test_user,
            user_prompt=None,
            output_language="ru",
            status="pending"
        )

        # Retrieve job
        job = await processing_service._get_job_by_id(job_id)

        assert job is not None
        assert job['id'] == job_id
        assert job['processing_type'] == "mvp_plan"
        assert job['output_language'] == "ru"

    async def test_get_job_by_id_nonexistent(self, processing_service):
        """Test retrieving non-existent job."""
        fake_id = str(uuid4())
        job = await processing_service._get_job_by_id(fake_id)
        assert job is None

    async def test_update_job_status(self, processing_service, test_content, test_user):
        """Test updating job status."""
        # Create job
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        # Update to processing
        await processing_service._update_job_status(job_id, "processing")

        job = await processing_service._get_job_by_id(job_id)
        assert job['status'] == "processing"

        # Update to completed
        await processing_service._update_job_status(job_id, "completed")

        job = await processing_service._get_job_by_id(job_id)
        assert job['status'] == "completed"

    async def test_update_job_status_with_error(self, processing_service, test_content, test_user):
        """Test updating job status with error message."""
        # Create job
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        # Update to failed with error
        error_msg = "Processing failed due to timeout"
        await processing_service._update_job_status(
            job_id,
            "failed",
            error_message=error_msg
        )

        job = await processing_service._get_job_by_id(job_id)
        assert job['status'] == "failed"
        assert job['error_message'] == error_msg

    async def test_update_job_result(self, processing_service, test_content, test_user, file_storage):
        """Test updating job with result."""
        # Create job
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="processing"
        )

        # Save result
        result_text = "This is the processing result"
        result_path = await file_storage.save_processing_result(job_id, result_text)

        # Update job
        await processing_service._update_job_result(
            job_id,
            "completed",
            result_path=result_path
        )

        job = await processing_service._get_job_by_id(job_id)
        assert job['status'] == "completed"
        assert job['result_path'] == result_path

    async def test_get_content(self, processing_service, test_content):
        """Test retrieving content via processing service."""
        content = await processing_service._get_content(test_content)

        assert content is not None
        assert content['id'] == test_content
        assert 'source_type' in content

    async def test_get_content_nonexistent(self, processing_service):
        """Test retrieving non-existent content."""
        fake_id = str(uuid4())
        content = await processing_service._get_content(fake_id)
        assert content is None

    async def test_get_user_jobs_pagination(self, processing_service, test_content, test_user):
        """Test paginating user jobs."""
        # Create multiple jobs
        job_ids = []
        for i in range(5):
            job_id = await processing_service._create_job_record(
                content_id=test_content,
                processing_type="summary",
                user_id=test_user,
                user_prompt=f"Prompt {i}",
                output_language="en",
                status="pending"
            )
            job_ids.append(job_id)

        # Get first page
        jobs, total = await processing_service.get_user_jobs(test_user, limit=2, offset=0)

        assert total == 5
        assert len(jobs) == 2

        # Get second page
        jobs2, total2 = await processing_service.get_user_jobs(test_user, limit=2, offset=2)

        assert total2 == 5
        assert len(jobs2) == 2

        # Ensure no overlap
        page1_ids = {job['id'] for job in jobs}
        page2_ids = {job['id'] for job in jobs2}
        assert page1_ids.isdisjoint(page2_ids)

    async def test_get_user_jobs_filter_by_status(self, processing_service, test_content, test_user):
        """Test filtering jobs by status."""
        # Create jobs with different statuses
        pending_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        completed_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="mvp_plan",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="completed"
        )

        # Filter by pending
        pending_jobs, pending_total = await processing_service.get_user_jobs(
            test_user,
            status="pending"
        )

        pending_ids = {job['id'] for job in pending_jobs}
        assert pending_id in pending_ids
        assert completed_id not in pending_ids

        # Filter by completed
        completed_jobs, completed_total = await processing_service.get_user_jobs(
            test_user,
            status="completed"
        )

        completed_ids = {job['id'] for job in completed_jobs}
        assert completed_id in completed_ids
        assert pending_id not in completed_ids

    async def test_get_user_jobs_filter_by_content_id(self, processing_service, db_manager, test_user, file_storage):
        """Test filtering jobs by content ID."""
        # Create two content items
        import uuid

        content_hash1 = f"hash1_{uuid.uuid4().hex[:8]}"
        text_path1 = await file_storage.save_extracted_text(content_hash1, "Content 1")

        async with db_manager._pool.acquire() as conn:
            async with conn.transaction():
                from sqlalchemy import text
                result = await conn.fetchrow(
                    text("""
                        INSERT INTO content_items (
                            id, content_hash, source_type, extracted_text_path,
                            extracted_text_paths, content_metadata, user_id,
                            processing_status, created_at, updated_at
                        )
                        VALUES (:id, :hash, 'pdf_url', :path, :paths, :metadata, :user_id, 'completed', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "hash": content_hash1,
                        "path": text_path1,
                        "paths": json.dumps({"en": text_path1}),
                        "metadata": json.dumps({}),
                        "user_id": test_user
                    }
                )
                content_id1 = result['id']

        content_hash2 = f"hash2_{uuid.uuid4().hex[:8]}"
        text_path2 = await file_storage.save_extracted_text(content_hash2, "Content 2")

        async with db_manager._pool.acquire() as conn:
            async with conn.transaction():
                from sqlalchemy import text
                result = await conn.fetchrow(
                    text("""
                        INSERT INTO content_items (
                            id, content_hash, source_type, extracted_text_path,
                            extracted_text_paths, content_metadata, user_id,
                            processing_status, created_at, updated_at
                        )
                        VALUES (:id, :hash, 'pdf_url', :path, :paths, :metadata, :user_id, 'completed', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "hash": content_hash2,
                        "path": text_path2,
                        "paths": json.dumps({"en": text_path2}),
                        "metadata": json.dumps({}),
                        "user_id": test_user
                    }
                )
                content_id2 = result['id']

        # Create jobs for each content
        job1_id = await processing_service._create_job_record(
            content_id=content_id1,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        job2_id = await processing_service._create_job_record(
            content_id=content_id2,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        # Filter by content_id1
        jobs1, total1 = await processing_service.get_user_jobs(
            test_user,
            content_id=content_id1
        )

        job1_ids = {job['id'] for job in jobs1}
        assert job1_id in job1_ids
        assert job2_id not in job1_ids

    async def test_create_bundle_job_record(self, processing_service, test_content, test_user, db_manager):
        """Test creating a bundle job record."""
        import uuid

        # Create bundle
        bundle_id = str(uuid.uuid4())
        content_ids = [test_content, str(uuid.uuid4())]

        async with db_manager._pool.acquire() as conn:
            from sqlalchemy import text
            await conn.execute(
                text("""
                    INSERT INTO bundles (id, user_id, name, content_ids, created_at, updated_at)
                    VALUES (:id, :user_id, :name, :content_ids, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """),
                {
                    "id": bundle_id,
                    "user_id": test_user,
                    "name": "Test Bundle",
                    "content_ids": json.dumps(content_ids)
                }
            )

        # Create bundle job
        job_id = await processing_service._create_bundle_job_record(
            bundle_id=bundle_id,
            content_ids=content_ids,
            processing_type="summary",
            user_id=test_user,
            user_prompt="Bundle prompt",
            output_language="en",
            status="pending"
        )

        assert job_id is not None

        # Verify job
        job = await processing_service._get_job_by_id(job_id)
        assert job is not None
        assert job['bundle_id'] == bundle_id

        # Parse content_ids
        job_content_ids = job['content_ids']
        if isinstance(job_content_ids, str):
            job_content_ids = json.loads(job_content_ids)
        assert len(job_content_ids) == 2

    async def test_execute_job_success(self, processing_service, test_content, test_user, file_storage):
        """Test executing a job successfully."""
        # Write actual content text
        content = await processing_service._get_content(test_content)
        test_text = "This is content for processing"
        text_path = await file_storage.save_extracted_text(content['content_hash'], test_text)

        # Update content with real path
        async with processing_service.db._pool.acquire() as conn:
            from sqlalchemy import text
            await conn.execute(
                text("UPDATE content_items SET extracted_text_path = :path WHERE id = :id"),
                {"path": text_path, "id": test_content}
            )

        # Create and execute job
        job = await processing_service.create_job(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            execute_immediately=True
        )

        assert job is not None
        assert job['status'] == "completed"
        assert job['result_path'] is not None

        # Verify result was saved
        result = await processing_service.get_job_result(job['id'])
        assert result is not None
        assert len(result) > 0

    async def test_execute_job_with_user_prompt(self, processing_service, test_content, test_user, file_storage):
        """Test executing job with custom user prompt."""
        # Write actual content text
        content = await processing_service._get_content(test_content)
        test_text = "Content with custom prompt"
        text_path = await file_storage.save_extracted_text(content['content_hash'], test_text)

        # Update content
        async with processing_service.db._pool.acquire() as conn:
            from sqlalchemy import text
            await conn.execute(
                text("UPDATE content_items SET extracted_text_path = :path WHERE id = :id"),
                {"path": text_path, "id": test_content}
            )

        # Create and execute job with user prompt
        job = await processing_service.create_job(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt="Focus on key points only",
            execute_immediately=True
        )

        assert job['status'] == "completed"
        assert job['user_prompt'] == "Focus on key points only"

        # Result should mention the prompt
        result = await processing_service.get_job_result(job['id'])
        assert "Focus on key points only" in result

    async def test_retry_job(self, processing_service, test_content, test_user, file_storage):
        """Test retrying a failed job."""
        # Write content
        content = await processing_service._get_content(test_content)
        test_text = "Content for retry"
        text_path = await file_storage.save_extracted_text(content['content_hash'], test_text)

        async with processing_service.db._pool.acquire() as conn:
            from sqlalchemy import text
            await conn.execute(
                text("UPDATE content_items SET extracted_text_path = :path WHERE id = :id"),
                {"path": text_path, "id": test_content}
            )

        # Create failed job
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="failed"
        )

        # Update with error
        await processing_service._update_job_status(
            job_id,
            "failed",
            error_message="Original failure"
        )

        # Retry
        result = await processing_service.retry_job(job_id)

        assert result is not None

        # Job should be completed now
        job = await processing_service._get_job_by_id(job_id)
        assert job['status'] == "completed"
        assert job['result_path'] is not None

    async def test_get_job_result_nonexistent(self, processing_service):
        """Test getting result for non-existent job."""
        fake_id = str(uuid4())
        result = await processing_service.get_job_result(fake_id)
        assert result is None

    async def test_get_job_result_no_result_path(self, processing_service, test_content, test_user):
        """Test getting result for job with no result yet."""
        # Create pending job
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        result = await processing_service.get_job_result(job_id)
        assert result is None

    async def test_create_job_without_immediate_execution(self, processing_service, test_content, test_user):
        """Test creating job without executing immediately."""
        job = await processing_service.create_job(
            content_id=test_content,
            processing_type="mvp_plan",
            user_id=test_user,
            execute_immediately=False
        )

        assert job is not None
        assert job['status'] == "pending"
        assert job['result_path'] is None

    async def test_empty_user_jobs_list(self, processing_service, db_manager):
        """Test getting jobs for user with no jobs."""
        # Create user with no jobs
        async with db_manager.session() as session:
            from sqlalchemy import text
            result = await session.execute(
                text("""
                    INSERT INTO users (id, email, hashed_password, is_active, created_at, updated_at)
                    VALUES (888, 'nojobs@example.com', 'hashed', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                """)
            )
            await session.commit()

        jobs, total = await processing_service.get_user_jobs(888, limit=20, offset=0)

        assert total == 0
        assert len(jobs) == 0

    async def test_multiple_jobs_same_content(self, processing_service, test_content, test_user):
        """Test creating multiple jobs for the same content."""
        # Create 3 jobs for same content with different types
        job1_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        job2_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="mvp_plan",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )

        job3_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="content_ideas",
            user_id=test_user,
            user_prompt=None,
            output_language="ru",
            status="pending"
        )

        # All should be unique
        assert len({job1_id, job2_id, job3_id}) == 3

        # All should be for same content
        job1 = await processing_service._get_job_by_id(job1_id)
        job2 = await processing_service._get_job_by_id(job2_id)
        job3 = await processing_service._get_job_by_id(job3_id)

        assert job1['content_id'] == test_content
        assert job2['content_id'] == test_content
        assert job3['content_id'] == test_content

    async def test_job_timestamps(self, processing_service, test_content, test_user):
        """Test that job timestamps are set correctly."""
        import time

        # Create job
        before = time.time()
        job_id = await processing_service._create_job_record(
            content_id=test_content,
            processing_type="summary",
            user_id=test_user,
            user_prompt=None,
            output_language="en",
            status="pending"
        )
        after = time.time()

        job = await processing_service._get_job_by_id(job_id)

        # Verify created_at exists
        assert 'created_at' in job
        assert 'updated_at' in job
