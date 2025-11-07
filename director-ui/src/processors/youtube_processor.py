"""YouTube video processing module with multiple transcript extractors."""

import logging
import re
from typing import Optional, List
from urllib.parse import urlparse, parse_qs

import yt_dlp

from processors.youtube_transcript_base import YouTubeTranscriptExtractor
from processors.youtube_extractors import (
    YouTubeTranscriptApiExtractor,
    PytubeExtractor,
    YtDlpExtractor
)

logger = logging.getLogger(__name__)


class YouTubeProcessor:
    """Handles YouTube video processing with fallback transcript extraction."""

    def __init__(self):
        """Initialize with multiple transcript extractors."""
        self.extractors: List[YouTubeTranscriptExtractor] = [
            YouTubeTranscriptApiExtractor(),  # Fastest and most reliable
            PytubeExtractor(),                 # Good fallback
            YtDlpExtractor(),                  # Last resort, downloads files
        ]

    @staticmethod
    def is_youtube_url(text: str) -> bool:
        """Check if the text is a YouTube URL."""
        youtube_patterns = [
            r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/',
            r'(?:https?:\/\/)?(?:m\.)?youtube\.com\/watch\?v='
        ]

        text = text.strip()
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in youtube_patterns)

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        try:
            # Handle different YouTube URL formats
            if 'youtu.be/' in url:
                return url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
            elif 'youtube.com/watch' in url:
                parsed = urlparse(url)
                return parse_qs(parsed.query).get('v', [None])[0]
            elif 'youtube.com/embed/' in url:
                return url.split('embed/')[-1].split('?')[0].split('&')[0]
            elif 'youtube.com/shorts/' in url:
                return url.split('shorts/')[-1].split('?')[0].split('&')[0]
            return None
        except Exception as e:
            logger.error(f"Error extracting video ID from {url}: {e}")
            return None

    async def extract_content_from_url(self, url: str) -> Optional[dict]:
        """Extract content from a YouTube URL."""
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.error("Could not extract video ID from URL")
                return None

            logger.info(f"Processing YouTube video: {video_id}")

            # Get basic video info
            video_info = await self._get_video_info(url)

            # Try transcript extraction with all extractors
            transcript = await self._extract_transcript_with_fallbacks(url, video_id)

            if transcript:
                logger.info(f"Successfully extracted transcript ({len(transcript)} characters)")
            else:
                logger.warning("All transcript extraction methods failed")

            return {
                'title': video_info.get('title', 'Unknown Title'),
                'description': video_info.get('description', ''),
                'duration': video_info.get('duration', 0),
                'transcript': transcript,
                'url': url,
                'video_id': video_id
            }

        except Exception as e:
            logger.error(f"Error extracting content from YouTube URL {url}: {e}")
            return None

    async def _get_video_info(self, url: str) -> dict:
        """Get basic video information using yt-dlp."""
        try:
            ydl_opts = {
                'extract_flat': False,
                'ignoreerrors': True,
                'no_warnings': True,
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    return {
                        'title': info.get('title', 'Unknown Title'),
                        'description': info.get('description', ''),
                        'duration': info.get('duration', 0),
                    }
        except Exception as e:
            logger.warning(f"Could not extract video info: {e}")

        return {'title': 'Unknown Title', 'description': '', 'duration': 0}

    async def _extract_transcript_with_fallbacks(self, url: str, video_id: str) -> Optional[str]:
        """Try all extractors in order until one succeeds."""
        for extractor in self.extractors:
            try:
                logger.info(f"Trying extractor: {extractor.get_name()}")
                transcript = await extractor.extract_transcript(url, video_id)

                if transcript and len(transcript.strip()) > 50:
                    logger.info(f"✅ Successfully extracted transcript with {extractor.get_name()}")
                    return transcript

            except Exception as e:
                logger.error(f"Extractor {extractor.get_name()} failed with exception: {e}")
                continue

        logger.error("❌ All transcript extractors failed")
        return None