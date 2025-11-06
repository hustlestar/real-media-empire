"""Prompts API endpoints."""

import logging
from typing import Dict
from fastapi import APIRouter, Depends, Query

from core.prompt_manager import PromptManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])


async def get_prompt_manager() -> PromptManager:
    """Get prompt manager instance."""
    return PromptManager()


@router.get("", response_model=Dict[str, Dict[str, str]])
async def get_system_prompts(
    language: str = Query("en", description="Output language (en, ru, es)"),
    prompt_manager: PromptManager = Depends(get_prompt_manager)
):
    """Get all system prompts for different processing types.

    Returns prompts with language parameter injected where applicable.
    """
    try:
        processing_types = prompt_manager.get_all_processing_types()
        prompts = {}

        for ptype in processing_types:
            # Get system prompt with generic source type
            system_prompt = prompt_manager.get_system_prompt(ptype, "combined")

            if system_prompt:
                # Add language instruction if not English
                if language != "en":
                    language_names = {"ru": "Russian", "es": "Spanish", "en": "English"}
                    lang_name = language_names.get(language, language)
                    system_prompt += f"\n\nIMPORTANT: Respond in {lang_name} language."

                prompts[ptype] = {
                    "system_prompt": system_prompt,
                    "description": _get_processing_description(ptype)
                }

        return prompts

    except Exception as e:
        logger.error(f"Error getting system prompts: {e}", exc_info=True)
        return {}


def _get_processing_description(processing_type: str) -> str:
    """Get human-readable description for processing type."""
    descriptions = {
        "summary": "Create comprehensive summaries of content",
        "mvp_plan": "Generate MVP plans for digital products",
        "content_ideas": "Generate creative content ideas and strategies"
    }
    return descriptions.get(processing_type, processing_type.replace("_", " ").title())
