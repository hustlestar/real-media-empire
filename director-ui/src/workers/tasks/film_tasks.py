"""Celery tasks for AI film generation."""

import logging
import asyncio
from typing import Dict, Any
from celery import Task
from workers.celery_app import app
from websocket.manager import broadcast_job_progress, broadcast_job_completed, broadcast_job_failed

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async functions from sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class FilmGenerationTask(Task):
    """Base task for film generation with error handling."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True


@app.task(base=FilmGenerationTask, bind=True, name="film.generate_shot")
def generate_shot_task(self, shot_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a single video shot using AI providers.

    Args:
        shot_config: Shot configuration including prompt, style, providers

    Returns:
        Dict containing generated shot metadata and file paths
    """
    shot_id = shot_config.get('shot_id')
    try:
        logger.info(f"Starting shot generation: {shot_id}")

        # Update task state and broadcast via WebSocket
        progress = {
            "current": 0,
            "total": 100,
            "status": "Generating image...",
        }
        self.update_state(state="PROCESSING", meta=progress)
        run_async(broadcast_job_progress(self.request.id, progress))

        # TODO: Integrate with actual film generation pipeline
        # from src.film.providers import generate_shot
        # result = generate_shot(shot_config)

        # Mock result for now
        result = {
            "shot_id": shot_id,
            "status": "completed",
            "video_url": f"/media/shots/{shot_id}.mp4",
            "thumbnail_url": f"/media/shots/{shot_id}_thumb.jpg",
            "cost": 0.5,
            "duration": 5.0,
            "metadata": shot_config
        }

        logger.info(f"Shot generation completed: {shot_id}")

        # Broadcast completion
        run_async(broadcast_job_completed(self.request.id, result))

        return result

    except Exception as e:
        logger.error(f"Shot generation failed: {e}", exc_info=True)
        run_async(broadcast_job_failed(self.request.id, str(e)))
        raise


@app.task(base=FilmGenerationTask, bind=True, name="film.generate_scene")
def generate_scene_task(self, scene_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a complete scene with multiple shots.

    Args:
        scene_config: Scene configuration with multiple shots

    Returns:
        Dict containing generated scene metadata
    """
    try:
        logger.info(f"Starting scene generation: {scene_config.get('scene_id')}")

        shots = scene_config.get("shots", [])
        total_shots = len(shots)
        generated_shots = []

        for idx, shot_config in enumerate(shots):
            # Update progress
            self.update_state(
                state="PROCESSING",
                meta={
                    "current": idx,
                    "total": total_shots,
                    "status": f"Generating shot {idx + 1}/{total_shots}",
                }
            )

            # Generate individual shot (could also spawn sub-tasks)
            shot_result = generate_shot_task.apply(args=[shot_config]).get()
            generated_shots.append(shot_result)

        result = {
            "scene_id": scene_config.get("scene_id"),
            "status": "completed",
            "shots": generated_shots,
            "total_cost": sum(shot.get("cost", 0) for shot in generated_shots),
            "total_duration": sum(shot.get("duration", 0) for shot in generated_shots)
        }

        logger.info(f"Scene generation completed: {scene_config.get('scene_id')}")
        return result

    except Exception as e:
        logger.error(f"Scene generation failed: {e}", exc_info=True)
        raise


@app.task(base=FilmGenerationTask, bind=True, name="film.compile_film")
def compile_film_task(self, film_id: str, scenes: list) -> Dict[str, Any]:
    """
    Compile multiple scenes into a final film.

    Args:
        film_id: Unique film identifier
        scenes: List of generated scenes

    Returns:
        Dict containing final film metadata
    """
    try:
        logger.info(f"Starting film compilation: {film_id}")

        self.update_state(
            state="PROCESSING",
            meta={
                "current": 0,
                "total": 100,
                "status": "Compiling scenes...",
            }
        )

        # TODO: Integrate with actual video compilation pipeline
        # from src.film.compiler import compile_scenes
        # result = compile_scenes(film_id, scenes)

        result = {
            "film_id": film_id,
            "status": "completed",
            "output_path": f"/media/films/{film_id}.mp4",
            "thumbnail_url": f"/media/films/{film_id}_poster.jpg",
            "total_scenes": len(scenes),
            "total_cost": sum(scene.get("total_cost", 0) for scene in scenes),
            "duration": sum(scene.get("total_duration", 0) for scene in scenes)
        }

        logger.info(f"Film compilation completed: {film_id}")
        return result

    except Exception as e:
        logger.error(f"Film compilation failed: {e}", exc_info=True)
        raise
