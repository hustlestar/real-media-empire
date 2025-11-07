"""
Film Generation Module

A comprehensive system for generating cinematic films using AI:
- Image generation (FAL, Replicate)
- Video animation (Minimax, Kling, Runway)
- Audio synthesis (OpenAI TTS, ElevenLabs)
- Asset caching and reuse
- Cost tracking and budget management
- Rich metadata for asset discovery
"""

from .models import (
    ShotDefinition,
    ShotConfig,
    ImageConfig,
    VideoConfig,
    AudioConfig,
    AssetMetadata,
    FilmProject,
    CostEstimate,
)

__all__ = [
    "ShotDefinition",
    "ShotConfig",
    "ImageConfig",
    "VideoConfig",
    "AudioConfig",
    "AssetMetadata",
    "FilmProject",
    "CostEstimate",
]
