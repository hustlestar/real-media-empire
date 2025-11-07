"""YouTube transcript extractor implementations."""

import logging
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from processors.youtube_transcript_base import YouTubeTranscriptExtractor

logger = logging.getLogger(__name__)


class YouTubeTranscriptApiExtractor(YouTubeTranscriptExtractor):
    """Extractor using youtube-transcript-api library."""

    def get_name(self) -> str:
        return "youtube-transcript-api"

    async def extract_transcript(self, url: str, video_id: str) -> Optional[str]:
        """Extract transcript using youtube-transcript-api."""
        try:
            logger.info(f"[{self.get_name()}] Attempting extraction for video {video_id}")

            # First, try to list all available transcripts
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                logger.info(f"[{self.get_name()}] Available transcripts: {[t.language_code for t in transcript_list]}")

                # Try manual transcripts first (better quality)
                for transcript in transcript_list:
                    if not transcript.is_generated:
                        try:
                            fetched = transcript.fetch()
                            text = ' '.join([item['text'] for item in fetched])
                            logger.info(f"[{self.get_name()}] Success with manual transcript: {transcript.language_code}")
                            return text.strip()
                        except Exception:
                            continue

                # Then try auto-generated in preferred languages
                languages = ['en', 'en-US', 'en-GB', 'ru', 'es']
                for transcript in transcript_list:
                    if transcript.is_generated and transcript.language_code in languages:
                        try:
                            fetched = transcript.fetch()
                            text = ' '.join([item['text'] for item in fetched])
                            logger.info(f"[{self.get_name()}] Success with auto-generated: {transcript.language_code}")
                            return text.strip()
                        except Exception:
                            continue

                # Finally, try any available transcript
                for transcript in transcript_list:
                    try:
                        fetched = transcript.fetch()
                        text = ' '.join([item['text'] for item in fetched])
                        logger.info(f"[{self.get_name()}] Success with any transcript: {transcript.language_code}")
                        return text.strip()
                    except Exception:
                        continue

            except Exception as list_error:
                logger.debug(f"Could not list transcripts: {list_error}")

                # Fallback to old method
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    if transcript_list:
                        transcript = ' '.join([item['text'] for item in transcript_list])
                        logger.info(f"[{self.get_name()}] Success with direct get_transcript")
                        return transcript.strip()
                except Exception:
                    pass

            logger.warning(f"[{self.get_name()}] Failed to extract transcript")
            return None

        except Exception as e:
            logger.error(f"[{self.get_name()}] Error: {e}")
            return None


class PytubeExtractor(YouTubeTranscriptExtractor):
    """Extractor using pytube library."""

    def get_name(self) -> str:
        return "pytube"

    async def extract_transcript(self, url: str, video_id: str) -> Optional[str]:
        """Extract transcript using pytube."""
        try:
            logger.info(f"[{self.get_name()}] Attempting extraction for {url}")

            yt = YouTube(url)
            captions = yt.captions

            # Try English captions
            caption_codes = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU', 'a.en']

            for code in caption_codes:
                if code in captions:
                    caption = captions[code]
                    transcript = caption.generate_srt_captions()
                    cleaned = self._clean_srt_content(transcript)
                    if cleaned and len(cleaned.strip()) > 50:
                        logger.info(f"[{self.get_name()}] Success with caption: {code}")
                        return cleaned

            # Try any available caption
            for caption_code, caption in captions.items():
                try:
                    transcript = caption.generate_srt_captions()
                    cleaned = self._clean_srt_content(transcript)
                    if cleaned and len(cleaned.strip()) > 50:
                        logger.info(f"[{self.get_name()}] Success with caption: {caption_code}")
                        return cleaned
                except Exception:
                    continue

            logger.warning(f"[{self.get_name()}] Failed to extract transcript")
            return None

        except Exception as e:
            logger.error(f"[{self.get_name()}] Error: {e}")
            return None

    def _clean_srt_content(self, content: str) -> str:
        """Clean SRT subtitle format."""
        import re
        lines = content.split('\n')
        text_lines = []

        for line in lines:
            line = line.strip()
            # Skip timestamps, numbers, and empty lines
            if (not line or
                '-->' in line or
                line.isdigit() or
                re.match(r'^\d{2}:\d{2}:\d{2}', line)):
                continue

            # Remove HTML tags
            line = re.sub(r'<[^>]+>', '', line)

            if line and line not in text_lines:
                text_lines.append(line)

        return ' '.join(text_lines)


class YtDlpExtractor(YouTubeTranscriptExtractor):
    """Extractor using yt-dlp library."""

    def get_name(self) -> str:
        return "yt-dlp"

    async def extract_transcript(self, url: str, video_id: str) -> Optional[str]:
        """Extract transcript using yt-dlp."""
        try:
            logger.info(f"[{self.get_name()}] Attempting extraction for {url}")

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                ydl_opts = {
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en', 'en-US', 'en-GB', 'ru', 'es'],
                    'skip_download': True,
                    'outtmpl': str(temp_path / '%(title)s.%(ext)s'),
                    'ignoreerrors': True,
                    'no_warnings': True,
                    'quiet': True,
                    # Add options to bypass bot detection
                    'no_check_certificate': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'referer': 'https://www.youtube.com/',
                    'extract_flat': False,
                    # Don't specify format when skip_download is True
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Look for subtitle files
                subtitle_files = list(temp_path.glob('*.vtt')) + list(temp_path.glob('*.srt'))

                if subtitle_files:
                    subtitle_file = subtitle_files[0]
                    with open(subtitle_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    cleaned = self._clean_vtt_content(content)
                    if cleaned and len(cleaned.strip()) > 50:
                        logger.info(f"[{self.get_name()}] Success with file: {subtitle_file.name}")
                        return cleaned

            logger.warning(f"[{self.get_name()}] Failed to extract transcript")
            return None

        except Exception as e:
            logger.error(f"[{self.get_name()}] Error: {e}")
            return None

    def _clean_vtt_content(self, content: str) -> str:
        """Clean VTT/SRT subtitle format."""
        import re
        lines = content.split('\n')
        text_lines = []

        for line in lines:
            line = line.strip()

            # Skip headers, timestamps, and empty lines
            if (not line or
                line.startswith('WEBVTT') or
                '-->' in line or
                line.isdigit() or
                re.match(r'^\d{2}:\d{2}:\d{2}', line)):
                continue

            # Remove HTML tags and timestamps
            line = re.sub(r'<[^>]+>', '', line)
            line = re.sub(r'\d{2}:\d{2}:\d{2},\d{3}', '', line)

            if line and line not in text_lines:
                text_lines.append(line)

        return ' '.join(text_lines)