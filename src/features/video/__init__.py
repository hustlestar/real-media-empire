"""Video processing features"""

from .subtitles import (
    SubtitleGenerator,
    SubtitleStyle,
    add_subtitles_from_text,
    add_subtitles_to_video
)

__all__ = [
    'SubtitleGenerator',
    'SubtitleStyle',
    'add_subtitles_from_text',  # Primary method - FREE!
    'add_subtitles_to_video'     # Fallback - costs money
]
