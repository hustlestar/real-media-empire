"""
World-class cinematic prompt system.
Written from the perspective of a professional film producer and director.
"""

from .builder import CinematicPromptBuilder
from .styles import CINEMATIC_STYLES, CinematicStyle
from .shot_types import SHOT_COMPOSITIONS, ShotComposition
from .lighting import LIGHTING_SETUPS, LightingSetup
from .emotions import EMOTIONAL_BEATS, EmotionalBeat

__all__ = [
    "CinematicPromptBuilder",
    "CINEMATIC_STYLES",
    "CinematicStyle",
    "SHOT_COMPOSITIONS",
    "ShotComposition",
    "LIGHTING_SETUPS",
    "LightingSetup",
    "EMOTIONAL_BEATS",
    "EmotionalBeat",
]
