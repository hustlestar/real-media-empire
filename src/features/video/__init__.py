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

from .hook_optimizer import (
    HookOptimizer,
    HookScore,
    analyze_hook,
    compare_hooks
)

from .thumbnail_generator import (
    ThumbnailGenerator,
    ThumbnailScore,
    create_thumbnail
)

from .smart_cropping import (
    SmartCropper,
    smart_crop_video
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
    'format_video_for_platforms',

    # Hook optimizer
    'HookOptimizer',
    'HookScore',
    'analyze_hook',
    'compare_hooks',

    # Thumbnail generator
    'ThumbnailGenerator',
    'ThumbnailScore',
    'create_thumbnail',

    # Smart cropping
    'SmartCropper',
    'smart_crop_video'
]
