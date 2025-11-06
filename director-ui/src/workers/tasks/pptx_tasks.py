"""Celery tasks for PowerPoint presentation generation."""

import logging
from typing import Dict, Any
from celery import Task
from workers.celery_app import app

logger = logging.getLogger(__name__)


class PPTXGenerationTask(Task):
    """Base task for PPTX generation with error handling."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


@app.task(base=PPTXGenerationTask, bind=True, name="pptx.fetch_content")
def fetch_content_task(self, source_type: str, source_url: str) -> Dict[str, Any]:
    """
    Fetch content from various sources (YouTube, Web, File).

    Args:
        source_type: Type of content source (youtube, web, file)
        source_url: URL or path to content

    Returns:
        Dict containing extracted content
    """
    try:
        logger.info(f"Fetching content from {source_type}: {source_url}")

        self.update_state(
            state="PROCESSING",
            meta={
                "current": 0,
                "total": 100,
                "status": f"Fetching content from {source_type}...",
            }
        )

        # TODO: Integrate with actual content fetchers
        # from src.content_fetchers import fetch_content
        # result = fetch_content(source_type, source_url)

        result = {
            "source_type": source_type,
            "source_url": source_url,
            "content": "Fetched content placeholder",
            "word_count": 1500,
            "status": "completed"
        }

        logger.info(f"Content fetching completed from {source_type}")
        return result

    except Exception as e:
        logger.error(f"Content fetching failed: {e}", exc_info=True)
        raise


@app.task(base=PPTXGenerationTask, bind=True, name="pptx.generate_outline")
def generate_outline_task(self, presentation_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate presentation outline using AI.

    Args:
        presentation_config: Configuration including topic, content, audience

    Returns:
        Dict containing generated outline
    """
    try:
        logger.info(f"Generating outline for: {presentation_config.get('topic')}")

        self.update_state(
            state="PROCESSING",
            meta={
                "current": 0,
                "total": 100,
                "status": "Generating outline with AI...",
            }
        )

        # TODO: Integrate with OpenAI for outline generation
        # from src.text.chat_gpt import generate_presentation_outline
        # result = generate_presentation_outline(presentation_config)

        num_slides = presentation_config.get("num_slides", 10)
        result = {
            "presentation_id": presentation_config.get("presentation_id"),
            "outline": [
                {"slide": i, "title": f"Slide {i}", "content": ["Bullet 1", "Bullet 2"]}
                for i in range(1, num_slides + 1)
            ],
            "estimated_cost": 0.15,
            "status": "completed"
        }

        logger.info(f"Outline generation completed")
        return result

    except Exception as e:
        logger.error(f"Outline generation failed: {e}", exc_info=True)
        raise


@app.task(base=PPTXGenerationTask, bind=True, name="pptx.generate_slides")
def generate_slides_task(self, presentation_id: str, outline: list, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate PowerPoint presentation from outline.

    Args:
        presentation_id: Unique presentation identifier
        outline: Presentation outline with slide structure
        config: Additional configuration (theme, template, etc.)

    Returns:
        Dict containing generated presentation metadata
    """
    try:
        logger.info(f"Generating slides for presentation: {presentation_id}")

        total_slides = len(outline)
        for idx, slide_config in enumerate(outline):
            self.update_state(
                state="PROCESSING",
                meta={
                    "current": idx,
                    "total": total_slides,
                    "status": f"Generating slide {idx + 1}/{total_slides}",
                }
            )

        # TODO: Integrate with actual PPTX generation
        # from src.pptx_gen import create_presentation
        # result = create_presentation(presentation_id, outline, config)

        result = {
            "presentation_id": presentation_id,
            "status": "completed",
            "output_path": f"/media/presentations/{presentation_id}.pptx",
            "thumbnail_url": f"/media/presentations/{presentation_id}_thumb.jpg",
            "total_slides": total_slides,
            "total_cost": config.get("estimated_cost", 0.20)
        }

        logger.info(f"Presentation generation completed: {presentation_id}")
        return result

    except Exception as e:
        logger.error(f"Slide generation failed: {e}", exc_info=True)
        raise


@app.task(base=PPTXGenerationTask, bind=True, name="pptx.generate_full")
def generate_full_presentation_task(self, presentation_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full pipeline: fetch content, generate outline, create slides.

    Args:
        presentation_config: Complete presentation configuration

    Returns:
        Dict containing final presentation metadata
    """
    try:
        presentation_id = presentation_config.get("presentation_id")
        logger.info(f"Starting full presentation generation: {presentation_id}")

        # Step 1: Fetch content if needed
        if presentation_config.get("content_source") in ["youtube", "web", "file"]:
            self.update_state(state="PROCESSING", meta={"status": "Fetching content..."})
            content = fetch_content_task.apply(args=[
                presentation_config.get("content_source"),
                presentation_config.get("content_url")
            ]).get()
            presentation_config["content"] = content.get("content")

        # Step 2: Generate outline
        self.update_state(state="PROCESSING", meta={"status": "Generating outline..."})
        outline_result = generate_outline_task.apply(args=[presentation_config]).get()

        # Step 3: Generate slides
        self.update_state(state="PROCESSING", meta={"status": "Creating slides..."})
        result = generate_slides_task.apply(args=[
            presentation_id,
            outline_result.get("outline"),
            presentation_config
        ]).get()

        logger.info(f"Full presentation generation completed: {presentation_id}")
        return result

    except Exception as e:
        logger.error(f"Full presentation generation failed: {e}", exc_info=True)
        raise
