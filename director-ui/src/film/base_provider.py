"""Base classes for video generation providers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Base configuration for video providers."""
    pass


class VideoGenerationResult(BaseModel):
    """Result from video generation."""
    video_url: str = Field(..., description="URL to the generated video")
    provider: str = Field(..., description="Provider name (e.g., 'heygen', 'minimax')")
    cost: float = Field(default=0.0, description="Generation cost in USD")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class VideoProvider(ABC):
    """Abstract base class for video generation providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def generate(self, *args, **kwargs) -> VideoGenerationResult:
        """Generate video. Implementation depends on provider."""
        pass

    async def close(self):
        """Clean up resources. Override if needed."""
        pass
