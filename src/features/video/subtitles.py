"""
Automated subtitle/caption generation system with viral styles.

This module provides subtitle generation for AI-generated videos where you
already have the script/text. Supports multiple viral caption styles
(TikTok, Instagram, Mr Beast, etc.).

Primary use case: Add subtitles when you have the text (AI-generated videos)
Fallback: Use Whisper transcription for videos without text
"""

import os
import tempfile
from typing import List, Dict, Literal, Optional
from dataclasses import dataclass
from pathlib import Path
import json
import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    from moviepy.video.fx.all import fadein, fadeout
except ImportError:
    VideoFileClip = TextClip = CompositeVideoClip = None
    fadein = fadeout = None

logger = logging.getLogger(__name__)

SubtitleStyle = Literal["tiktok", "instagram", "mr_beast", "minimal", "professional"]


@dataclass
class Word:
    """Represents a transcribed word with timing"""
    text: str
    start: float
    end: float


@dataclass
class SubtitleSegment:
    """Represents a subtitle segment"""
    text: str
    start: float
    end: float
    words: List[Word]


class SubtitleStyleConfig:
    """Configuration for different subtitle styles"""

    STYLES = {
        "tiktok": {
            "fontsize": 70,
            "font": "Impact",
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 3,
            "bg_color": None,
            "position": ("center", 0.75),  # 75% down the screen
            "method": "caption",
            "align": "center",
            "size": (800, None),
            "interline": -5,  # Tighter line spacing
        },
        "instagram": {
            "fontsize": 60,
            "font": "Montserrat-Bold",
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 2,
            "bg_color": (0, 0, 0, 128),  # Semi-transparent black
            "position": ("center", 0.70),
            "method": "caption",
            "align": "center",
            "size": (750, None),
            "interline": 0,
        },
        "mr_beast": {
            "fontsize": 80,
            "font": "Impact",
            "color": "yellow",
            "stroke_color": "black",
            "stroke_width": 4,
            "bg_color": None,
            "position": ("center", 0.5),  # Center of screen
            "method": "caption",
            "align": "center",
            "size": (850, None),
            "interline": -10,
        },
        "minimal": {
            "fontsize": 50,
            "font": "Helvetica",
            "color": "white",
            "stroke_color": None,
            "stroke_width": 0,
            "bg_color": (0, 0, 0, 180),
            "position": ("center", 0.85),  # Near bottom
            "method": "caption",
            "align": "center",
            "size": (700, None),
            "interline": 5,
        },
        "professional": {
            "fontsize": 45,
            "font": "Arial",
            "color": "white",
            "stroke_color": None,
            "stroke_width": 0,
            "bg_color": (0, 0, 0, 200),
            "position": ("center", 0.90),  # Bottom
            "method": "caption",
            "align": "center",
            "size": (1000, None),
            "interline": 3,
        }
    }

    @classmethod
    def get_style(cls, style: SubtitleStyle) -> dict:
        """Get style configuration"""
        return cls.STYLES.get(style, cls.STYLES["tiktok"])


class SubtitleGenerator:
    """
    Generate and burn-in subtitles with viral styles.

    Features:
    - Automatic transcription using OpenAI Whisper
    - Multiple viral caption styles (TikTok, Instagram, Mr Beast, etc.)
    - Word-level timing for precision
    - Keyword highlighting
    - Customizable styling

    Example:
        >>> generator = SubtitleGenerator()
        >>> output = generator.add_subtitles(
        ...     video_path="input.mp4",
        ...     output_path="output.mp4",
        ...     style="tiktok",
        ...     highlight_keywords=True
        ... )
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize subtitle generator.

        Args:
            api_key: OpenAI API key (optional, only needed for Whisper transcription)
        """
        if VideoFileClip is None:
            raise ImportError("moviepy package required. Install: uv add moviepy")

        # OpenAI client is optional - only needed for Whisper transcription
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if api_key and OpenAI is not None:
            self.client = OpenAI(api_key=api_key)
            self.model = "whisper-1"
        else:
            self.client = None
            self.model = None

    def create_timing_from_text(
        self,
        text: str,
        audio_duration: float
    ) -> List[Word]:
        """
        Create word timing from text and audio duration (no transcription needed).

        Use this when you already have the script text and know the audio duration.
        Perfect for AI-generated videos where you have the original text.

        Args:
            text: The script text
            audio_duration: Duration of audio in seconds

        Returns:
            List of Word objects with estimated timing

        Example:
            >>> generator = SubtitleGenerator()
            >>> words = generator.create_timing_from_text(
            ...     text="Hello world, this is amazing content!",
            ...     audio_duration=5.0
            ... )
        """
        # Split text into words
        words_list = text.split()
        word_count = len(words_list)

        if word_count == 0:
            return []

        # Calculate time per word
        time_per_word = audio_duration / word_count

        # Create Word objects with evenly distributed timing
        words = []
        current_time = 0.0

        for word_text in words_list:
            # Adjust duration based on word length (longer words get more time)
            word_duration = time_per_word * (len(word_text) / 5.0)  # Assume 5 chars is average
            word_duration = max(0.2, min(word_duration, 2.0))  # Clamp between 0.2-2.0 seconds

            words.append(Word(
                text=word_text,
                start=current_time,
                end=current_time + word_duration
            ))

            current_time += word_duration

        # Normalize to fit exact duration
        if current_time != audio_duration and words:
            scale_factor = audio_duration / current_time
            for word in words:
                word.start *= scale_factor
                word.end *= scale_factor

        logger.info(f"Created timing for {len(words)} words over {audio_duration:.2f}s")
        return words

    def transcribe_video(
        self,
        video_path: str,
        language: str = "en"
    ) -> List[Word]:
        """
        Transcribe video using Whisper with word-level timestamps.

        NOTE: Only use this if you don't have the original text.
        If you generated the video and have the script, use create_timing_from_text() instead.

        Args:
            video_path: Path to video file
            language: Language code (e.g., 'en', 'es', 'fr')

        Returns:
            List of Word objects with text and timing
        """
        if self.client is None:
            raise ValueError(
                "Whisper transcription requires OpenAI API key. "
                "Set OPENAI_API_KEY environment variable, or use create_timing_from_text() "
                "if you already have the script text."
            )

        logger.info(f"Transcribing video with Whisper: {video_path}")

        # Extract audio from video
        video = VideoFileClip(video_path)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            audio_path = temp_audio.name
            video.audio.write_audiofile(audio_path, logger=None)

        try:
            # Transcribe with Whisper
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"],
                    language=language if language != "auto" else None
                )

            # Convert to Word objects
            words = []
            if hasattr(transcript, 'words') and transcript.words:
                for word_data in transcript.words:
                    words.append(Word(
                        text=word_data.word.strip(),
                        start=word_data.start,
                        end=word_data.end
                    ))

            logger.info(f"Transcribed {len(words)} words")
            return words

        finally:
            # Cleanup temp file
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            video.close()

    def group_words_into_segments(
        self,
        words: List[Word],
        max_words_per_line: int = 5,
        max_duration: float = 3.0
    ) -> List[SubtitleSegment]:
        """
        Group words into subtitle segments.

        Args:
            words: List of Word objects
            max_words_per_line: Maximum words per subtitle line
            max_duration: Maximum duration per subtitle (seconds)

        Returns:
            List of SubtitleSegment objects
        """
        segments = []
        current_words = []
        segment_start = None

        for word in words:
            if segment_start is None:
                segment_start = word.start

            current_words.append(word)

            # Check if we should create a segment
            duration = word.end - segment_start
            should_segment = (
                len(current_words) >= max_words_per_line or
                duration >= max_duration
            )

            if should_segment:
                segments.append(SubtitleSegment(
                    text=' '.join([w.text for w in current_words]),
                    start=segment_start,
                    end=word.end,
                    words=current_words.copy()
                ))
                current_words = []
                segment_start = None

        # Add remaining words
        if current_words:
            segments.append(SubtitleSegment(
                text=' '.join([w.text for w in current_words]),
                start=segment_start,
                end=current_words[-1].end,
                words=current_words
            ))

        return segments

    def highlight_keywords(self, text: str) -> str:
        """
        Highlight important keywords in text.

        Args:
            text: Input text

        Returns:
            Text with highlighted keywords (uppercase)
        """
        keywords = [
            'amazing', 'incredible', 'crazy', 'shocking', 'must',
            'never', 'always', 'secret', 'wow', 'unbelievable',
            'insane', 'perfect', 'best', 'worst', 'love', 'hate',
            'urgent', 'important', 'critical', 'warning'
        ]

        words = text.split()
        highlighted_words = []

        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            if word_lower in keywords:
                highlighted_words.append(word.upper())
            else:
                highlighted_words.append(word)

        return ' '.join(highlighted_words)

    def create_subtitle_clip(
        self,
        segment: SubtitleSegment,
        style: SubtitleStyle,
        video_size: tuple,
        highlight: bool = True
    ) -> TextClip:
        """
        Create a subtitle clip with styling.

        Args:
            segment: SubtitleSegment object
            style: Style name
            video_size: (width, height) of video
            highlight: Whether to highlight keywords

        Returns:
            TextClip object
        """
        style_config = SubtitleStyleConfig.get_style(style)

        # Prepare text
        text = segment.text
        if highlight:
            text = self.highlight_keywords(text)

        # Create text clip
        txt_clip = TextClip(
            txt=text,
            fontsize=style_config["fontsize"],
            font=style_config["font"],
            color=style_config["color"],
            stroke_color=style_config["stroke_color"],
            stroke_width=style_config["stroke_width"],
            method=style_config["method"],
            align=style_config["align"],
            size=style_config["size"],
            interline=style_config.get("interline", 0),
            bg_color=style_config["bg_color"]
        )

        # Set timing
        duration = segment.end - segment.start
        txt_clip = txt_clip.set_start(segment.start).set_duration(duration)

        # Set position
        position = style_config["position"]
        if isinstance(position, tuple):
            # Convert percentage to pixels if needed
            x, y = position
            if isinstance(y, float):
                y = int(video_size[1] * y)
            position = (x, y)

        txt_clip = txt_clip.set_position(position)

        # Add fade effects
        txt_clip = txt_clip.crossfadein(0.1).crossfadeout(0.1)

        return txt_clip

    def add_subtitles_from_text(
        self,
        video_path: str,
        text: str,
        output_path: str,
        style: SubtitleStyle = "tiktok",
        highlight_keywords: bool = True,
        max_words_per_line: int = 5
    ) -> str:
        """
        Add burned-in subtitles to video using pre-existing text (NO API COST).

        Use this method when you already have the script text (AI-generated videos).
        This is FREE - no Whisper API calls needed!

        Args:
            video_path: Input video path
            text: The script text (what's spoken in the video)
            output_path: Output video path
            style: Caption style (tiktok, instagram, mr_beast, minimal, professional)
            highlight_keywords: Whether to highlight important words
            max_words_per_line: Maximum words per subtitle line

        Returns:
            Path to output video

        Example:
            >>> generator = SubtitleGenerator()
            >>> output = generator.add_subtitles_from_text(
            ...     video_path="generated_video.mp4",
            ...     text="Welcome to my channel! This is amazing content.",
            ...     output_path="output.mp4",
            ...     style="tiktok"
            ... )

        Cost: FREE (no API calls)
        Performance: 2-3 minutes for 10-minute video
        """
        logger.info(f"Adding subtitles from text: {video_path} -> {output_path}")
        logger.info(f"Style: {style}, Text length: {len(text)} chars")

        # Load video
        video = VideoFileClip(video_path)
        video_size = video.size

        # Get audio duration
        audio_duration = video.audio.duration if video.audio else video.duration

        # Create timing from text
        words = self.create_timing_from_text(text, audio_duration)

        if not words:
            logger.warning("No words in text, returning original video")
            video.write_videofile(output_path)
            return output_path

        # Group into segments
        segments = self.group_words_into_segments(words, max_words_per_line)

        logger.info(f"Created {len(segments)} subtitle segments")

        # Create subtitle clips
        subtitle_clips = []
        for segment in segments:
            try:
                clip = self.create_subtitle_clip(
                    segment=segment,
                    style=style,
                    video_size=video_size,
                    highlight=highlight_keywords
                )
                subtitle_clips.append(clip)
            except Exception as e:
                logger.error(f"Error creating subtitle clip: {e}")
                continue

        # Composite video with subtitles
        final = CompositeVideoClip([video] + subtitle_clips)

        # Write output
        final.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
            logger=None
        )

        logger.info(f"Subtitles added successfully: {output_path}")

        # Cleanup
        video.close()
        final.close()

        return output_path

    def add_subtitles(
        self,
        video_path: str,
        output_path: str,
        style: SubtitleStyle = "tiktok",
        highlight_keywords: bool = True,
        max_words_per_line: int = 5,
        language: str = "en"
    ) -> str:
        """
        Add burned-in subtitles to video using Whisper transcription (COSTS MONEY).

        NOTE: Only use this if you don't have the original text.
        If you generated the video and have the script, use add_subtitles_from_text() instead!

        This method transcribes the video using Whisper API which costs $0.006/minute.

        Args:
            video_path: Input video path
            output_path: Output video path
            style: Caption style (tiktok, instagram, mr_beast, minimal, professional)
            highlight_keywords: Whether to highlight important words
            max_words_per_line: Maximum words per subtitle line
            language: Language code for transcription

        Returns:
            Path to output video

        Example:
            >>> generator = SubtitleGenerator()
            >>> output = generator.add_subtitles(
            ...     video_path="input.mp4",
            ...     output_path="output.mp4",
            ...     style="tiktok",
            ...     highlight_keywords=True
            ... )
        """
        logger.info(f"Adding subtitles: {video_path} -> {output_path}")
        logger.info(f"Style: {style}, Highlight: {highlight_keywords}")

        # Load video
        video = VideoFileClip(video_path)
        video_size = video.size

        # Transcribe
        words = self.transcribe_video(video_path, language)

        if not words:
            logger.warning("No words transcribed, returning original video")
            video.write_videofile(output_path)
            return output_path

        # Group into segments
        segments = self.group_words_into_segments(words, max_words_per_line)

        logger.info(f"Created {len(segments)} subtitle segments")

        # Create subtitle clips
        subtitle_clips = []
        for segment in segments:
            try:
                clip = self.create_subtitle_clip(
                    segment=segment,
                    style=style,
                    video_size=video_size,
                    highlight=highlight_keywords
                )
                subtitle_clips.append(clip)
            except Exception as e:
                logger.error(f"Error creating subtitle clip: {e}")
                continue

        # Composite video with subtitles
        final = CompositeVideoClip([video] + subtitle_clips)

        # Write output
        final.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=video.fps,
            logger=None
        )

        logger.info(f"Subtitles added successfully: {output_path}")

        # Cleanup
        video.close()
        final.close()

        return output_path

    def export_transcript(
        self,
        video_path: str,
        output_path: str,
        format: Literal["srt", "vtt", "json", "txt"] = "srt"
    ) -> str:
        """
        Export transcript in various formats.

        Args:
            video_path: Input video path
            output_path: Output transcript path
            format: Output format (srt, vtt, json, txt)

        Returns:
            Path to output transcript
        """
        words = self.transcribe_video(video_path)
        segments = self.group_words_into_segments(words)

        if format == "srt":
            self._export_srt(segments, output_path)
        elif format == "vtt":
            self._export_vtt(segments, output_path)
        elif format == "json":
            self._export_json(segments, output_path)
        elif format == "txt":
            self._export_txt(segments, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path

    def _export_srt(self, segments: List[SubtitleSegment], output_path: str):
        """Export as SRT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = self._format_srt_time(segment.start)
                end_time = self._format_srt_time(segment.end)
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment.text}\n\n")

    def _export_vtt(self, segments: List[SubtitleSegment], output_path: str):
        """Export as WebVTT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                start_time = self._format_vtt_time(segment.start)
                end_time = self._format_vtt_time(segment.end)
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment.text}\n\n")

    def _export_json(self, segments: List[SubtitleSegment], output_path: str):
        """Export as JSON format"""
        data = {
            "segments": [
                {
                    "text": seg.text,
                    "start": seg.start,
                    "end": seg.end,
                    "words": [
                        {"text": w.text, "start": w.start, "end": w.end}
                        for w in seg.words
                    ]
                }
                for seg in segments
            ]
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_txt(self, segments: List[SubtitleSegment], output_path: str):
        """Export as plain text"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for segment in segments:
                f.write(f"{segment.text}\n")

    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_vtt_time(self, seconds: float) -> str:
        """Format time for VTT (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


# Convenience functions

def add_subtitles_from_text(
    video_path: str,
    text: str,
    output_path: str,
    style: SubtitleStyle = "tiktok",
    highlight_keywords: bool = True
) -> str:
    """
    Convenience function to add subtitles when you have the text (FREE - no API cost).

    Use this for AI-generated videos where you already have the script!

    Args:
        video_path: Input video path
        text: The script text
        output_path: Output video path
        style: Caption style
        highlight_keywords: Whether to highlight important words

    Returns:
        Path to output video

    Example:
        >>> from features.video.subtitles import add_subtitles_from_text
        >>> output = add_subtitles_from_text(
        ...     video_path="generated_video.mp4",
        ...     text="Welcome to my amazing content!",
        ...     output_path="output.mp4",
        ...     style="tiktok"
        ... )

    Cost: FREE (no API calls)
    """
    generator = SubtitleGenerator()  # No API key needed!
    return generator.add_subtitles_from_text(
        video_path=video_path,
        text=text,
        output_path=output_path,
        style=style,
        highlight_keywords=highlight_keywords
    )


def add_subtitles_to_video(
    video_path: str,
    output_path: str,
    style: SubtitleStyle = "tiktok",
    highlight_keywords: bool = True,
    api_key: Optional[str] = None
) -> str:
    """
    Convenience function to add subtitles using Whisper transcription (COSTS MONEY).

    Only use this if you don't have the original text!
    For AI-generated videos, use add_subtitles_from_text() instead (FREE).

    Args:
        video_path: Input video path
        output_path: Output video path
        style: Caption style
        highlight_keywords: Whether to highlight important words
        api_key: OpenAI API key (required)

    Returns:
        Path to output video

    Example:
        >>> from features.video.subtitles import add_subtitles_to_video
        >>> output = add_subtitles_to_video(
        ...     "input.mp4",
        ...     "output.mp4",
        ...     style="tiktok"
        ... )

    Cost: $0.006 per minute
    """
    generator = SubtitleGenerator(api_key=api_key)
    return generator.add_subtitles(
        video_path=video_path,
        output_path=output_path,
        style=style,
        highlight_keywords=highlight_keywords
    )
