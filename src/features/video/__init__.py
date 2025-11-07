"""Video processing features"""

from .subtitles import (
    SubtitleGenerator,
    SubtitleStyle,
    add_subtitles_from_text,
    add_subtitles_to_video
)

from .formatter import (
    PlatformVideoFormatter,
    PlatformSpecs,
    Platform,
    format_video_for_platforms
)

__all__ = [
    # Subtitles
    'SubtitleGenerator',
    'SubtitleStyle',
    'add_subtitles_from_text',  # Primary method - FREE!
    'add_subtitles_to_video',   # Fallback - costs money

    # Platform formatter
    'PlatformVideoFormatter',
    'PlatformSpecs',
    'Platform',
    'format_video_for_platforms'
]
