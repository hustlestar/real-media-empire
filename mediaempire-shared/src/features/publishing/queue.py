"""
Publishing Queue System - Database-backed queue for scheduled publishing.
Handles scheduling, retries, status tracking, and webhooks.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from pathlib import Path
import json

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .platforms.base import PublishConfig, PublishResult, PublishStatus
from .manager import PublishingManager

logger = logging.getLogger(__name__)

Base = declarative_base()


class QueueStatus(str, Enum):
    """Status of queued publishing job."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class PublishJob(Base):
    """Database model for publishing job."""
    __tablename__ = "publish_jobs"

    id = Column(String, primary_key=True)
    account_id = Column(String, nullable=False, index=True)
    platforms = Column(Text, nullable=False)  # JSON array
    video_path = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    config_json = Column(Text, nullable=False)  # JSON PublishConfig

    status = Column(String, nullable=False, default=QueueStatus.PENDING, index=True)
    priority = Column(Integer, default=5)  # 1-10, higher = more priority

    scheduled_time = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=300)  # 5 minutes

    results_json = Column(Text, nullable=True)  # JSON results
    error_message = Column(Text, nullable=True)

    webhook_url = Column(String, nullable=True)
    callback_data = Column(Text, nullable=True)

    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)


class QueuedPublishConfig(BaseModel):
    """Configuration for queued publish job."""
    account_id: str
    platforms: List[str]
    video_path: str
    config: PublishConfig

    scheduled_time: Optional[datetime] = None
    priority: int = 5
    max_retries: int = 3
    retry_delay_seconds: int = 300
    webhook_url: Optional[str] = None
    callback_data: Optional[Dict] = None


class PublishingQueue:
    """Queue manager for scheduled and batch publishing."""

    def __init__(
        self,
        db_session: Session,
        manager: PublishingManager,
        worker_count: int = 3
    ):
        """
        Initialize publishing queue.

        Args:
            db_session: SQLAlchemy database session
            manager: PublishingManager instance
            worker_count: Number of concurrent workers
        """
        self.db = db_session
        self.manager = manager
        self.worker_count = worker_count
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.webhooks: Dict[str, Callable] = {}

    def add_job(
        self,
        job_id: str,
        config: QueuedPublishConfig
    ) -> PublishJob:
        """
        Add new publishing job to queue.

        Args:
            job_id: Unique job identifier
            config: Job configuration

        Returns:
            Created PublishJob instance
        """
        # Create job record
        job = PublishJob(
            id=job_id,
            account_id=config.account_id,
            platforms=json.dumps(config.platforms),
            video_path=config.video_path,
            title=config.config.title,
            description=config.config.description,
            config_json=config.config.json(),
            status=QueueStatus.SCHEDULED if config.scheduled_time else QueueStatus.PENDING,
            priority=config.priority,
            scheduled_time=config.scheduled_time,
            max_retries=config.max_retries,
            retry_delay_seconds=config.retry_delay_seconds,
            webhook_url=config.webhook_url,
            callback_data=json.dumps(config.callback_data) if config.callback_data else None
        )

        self.db.add(job)
        self.db.commit()

        logger.info(f"Added job {job_id} to queue: {config.platforms} for {config.account_id}")
        return job

    def get_job(self, job_id: str) -> Optional[PublishJob]:
        """Get job by ID."""
        return self.db.query(PublishJob).filter(PublishJob.id == job_id).first()

    def update_job_status(
        self,
        job_id: str,
        status: QueueStatus,
        error_message: Optional[str] = None,
        results: Optional[Dict] = None
    ) -> None:
        """Update job status."""
        job = self.get_job(job_id)
        if not job:
            return

        job.status = status

        if status == QueueStatus.PROCESSING:
            job.started_at = datetime.utcnow()
        elif status in [QueueStatus.COMPLETED, QueueStatus.FAILED, QueueStatus.CANCELLED]:
            job.completed_at = datetime.utcnow()

        if error_message:
            job.error_message = error_message

        if results:
            job.results_json = json.dumps(results, default=str)

        self.db.commit()
        logger.info(f"Job {job_id} status updated to {status}")

    def cancel_job(self, job_id: str) -> bool:
        """Cancel pending or scheduled job."""
        job = self.get_job(job_id)
        if not job:
            return False

        if job.status not in [QueueStatus.PENDING, QueueStatus.SCHEDULED]:
            logger.warning(f"Cannot cancel job {job_id} with status {job.status}")
            return False

        self.update_job_status(job_id, QueueStatus.CANCELLED)
        return True

    def get_pending_jobs(self, limit: int = 10) -> List[PublishJob]:
        """
        Get pending jobs ready to process.

        Returns jobs that are:
        - Status PENDING or SCHEDULED with time passed
        - Ordered by priority (high to low) then created_at (old to new)
        """
        now = datetime.utcnow()

        jobs = (
            self.db.query(PublishJob)
            .filter(
                (PublishJob.status == QueueStatus.PENDING) |
                (
                    (PublishJob.status == QueueStatus.SCHEDULED) &
                    (PublishJob.scheduled_time <= now)
                )
            )
            .order_by(PublishJob.priority.desc(), PublishJob.created_at.asc())
            .limit(limit)
            .all()
        )

        return jobs

    def get_retry_jobs(self) -> List[PublishJob]:
        """Get failed jobs that should be retried."""
        jobs = (
            self.db.query(PublishJob)
            .filter(
                PublishJob.status == QueueStatus.FAILED,
                PublishJob.retry_count < PublishJob.max_retries
            )
            .all()
        )

        # Filter jobs where retry delay has passed
        now = datetime.utcnow()
        ready_jobs = []

        for job in jobs:
            if not job.completed_at:
                continue

            retry_time = job.completed_at + timedelta(seconds=job.retry_delay_seconds)
            if now >= retry_time:
                ready_jobs.append(job)

        return ready_jobs

    async def process_job(self, job: PublishJob) -> None:
        """
        Process a single publishing job.

        Args:
            job: PublishJob to process
        """
        try:
            # Update status to processing
            self.update_job_status(job.id, QueueStatus.PROCESSING)

            # Parse configuration
            platforms = json.loads(job.platforms)
            config = PublishConfig.parse_raw(job.config_json)

            # Validate video exists
            if not Path(job.video_path).exists():
                raise FileNotFoundError(f"Video not found: {job.video_path}")

            # Publish to all platforms
            logger.info(f"Processing job {job.id}: {platforms}")
            results = await self.manager.publish_multi_platform(
                account_id=job.account_id,
                platforms=platforms,
                video_path=job.video_path,
                config=config
            )

            # Check if all succeeded
            all_success = all(r.success for r in results.values())

            if all_success:
                self.update_job_status(
                    job.id,
                    QueueStatus.COMPLETED,
                    results={p: r.dict() for p, r in results.items()}
                )
                await self._trigger_webhook(job, success=True, results=results)
            else:
                # Some failed
                errors = [f"{p}: {r.error}" for p, r in results.items() if not r.success]
                error_msg = "; ".join(errors)

                # Check if we should retry
                if job.retry_count < job.max_retries:
                    job.retry_count += 1
                    self.update_job_status(
                        job.id,
                        QueueStatus.FAILED,
                        error_message=f"Attempt {job.retry_count}: {error_msg}",
                        results={p: r.dict() for p, r in results.items()}
                    )
                    logger.warning(f"Job {job.id} failed, will retry ({job.retry_count}/{job.max_retries})")
                else:
                    self.update_job_status(
                        job.id,
                        QueueStatus.FAILED,
                        error_message=f"Max retries exceeded: {error_msg}",
                        results={p: r.dict() for p, r in results.items()}
                    )
                    await self._trigger_webhook(job, success=False, results=results)

        except Exception as e:
            logger.error(f"Error processing job {job.id}: {e}", exc_info=True)

            if job.retry_count < job.max_retries:
                job.retry_count += 1
                self.update_job_status(
                    job.id,
                    QueueStatus.FAILED,
                    error_message=f"Attempt {job.retry_count}: {str(e)}"
                )
            else:
                self.update_job_status(
                    job.id,
                    QueueStatus.FAILED,
                    error_message=f"Max retries exceeded: {str(e)}"
                )
                await self._trigger_webhook(job, success=False, error=str(e))

    async def _trigger_webhook(
        self,
        job: PublishJob,
        success: bool,
        results: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> None:
        """Trigger webhook notification for job completion."""
        if not job.webhook_url:
            return

        try:
            import aiohttp

            payload = {
                'job_id': job.id,
                'account_id': job.account_id,
                'platforms': json.loads(job.platforms),
                'title': job.title,
                'success': success,
                'status': job.status,
                'created_at': job.created_at.isoformat(),
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'results': {p: r.dict() for p, r in results.items()} if results else None,
                'error': error,
                'callback_data': json.loads(job.callback_data) if job.callback_data else None
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(job.webhook_url, json=payload) as resp:
                    if resp.status >= 400:
                        logger.warning(f"Webhook failed for job {job.id}: {resp.status}")
                    else:
                        logger.info(f"Webhook triggered for job {job.id}")

        except Exception as e:
            logger.error(f"Error triggering webhook for job {job.id}: {e}")

    async def worker(self, worker_id: int) -> None:
        """
        Background worker that processes jobs from queue.

        Args:
            worker_id: Worker identifier for logging
        """
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Get pending jobs
                jobs = self.get_pending_jobs(limit=1)

                # Check for retry jobs if no pending
                if not jobs:
                    jobs = self.get_retry_jobs()[:1]

                if jobs:
                    await self.process_job(jobs[0])
                else:
                    # No jobs, wait before checking again
                    await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}", exc_info=True)
                await asyncio.sleep(10)

        logger.info(f"Worker {worker_id} stopped")

    async def start(self) -> None:
        """Start queue workers."""
        if self.running:
            logger.warning("Queue already running")
            return

        self.running = True
        logger.info(f"Starting {self.worker_count} queue workers")

        self.workers = [
            asyncio.create_task(self.worker(i))
            for i in range(self.worker_count)
        ]

    async def stop(self) -> None:
        """Stop queue workers gracefully."""
        if not self.running:
            return

        logger.info("Stopping queue workers")
        self.running = False

        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)

        self.workers = []
        logger.info("Queue stopped")

    def get_queue_stats(self) -> Dict:
        """Get queue statistics."""
        stats = {}

        for status in QueueStatus:
            count = self.db.query(PublishJob).filter(PublishJob.status == status.value).count()
            stats[status.value] = count

        # Additional stats
        stats['total'] = self.db.query(PublishJob).count()
        stats['scheduled_future'] = (
            self.db.query(PublishJob)
            .filter(
                PublishJob.status == QueueStatus.SCHEDULED,
                PublishJob.scheduled_time > datetime.utcnow()
            )
            .count()
        )

        return stats

    def list_jobs(
        self,
        status: Optional[QueueStatus] = None,
        account_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[PublishJob]:
        """List jobs with optional filtering."""
        query = self.db.query(PublishJob)

        if status:
            query = query.filter(PublishJob.status == status)

        if account_id:
            query = query.filter(PublishJob.account_id == account_id)

        query = query.order_by(PublishJob.created_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()
