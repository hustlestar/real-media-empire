"""
Abstract base class for content providers.

Defines the interface for AI-powered content generation for presentations.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from ..models import (
    PresentationRequest,
    PresentationOutline,
    SlideDefinition,
    ContentGenerationResult,
    SlideContent,
)


# ============================================================================
# Exceptions
# ============================================================================


class ContentProviderError(Exception):
    """Base exception for content provider errors"""

    pass


class ContentGenerationError(ContentProviderError):
    """Error during content generation"""

    pass


class TokenLimitExceededError(ContentProviderError):
    """Token limit exceeded for model"""

    pass


class InvalidResponseError(ContentProviderError):
    """Invalid response format from AI"""

    pass


# ============================================================================
# Base Provider
# ============================================================================


class BaseContentProvider(ABC):
    """
    Abstract base class for AI content generation providers.

    Providers generate presentation outlines and detailed slide content
    based on user requests.
    """

    def __init__(self, api_key: str, model: str):
        """
        Initialize provider.

        Args:
            api_key: API key for the provider
            model: Model identifier to use
        """
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate_outline(self, request: PresentationRequest, max_tokens: Optional[int] = None) -> PresentationOutline:
        """
        Generate high-level presentation outline.

        Args:
            request: Presentation request with topic and parameters
            max_tokens: Maximum tokens to use (None = provider default)

        Returns:
            PresentationOutline with slide titles and structure

        Raises:
            ContentGenerationError: If generation fails
            TokenLimitExceededError: If token limit exceeded
        """
        pass

    @abstractmethod
    def generate_slide_content(
        self, request: PresentationRequest, outline: PresentationOutline, slide_number: int, slide_title: str, max_tokens: Optional[int] = None
    ) -> SlideDefinition:
        """
        Generate detailed content for a single slide.

        Args:
            request: Original presentation request
            outline: Overall presentation outline
            slide_number: Number of this slide (1-indexed)
            slide_title: Title of this slide from outline
            max_tokens: Maximum tokens to use

        Returns:
            SlideDefinition with complete content

        Raises:
            ContentGenerationError: If generation fails
        """
        pass

    @abstractmethod
    def generate_all_content(self, request: PresentationRequest, max_tokens_per_slide: Optional[int] = None) -> ContentGenerationResult:
        """
        Generate complete presentation content (outline + all slides).

        This is the main method for end-to-end generation.

        Args:
            request: Presentation request
            max_tokens_per_slide: Token limit per slide

        Returns:
            ContentGenerationResult with all slides and metadata

        Raises:
            ContentGenerationError: If generation fails
        """
        pass

    @abstractmethod
    def estimate_cost(self, request: PresentationRequest) -> Decimal:
        """
        Estimate cost for generating presentation content.

        Args:
            request: Presentation request

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text for this provider's tokenizer.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        pass

    def fit_content_to_constraints(self, content: SlideContent, max_bullets: int = 5, max_chars_per_bullet: int = 100) -> SlideContent:
        """
        Ensure content fits within slide constraints.

        Default implementation truncates bullets and text.
        Providers can override for more intelligent fitting.

        Args:
            content: Original slide content
            max_bullets: Maximum bullets per slide
            max_chars_per_bullet: Maximum characters per bullet

        Returns:
            Fitted SlideContent
        """
        fitted = content.model_copy(deep=True)

        # Truncate bullets
        if len(fitted.bullets) > max_bullets:
            fitted.bullets = fitted.bullets[:max_bullets]

        # Truncate bullet text
        for bullet in fitted.bullets:
            if len(bullet.text) > max_chars_per_bullet:
                bullet.text = bullet.text[: max_chars_per_bullet - 3] + "..."

        # Truncate text content
        max_text_chars = max_bullets * max_chars_per_bullet
        if fitted.text_content and len(fitted.text_content) > max_text_chars:
            fitted.text_content = fitted.text_content[: max_text_chars - 3] + "..."

        return fitted
