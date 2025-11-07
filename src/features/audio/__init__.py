"""
Audio Features Module

Provides audio generation and processing capabilities:
- Voice cloning and management (ElevenLabs Voice Lab)
- Brand voice consistency
- Content-optimized speech synthesis
"""

from features.audio.voice_cloning import (
    VoiceCloner,
    VoiceSettings,
    Voice,
    clone_voice,
    generate_speech,
)

__all__ = [
    "VoiceCloner",
    "VoiceSettings",
    "Voice",
    "clone_voice",
    "generate_speech",
]
