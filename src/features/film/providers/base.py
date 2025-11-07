"""
Base classes for generation providers.

Defines common interfaces for image, video, and audio generation.
All providers must implement these interfaces for consistent usage.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from film.models import (
    ImageConfig,
    ImageResult,
    VideoConfig,
    VideoResult,
    AudioConfig,
    AudioResult,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Base Image Provider
# ============================================================================


class BaseImageProvider(ABC):
    """
    Abstract base class for image generation providers.

    All image providers (FAL, Replicate, etc.) must implement this interface.
    """

    def __init__(self, api_key: str, name: str):
        self.api_key = api_key
        self.name = name

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        config: ImageConfig,
    ) -> ImageResult:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Detailed description of desired image
            negative_prompt: What to avoid in the image
            config: Image generation configuration

        Returns:
            ImageResult with URL and metadata

        Raises:
            ProviderError: If generation fails
        """
        pass

    @abstractmethod
    def estimate_cost(self, config: ImageConfig) -> Decimal:
        """
        Estimate cost for generating an image with given config.

        Args:
            config: Image generation configuration

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    async def poll_status(self, status_url: str) -> dict:
        """
        Poll async generation status until complete.

        Args:
            status_url: Status endpoint URL

        Returns:
            Final result data

        Raises:
            TimeoutError: If polling exceeds max attempts
            ProviderError: If generation fails
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


# ============================================================================
# Base Video Provider
# ============================================================================


class BaseVideoProvider(ABC):
    """
    Abstract base class for video generation providers.

    All video providers (Minimax, Kling, Runway) must implement this interface.
    """

    def __init__(self, api_key: str, name: str):
        self.api_key = api_key
        self.name = name

    @abstractmethod
    async def generate(
        self,
        image_url: str,
        prompt: str,
        config: VideoConfig,
    ) -> VideoResult:
        """
        Animate an image into a video using a text prompt.

        Args:
            image_url: URL of source image to animate
            prompt: Motion/action description
            config: Video generation configuration

        Returns:
            VideoResult with URL and metadata

        Raises:
            ProviderError: If generation fails
        """
        pass

    @abstractmethod
    def estimate_cost(self, config: VideoConfig) -> Decimal:
        """
        Estimate cost for generating a video with given config.

        Args:
            config: Video generation configuration

        Returns:
            Estimated cost in USD
        """
        pass

    @abstractmethod
    async def poll_status(self, status_url: str) -> dict:
        """
        Poll async generation status until complete.

        Args:
            status_url: Status endpoint URL

        Returns:
            Final result data

        Raises:
            TimeoutError: If polling exceeds max attempts
            ProviderError: If generation fails
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


# ============================================================================
# Base Audio Provider
# ============================================================================


class BaseAudioProvider(ABC):
    """
    Abstract base class for audio synthesis providers.

    All TTS providers (OpenAI, ElevenLabs) must implement this interface.
    """

    def __init__(self, api_key: str, name: str):
        self.api_key = api_key
        self.name = name

    @abstractmethod
    async def generate(
        self,
        text: str,
        config: AudioConfig,
    ) -> AudioResult:
        """
        Synthesize speech from text.

        Args:
            text: Text to speak
            config: Audio synthesis configuration

        Returns:
            AudioResult with audio data and metadata

        Raises:
            ProviderError: If synthesis fails
        """
        pass

    @abstractmethod
    def estimate_cost(self, text: str, config: AudioConfig) -> Decimal:
        """
        Estimate cost for synthesizing given text.

        Args:
            text: Text to synthesize
            config: Audio configuration

        Returns:
            Estimated cost in USD
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


# ============================================================================
# Common Exceptions
# ============================================================================


class ProviderError(Exception):
    """Base exception for provider errors"""

    pass


class ProviderTimeoutError(ProviderError):
    """Raised when polling times out"""

    pass


class ProviderQuotaError(ProviderError):
    """Raised when API quota is exceeded"""

    pass


class ProviderAuthError(ProviderError):
    """Raised when authentication fails"""

    pass
