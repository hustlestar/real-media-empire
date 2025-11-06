"""AI processing module for content analysis and generation."""

import logging
from typing import Optional, Dict, Any, List

from core.ai_interface import AIProviderInterface
from core.prompt_manager import PromptManager

logger = logging.getLogger(__name__)

class AIProcessor:
    """Handles AI-powered content processing and generation."""

    def __init__(self, ai_provider: AIProviderInterface, prompt_manager: PromptManager = None):
        self.ai_provider = ai_provider
        self.prompt_manager = prompt_manager or PromptManager()

    async def generate_summary(self, content: str, source_type: str, user_id: int, language: str = "en") -> Optional[str]:
        """Generate a summary of the extracted content."""
        try:
            system_prompt = self.prompt_manager.get_system_prompt("summary", source_type)
            if language != "en":
                language_names = {"ru": "Russian", "es": "Spanish", "en": "English"}
                lang_name = language_names.get(language, language)
                system_prompt += f"\n\nIMPORTANT: Respond in {lang_name} language."
            user_prompt = self.prompt_manager.get_user_prompt("summary", source_type, content)

            if not system_prompt or not user_prompt:
                logger.error("Failed to get prompts for summary generation")
                return None

            response = await self.ai_provider.get_response(
                message=user_prompt,
                user_id=user_id,
                system_prompt=system_prompt
            )

            return response

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None

    async def generate_mvp_plan(self, content: str, source_type: str, user_id: int, language: str = "en") -> Optional[str]:
        """Generate a detailed technical MVP plan for apps mentioned in the content."""
        try:
            system_prompt = self.prompt_manager.get_system_prompt("mvp_plan", source_type)
            if language != "en":
                language_names = {"ru": "Russian", "es": "Spanish", "en": "English"}
                lang_name = language_names.get(language, language)
                system_prompt += f"\n\nIMPORTANT: Respond in {lang_name} language."
            user_prompt = self.prompt_manager.get_user_prompt("mvp_plan", source_type, content)

            if not system_prompt or not user_prompt:
                logger.error("Failed to get prompts for MVP plan generation")
                return None

            response = await self.ai_provider.get_response(
                message=user_prompt,
                user_id=user_id,
                system_prompt=system_prompt
            )

            return response

        except Exception as e:
            logger.error(f"Error generating MVP plan: {e}")
            return None

    async def generate_content_ideas(self, content: str, source_type: str, user_id: int, language: str = "en") -> Optional[str]:
        """Generate content ideas, plans, and scenarios based on the content."""
        try:
            system_prompt = self.prompt_manager.get_system_prompt("content_ideas", source_type)
            if language != "en":
                language_names = {"ru": "Russian", "es": "Spanish", "en": "English"}
                lang_name = language_names.get(language, language)
                system_prompt += f"\n\nIMPORTANT: Respond in {lang_name} language."
            user_prompt = self.prompt_manager.get_user_prompt("content_ideas", source_type, content)

            if not system_prompt or not user_prompt:
                logger.error("Failed to get prompts for content ideas generation")
                return None

            response = await self.ai_provider.get_response(
                message=user_prompt,
                user_id=user_id,
                system_prompt=system_prompt
            )

            return response

        except Exception as e:
            logger.error(f"Error generating content ideas: {e}")
            return None

    async def generate_blog_post(self, content: str, source_type: str, user_id: int, language: str = "en") -> Optional[str]:
        """Generate an SEO-optimized blog post and YouTube video script from the content."""
        try:
            system_prompt = self.prompt_manager.get_system_prompt("blog_post", source_type)
            if language != "en":
                language_names = {"ru": "Russian", "es": "Spanish", "en": "English"}
                lang_name = language_names.get(language, language)
                system_prompt += f"\n\nIMPORTANT: Respond in {lang_name} language."
            user_prompt = self.prompt_manager.get_user_prompt("blog_post", source_type, content)

            if not system_prompt or not user_prompt:
                logger.error("Failed to get prompts for blog post generation")
                return None

            response = await self.ai_provider.get_response(
                message=user_prompt,
                user_id=user_id,
                system_prompt=system_prompt
            )

            return response

        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            return None

    async def process_content(self, content: str, processing_type: str, source_type: str, user_id: int, language: str = "en") -> Optional[str]:
        """Process content based on the specified processing type."""
        try:
            if processing_type == "summary":
                return await self.generate_summary(content, source_type, user_id, language)
            elif processing_type == "mvp_plan":
                return await self.generate_mvp_plan(content, source_type, user_id, language)
            elif processing_type == "content_ideas":
                return await self.generate_content_ideas(content, source_type, user_id, language)
            elif processing_type == "blog_post":
                return await self.generate_blog_post(content, source_type, user_id, language)
            else:
                logger.error(f"Unknown processing type: {processing_type}")
                return None

        except Exception as e:
            logger.error(f"Error processing content: {e}")
            return None

    def get_available_processing_types(self) -> list:
        """Get list of available processing types from prompt manager."""
        return self.prompt_manager.get_all_processing_types()

    def validate_prompts(self) -> dict:
        """Validate that all required prompts are available."""
        return self.prompt_manager.validate_prompts()

    def reload_prompts(self) -> None:
        """Reload prompts from configuration file."""
        self.prompt_manager.reload_prompts()

    def get_processing_config(self) -> dict:
        """Get processing configuration from prompt manager."""
        return self.prompt_manager.get_processing_config()

    def get_prompts_info(self) -> dict:
        """Get information about loaded prompts."""
        return self.prompt_manager.get_prompts_info()

    async def process_content_with_user_prompt(self, content: str, processing_type: str, source_type: str,
                                             user_id: int, user_prompt: Optional[str] = None, language: str = "en") -> Optional[str]:
        """Process content with optional custom user prompt."""
        try:
            logger.info(f"Processing content with type: {processing_type}, source: {source_type}")
            
            system_prompt = self.prompt_manager.get_system_prompt(processing_type, source_type)
            if language != "en":
                language_names = {"ru": "Russian", "es": "Spanish", "en": "English"}
                lang_name = language_names.get(language, language)
                system_prompt += f"\n\nIMPORTANT: Respond in {lang_name} language."
            base_user_prompt = self.prompt_manager.get_user_prompt(processing_type, source_type, content)

            if not system_prompt or not base_user_prompt:
                logger.error(f"Failed to get prompts for {processing_type} generation")
                return None

            # If user provided custom instructions, append them to the user prompt
            if user_prompt and user_prompt.strip():
                enhanced_user_prompt = f"{base_user_prompt}\n\nAdditional Instructions: {user_prompt.strip()}"
                logger.info(f"Added custom user instructions: {user_prompt.strip()}")
            else:
                enhanced_user_prompt = base_user_prompt

            response = await self.ai_provider.get_response(
                message=enhanced_user_prompt,
                user_id=user_id,
                system_prompt=system_prompt
            )

            return response

        except Exception as e:
            logger.error(f"Error processing content with user prompt: {e}", exc_info=True)
            return None
    
    async def process_combined_content(self, combined_data: Dict[str, Any], processing_type: str,
                                      user_id: int, user_prompt: Optional[str] = None, language: str = "en") -> Optional[str]:
        """Process combined content from multiple sources."""
        try:
            logger.info(f"Processing combined content from {combined_data['total_sources']} sources")

            # Create a formatted description of sources
            sources_description = "\n".join([
                f"- {source['description']}"
                for source in combined_data['sources']
            ])

            # Get prompts for combined processing
            system_prompt = self.prompt_manager.get_system_prompt(processing_type, "combined")
            if not system_prompt:
                # Fallback to generic system prompt
                system_prompt = self.prompt_manager.get_system_prompt(processing_type, "generic")

            # Add language instruction
            if language != "en":
                language_names = {"ru": "Russian", "es": "Spanish", "en": "English"}
                lang_name = language_names.get(language, language)
                system_prompt += f"\n\nIMPORTANT: Respond in {lang_name} language."

            # Prepare the combined content with clear source separation
            combined_text = combined_data['combined_text']

            # Create user prompt based on processing type
            if processing_type == "summary":
                base_prompt = f"""Please provide a comprehensive summary of the following {combined_data['total_sources']} sources:

{sources_description}

The content from all sources is provided below. Create a unified summary that captures the key points from all sources, noting any connections or contrasts between them.

{combined_text}"""
            elif processing_type == "mvp_plan":
                base_prompt = f"""Based on the following {combined_data['total_sources']} sources, create a detailed MVP plan:

{sources_description}

Analyze all the content below and create a comprehensive MVP plan that incorporates insights from all sources.

{combined_text}"""
            elif processing_type == "content_ideas":
                base_prompt = f"""Generate creative content ideas based on the following {combined_data['total_sources']} sources:

{sources_description}

Use the content from all sources below to generate innovative content ideas that combine themes and insights from multiple sources.

{combined_text}"""
            else:
                base_prompt = f"""Process the following {combined_data['total_sources']} sources:

{sources_description}

Content:
{combined_text}"""

            # Add custom user instructions if provided
            if user_prompt and user_prompt.strip():
                enhanced_prompt = f"{base_prompt}\n\nAdditional Instructions: {user_prompt.strip()}"
            else:
                enhanced_prompt = base_prompt

            response = await self.ai_provider.get_response(
                message=enhanced_prompt,
                user_id=user_id,
                system_prompt=system_prompt or "You are a helpful assistant that analyzes and processes multiple content sources."
            )

            # Add source attribution to the response
            if response:
                response = f"# Combined Analysis of {combined_data['total_sources']} Sources\n\n**Sources:**\n{sources_description}\n\n---\n\n{response}"

            return response

        except Exception as e:
            logger.error(f"Error processing combined content: {e}", exc_info=True)
            return None

    async def detect_language_and_generate_tags(
        self,
        text: str,
        existing_tags: list[str],
        user_id: int
    ) -> Dict[str, Any]:
        """Detect language and generate tags in a single AI call.

        Args:
            text: Content text to analyze (first 3000 chars)
            existing_tags: List of all existing tag names in the system
            user_id: User ID for AI provider

        Returns:
            Dict with 'language' (en/ru/es) and 'tags' (list of 3 tag names)
        """
        try:
            # Truncate text for analysis
            analysis_text = text[:3000] if len(text) > 3000 else text

            system_prompt = """You are a content analysis assistant. Your task is to:
1. Detect the primary language of the content (must be one of: en, ru, es)
2. Generate exactly 3 relevant tags for categorization

IMPORTANT:
- ALL TAGS MUST BE IN ENGLISH ONLY, regardless of the content language
- For tags, prefer reusing existing tags from the provided list (aim for 80% reuse)
- Only create new tags if existing ones don't fit well
- Tags should be lowercase, concise (1-3 words), and descriptive
- Language must be exactly: "en", "ru", or "es"

Respond ONLY with valid JSON in this exact format:
{
  "language": "en",
  "tags": ["tag1", "tag2", "tag3"]
}"""

            # Prepare existing tags list
            existing_tags_str = ", ".join(existing_tags[:100]) if existing_tags else "No existing tags yet"

            user_prompt = f"""Analyze this content and provide language detection + 3 tags.

EXISTING TAGS (prefer these): {existing_tags_str}

CONTENT TO ANALYZE:
{analysis_text}

Remember: Respond with ONLY valid JSON."""

            response = await self.ai_provider.get_response(
                message=user_prompt,
                user_id=user_id,
                system_prompt=system_prompt
            )

            if not response:
                logger.error("No response from AI for language/tag detection")
                return {"language": "en", "tags": ["content", "uncategorized", "unknown"]}

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from response (in case AI added extra text)
            json_match = re.search(r'\{[^{}]*"language"[^{}]*"tags"[^{}]*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response.strip()

            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON: {response}")
                return {"language": "en", "tags": ["content", "uncategorized", "unknown"]}

            # Validate and normalize result
            language = result.get("language", "en").lower()
            if language not in ["en", "ru", "es"]:
                logger.warning(f"Invalid language detected: {language}, defaulting to 'en'")
                language = "en"

            tags = result.get("tags", [])
            if not isinstance(tags, list) or len(tags) != 3:
                logger.warning(f"Invalid tags from AI: {tags}, using defaults")
                tags = ["content", "uncategorized", "unknown"]

            # Normalize tags (lowercase, strip)
            tags = [tag.strip().lower() for tag in tags if isinstance(tag, str) and tag.strip()]
            if len(tags) < 3:
                # Pad with generic tags if needed
                while len(tags) < 3:
                    if "content" not in tags:
                        tags.append("content")
                    elif "general" not in tags:
                        tags.append("general")
                    else:
                        tags.append("unknown")

            # Take only first 3 tags
            tags = tags[:3]

            logger.info(f"Detected language: {language}, Generated tags: {tags}")
            return {"language": language, "tags": tags}

        except Exception as e:
            logger.error(f"Error in language/tag detection: {e}", exc_info=True)
            return {"language": "en", "tags": ["content", "uncategorized", "error"]}