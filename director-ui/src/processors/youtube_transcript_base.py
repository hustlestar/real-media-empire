"""Base interface for YouTube transcript extractors."""

from abc import ABC, abstractmethod
from typing import Optional, Dict


class YouTubeTranscriptExtractor(ABC):
    """Abstract base class for YouTube transcript extraction."""

    @abstractmethod
    async def extract_transcript(self, url: str, video_id: str) -> Optional[str]:
        """
        Extract transcript from a YouTube video.

        Args:
            url: Full YouTube URL
            video_id: YouTube video ID

        Returns:
            Transcript text or None if extraction fails
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this extractor."""
        pass