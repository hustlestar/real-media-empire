"""Celery tasks for multi-platform content publishing."""

import logging
from typing import Dict, Any, List
from celery import Task
from src.workers.celery_app import app

logger = logging.getLogger(__name__)


class PublishingTask(Task):
    """Base task for publishing with error handling and retries."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}  # More retries for network operations
    retry_backoff = True
    retry_backoff_max = 1800  # 30 minutes
    retry_jitter = True


@app.task(base=PublishingTask, bind=True, name="publishing.upload_to_platform")
def upload_to_platform_task(self, platform: str, video_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upload video to a specific platform.

    Args:
        platform: Platform name (tiktok, instagram, youtube, etc.)
        video_path: Path to video file
        metadata: Video metadata (title, description, tags, etc.)

    Returns:
        Dict containing upload result and platform-specific ID
    """
    try:
        logger.info(f"Uploading to {platform}: {metadata.get('title')}")

        self.update_state(
            state="PROCESSING",
            meta={
                "current": 0,
                "total": 100,
                "status": f"Uploading to {platform}...",
                "platform": platform
            }
        )

        # TODO: Integrate with actual platform APIs
        # from src.social.platforms import get_platform_publisher
        # publisher = get_platform_publisher(platform)
        # result = publisher.upload(video_path, metadata)

        result = {
            "platform": platform,
            "status": "completed",
            "platform_video_id": f"{platform}_video_123",
            "platform_url": f"https://{platform}.com/video/123",
            "uploaded_at": "2025-11-06T15:00:00Z"
        }

        logger.info(f"Upload to {platform} completed successfully")
        return result

    except Exception as e:
        logger.error(f"Upload to {platform} failed: {e}", exc_info=True)
        # Update task metadata with error
        self.update_state(
            state="FAILURE",
            meta={
                "platform": platform,
                "error": str(e)
            }
        )
        raise


@app.task(base=PublishingTask, bind=True, name="publishing.publish_multi_platform")
def publish_multi_platform_task(
    self,
    video_path: str,
    platforms: List[str],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Publish video to multiple platforms simultaneously.

    Args:
        video_path: Path to video file
        platforms: List of platform names
        metadata: Video metadata

    Returns:
        Dict containing results for all platforms
    """
    try:
        job_id = metadata.get("job_id")
        logger.info(f"Publishing to {len(platforms)} platforms: {job_id}")

        total_platforms = len(platforms)
        results = {}
        errors = {}

        for idx, platform in enumerate(platforms):
            self.update_state(
                state="PROCESSING",
                meta={
                    "current": idx,
                    "total": total_platforms,
                    "status": f"Publishing to {platform} ({idx + 1}/{total_platforms})",
                    "completed": list(results.keys()),
                    "failed": list(errors.keys())
                }
            )

            try:
                # Upload to individual platform
                result = upload_to_platform_task.apply(args=[platform, video_path, metadata]).get()
                results[platform] = result
            except Exception as e:
                logger.error(f"Failed to publish to {platform}: {e}")
                errors[platform] = str(e)

        final_result = {
            "job_id": job_id,
            "status": "completed" if not errors else "partial",
            "total_platforms": total_platforms,
            "successful": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors
        }

        logger.info(f"Multi-platform publishing completed: {job_id}")
        return final_result

    except Exception as e:
        logger.error(f"Multi-platform publishing failed: {e}", exc_info=True)
        raise


@app.task(base=PublishingTask, bind=True, name="publishing.schedule_publication")
def schedule_publication_task(
    self,
    video_path: str,
    platforms: List[str],
    metadata: Dict[str, Any],
    scheduled_time: str
) -> Dict[str, Any]:
    """
    Schedule video publication for a future time.

    Args:
        video_path: Path to video file
        platforms: List of platform names
        metadata: Video metadata
        scheduled_time: ISO format timestamp for publication

    Returns:
        Dict containing scheduling confirmation
    """
    try:
        logger.info(f"Scheduling publication for {scheduled_time}")

        # TODO: Integrate with actual scheduling system
        # from src.social.scheduler import schedule_publish
        # result = schedule_publish(video_path, platforms, metadata, scheduled_time)

        result = {
            "job_id": metadata.get("job_id"),
            "status": "scheduled",
            "scheduled_time": scheduled_time,
            "platforms": platforms,
            "eta": scheduled_time
        }

        logger.info(f"Publication scheduled successfully")
        return result

    except Exception as e:
        logger.error(f"Scheduling failed: {e}", exc_info=True)
        raise


@app.task(name="publishing.cleanup_old_jobs")
def cleanup_old_jobs_task(days: int = 30) -> Dict[str, Any]:
    """
    Periodic task to cleanup old publishing jobs.

    Args:
        days: Number of days to keep jobs

    Returns:
        Dict containing cleanup statistics
    """
    try:
        logger.info(f"Cleaning up jobs older than {days} days")

        # TODO: Integrate with database cleanup
        # from src.data.dao import cleanup_old_publishing_jobs
        # result = cleanup_old_publishing_jobs(days)

        result = {
            "deleted_count": 0,
            "status": "completed"
        }

        logger.info(f"Cleanup completed: {result['deleted_count']} jobs deleted")
        return result

    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        raise
