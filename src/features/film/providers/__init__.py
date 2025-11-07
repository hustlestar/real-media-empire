"""
Provider abstractions for film generation.

Implements the Strategy pattern for swappable image/video/audio generators.
"""

from film.providers.base import (
    BaseImageProvider,
    BaseVideoProvider,
    BaseAudioProvider,
)

__all__ = [
    "BaseImageProvider",
    "BaseVideoProvider",
    "BaseAudioProvider",
]
