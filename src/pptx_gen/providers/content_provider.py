"""
OpenAI-based content provider for presentation generation.

Uses GPT-4 or GPT-3.5 for generating presentation content.
"""

import json
import logging
from decimal import Decimal
from typing import List, Optional

from openai import OpenAI

from .base import (
    BaseContentProvider,
    ContentGenerationError,
    TokenLimitExceededError,
    InvalidResponseError,
)
from ..models import (
    PresentationRequest,
    PresentationOutline,
    SlideDefinition,
    SlideContent,
    BulletPoint,
    ContentGenerationResult,
    SlideLayout,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Cost Constants (as of 2025)
# ============================================================================

MODEL_COSTS = {
    # GPT-4 models (per 1M tokens)
    "gpt-4": {"input": Decimal("30.00"), "output": Decimal("60.00")},
    "gpt-4-turbo": {"input": Decimal("10.00"), "output": Decimal("30.00")},
    "gpt-4o": {"input": Decimal("5.00"), "output": Decimal("15.00")},
    "gpt-4o-mini": {"input": Decimal("0.150"), "output": Decimal("0.600")},
    # GPT-3.5 models (per 1M tokens)
    "gpt-3.5-turbo": {"input": Decimal("0.50"), "output": Decimal("1.50")},
}


# ============================================================================
# Prompt Templates
# ============================================================================

OUTLINE_PROMPT_TEMPLATE = """You are an expert presentation designer. Create a presentation outline based on the following:

Topic: {topic}
{brief_section}
Target Audience: {audience}
Number of Slides: {num_slides}
Tone: {tone}
{key_points_section}
{reference_content_section}
{additional_instructions_section}

Generate a JSON response with the following structure:
{{
    "title": "Main presentation title",
    "subtitle": "Optional subtitle",
    "slide_titles": ["Slide 1 title", "Slide 2 title", ...],
    "estimated_duration_minutes": 30
}}

Guidelines:
- Create engaging, clear slide titles
- Ensure logical flow from introduction to conclusion
- {include_title}
- {include_conclusion}
- Slide titles should be concise (max 10 words)

Return ONLY the JSON, no additional text."""

SLIDE_CONTENT_PROMPT_TEMPLATE = """You are an expert presentation content writer. Generate content for a presentation slide.

Presentation Context:
- Overall Topic: {topic}
- Target Audience: {audience}
- Tone: {tone}
{additional_instructions_section}

This Slide:
- Number: {slide_number} of {total_slides}
- Title: {slide_title}

Generate a JSON response with the following structure:
{{
    "title": "{slide_title}",
    "bullets": [
        {{"text": "Main point with **bold** text and *italic* text", "level": 0, "list_type": "bullet"}},
        {{"text": "Supporting detail", "level": 1, "list_type": "bullet"}},
        {{"text": "Another point with **emphasis**", "level": 0, "list_type": "bullet"}}
    ],
    "speaker_notes": "Additional context for the presenter",
    "image_placeholder": "Description of helpful visual (optional)"
}}

Guidelines:
- Use 3-5 main bullet points (level 0)
- Add 1-2 sub-bullets (level 1) for important points if needed
- Keep bullet text concise (max 100 chars each)
- Make content specific and actionable
- Use **bold** for emphasis on key words/phrases (2-3 per slide)
- Use *italic* for technical terms or subtle emphasis (1-2 per slide)
- Don't overuse formatting - only highlight truly important concepts
- Speaker notes should expand on bullets
- Suggest relevant visuals if applicable

LIST TYPE SELECTION:
- Use "numbered" for sequential steps, processes, rankings, or ordered items
- Use "bullet" for general points, features, benefits, or unordered items
- Examples of numbered: "Step-by-step guide", "Top 5 strategies", "Implementation phases"
- Examples of bullets: "Key features", "Benefits", "Characteristics", "Options"

FORMATTING RULES:
- **text** = bold (use for KEY CONCEPTS, important numbers, critical actions)
- *text* = italic (use for terms, definitions, subtle emphasis)
- Plain text for everything else
- list_type can be "bullet" or "numbered"

Return ONLY the JSON, no additional text."""


# ============================================================================
# OpenAI Content Provider
# ============================================================================


class OpenAIContentProvider(BaseContentProvider):
    """
    OpenAI GPT-based content provider.

    Generates presentation content using GPT-4 or GPT-3.5 models.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini for cost efficiency)
        """
        super().__init__(api_key, model)
        self.client = OpenAI(api_key=api_key)

        if model not in MODEL_COSTS:
            logger.warning(f"Unknown model {model}, cost estimation may be inaccurate")

    def generate_outline(self, request: PresentationRequest, max_tokens: Optional[int] = None) -> PresentationOutline:
        """Generate presentation outline using GPT."""
        try:
            # Build prompt
            brief_section = f"Brief: {request.brief}" if request.brief else ""
            key_points_section = ""
            if request.key_points:
                points = "\n".join(f"- {pt}" for pt in request.key_points)
                key_points_section = f"Key Points to Cover:\n{points}"

            reference_content_section = ""
            if request.reference_content:
                # Truncate if too long (keep first 2000 chars)
                ref_content = request.reference_content[:2000]
                if len(request.reference_content) > 2000:
                    ref_content += "\n... (truncated)"
                reference_content_section = f"Reference Content:\n{ref_content}"

            additional_instructions_section = ""
            if request.additional_instructions:
                additional_instructions_section = f"Additional Instructions:\n{request.additional_instructions}"

            prompt = OUTLINE_PROMPT_TEMPLATE.format(
                topic=request.topic,
                brief_section=brief_section,
                audience=request.target_audience or "general audience",
                num_slides=request.num_slides,
                tone=request.tone.value,
                key_points_section=key_points_section,
                reference_content_section=reference_content_section,
                additional_instructions_section=additional_instructions_section,
                include_title="Include a title slide" if request.include_title_slide else "No separate title slide needed",
                include_conclusion="Include a conclusion/summary slide" if request.include_conclusion else "No conclusion slide needed",
            )

            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert presentation designer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens or 1000,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content
            data = json.loads(content)

            outline = PresentationOutline(
                title=data["title"],
                subtitle=data.get("subtitle"),
                slide_titles=data["slide_titles"],
                estimated_duration_minutes=data.get("estimated_duration_minutes"),
            )

            logger.info(f"Generated outline with {outline.get_num_slides()} slides")
            return outline

        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate outline: {e}")

    def generate_slide_content(
        self, request: PresentationRequest, outline: PresentationOutline, slide_number: int, slide_title: str, max_tokens: Optional[int] = None
    ) -> SlideDefinition:
        """Generate content for a single slide using GPT."""
        try:
            additional_instructions_section = ""
            if request.additional_instructions:
                additional_instructions_section = f"- Additional Instructions: {request.additional_instructions}"

            prompt = SLIDE_CONTENT_PROMPT_TEMPLATE.format(
                topic=outline.title,
                audience=request.target_audience or "general audience",
                tone=request.tone.value,
                additional_instructions_section=additional_instructions_section,
                slide_number=slide_number,
                total_slides=outline.get_num_slides(),
                slide_title=slide_title,
            )

            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert presentation content writer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens or 800,
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content
            data = json.loads(content)

            # Create SlideContent
            from ..models import ListType

            bullets = [
                BulletPoint(text=b["text"], level=b.get("level", 0), list_type=ListType(b.get("list_type", "bullet")))
                for b in data.get("bullets", [])
            ]

            slide_content = SlideContent(
                title=data["title"], bullets=bullets, speaker_notes=data.get("speaker_notes"), image_placeholder=data.get("image_placeholder")
            )

            # Determine layout
            layout = SlideLayout.CONTENT
            if slide_number == 1 and request.include_title_slide:
                layout = SlideLayout.TITLE
            elif slide_content.image_placeholder:
                layout = SlideLayout.IMAGE_TEXT

            slide_def = SlideDefinition(
                slide_number=slide_number, layout_type=layout, content=slide_content, tags=[request.tone.value, request.topic[:50]]
            )

            return slide_def

        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate slide {slide_number}: {e}")

    def generate_all_content(self, request: PresentationRequest, max_tokens_per_slide: Optional[int] = None) -> ContentGenerationResult:
        """Generate complete presentation content."""
        try:
            # Step 1: Generate outline
            outline = self.generate_outline(request)

            # Step 2: Generate content for each slide
            slides = []
            total_tokens = 0

            for idx, slide_title in enumerate(outline.slide_titles, start=1):
                slide_def = self.generate_slide_content(
                    request=request, outline=outline, slide_number=idx, slide_title=slide_title, max_tokens=max_tokens_per_slide
                )
                slides.append(slide_def)

                # Estimate tokens used (rough approximation)
                total_tokens += self.count_tokens(slide_title) + 500  # Approx per slide

            # Calculate cost
            cost = self._calculate_cost(total_tokens, total_tokens // 2)

            result = ContentGenerationResult(slides=slides, outline=outline, tokens_used=total_tokens, cost_usd=cost, model_used=self.model)

            logger.info(f"Generated {len(slides)} slides, {total_tokens} tokens, ${cost}")
            return result

        except Exception as e:
            raise ContentGenerationError(f"Failed to generate presentation content: {e}")

    def estimate_cost(self, request: PresentationRequest) -> Decimal:
        """Estimate cost for generating presentation."""
        # Rough estimation: outline (1000 tokens) + slides (800 tokens each)
        estimated_input_tokens = 1000 + (request.num_slides * 400)
        estimated_output_tokens = 500 + (request.num_slides * 400)

        return self._calculate_cost(estimated_input_tokens, estimated_output_tokens)

    def count_tokens(self, text: str) -> int:
        """
        Approximate token count.

        OpenAI's tiktoken library would be more accurate, but this provides
        a reasonable approximation: ~4 characters per token.
        """
        return len(text) // 4

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate cost based on token usage."""
        if self.model not in MODEL_COSTS:
            # Use GPT-4o-mini as default for unknown models
            costs = MODEL_COSTS["gpt-4o-mini"]
        else:
            costs = MODEL_COSTS[self.model]

        input_cost = (Decimal(input_tokens) / Decimal("1000000")) * costs["input"]
        output_cost = (Decimal(output_tokens) / Decimal("1000000")) * costs["output"]

        return input_cost + output_cost


# ============================================================================
# Factory Function
# ============================================================================


def create_content_provider(provider: str = "openai", api_key: Optional[str] = None, model: Optional[str] = None) -> BaseContentProvider:
    """
    Factory function to create content providers.

    Args:
        provider: Provider name ('openai')
        api_key: API key (if None, read from environment)
        model: Model to use (if None, use provider default)

    Returns:
        Initialized content provider

    Raises:
        ValueError: If provider is unknown or API key missing
    """
    if provider == "openai":
        if api_key is None:
            from config import CONFIG

            api_key = CONFIG.get("OPEN_AI_API_KEY")
            if not api_key:
                raise ValueError("OPEN_AI_API_KEY not found in environment")

        model = model or "gpt-4o-mini"
        return OpenAIContentProvider(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")
