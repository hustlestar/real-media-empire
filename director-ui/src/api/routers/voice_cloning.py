"""
API endpoints for voice cloning and management.

Note: This router expects features.audio module to be importable.
If running from director-ui/, set PYTHONPATH to include src/:
    PYTHONPATH=../src uvicorn src.api.app:app --reload
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict
from enum import Enum

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Direct import - ensure PYTHONPATH includes src/
try:
    from features.audio.voice_cloning import VoiceCloner, VoiceSettings, Voice, ContentType
except ImportError:
    VoiceCloner = None


router = APIRouter(prefix="/api/voice", tags=["voice_cloning"])


# Request/Response Models

class VoiceSettingsModel(BaseModel):
    """Voice settings configuration"""
    stability: float = Field(0.5, ge=0.0, le=1.0, description="Voice stability (0=expressive, 1=stable)")
    similarity_boost: float = Field(0.75, ge=0.0, le=1.0, description="Similarity to original voice")
    style: float = Field(0.0, ge=0.0, le=1.0, description="Style exaggeration (v2 models)")
    use_speaker_boost: bool = Field(True, description="Boost similarity to speaker")


class VoiceModel(BaseModel):
    """Voice information"""
    voice_id: str
    name: str
    category: str
    description: str = ""
    labels: Dict[str, str] = {}
    sample_count: int = 0


class VoiceListResponse(BaseModel):
    """Response for voice listing"""
    voices: List[VoiceModel]
    total: int


class VoiceCloneResponse(BaseModel):
    """Response for voice cloning"""
    success: bool
    message: str
    voice_id: Optional[str] = None
    voice_name: Optional[str] = None


class SpeechGenerateResponse(BaseModel):
    """Response for speech generation"""
    success: bool
    message: str
    output_path: Optional[str] = None
    download_url: Optional[str] = None
    character_count: Optional[int] = None


class UsageStatsResponse(BaseModel):
    """API usage statistics"""
    character_count: int
    character_limit: int
    remaining_characters: int
    tier: str
    can_use_instant_voice_cloning: bool
    can_use_professional_voice_cloning: bool


# Endpoints

@router.post("/clone", response_model=VoiceCloneResponse)
async def clone_voice(
    name: str = Form(...),
    description: str = Form(""),
    labels: str = Form("{}"),  # JSON string
    files: List[UploadFile] = File(...)
):
    """
    Clone a voice from audio samples.

    Upload 1-3 audio samples of clean speech (no background noise/music).
    Each sample should be 30 seconds to 5 minutes long.

    Args:
        name: Voice name (e.g., "CEO Voice")
        description: Voice description
        labels: JSON string of metadata (e.g., '{"use_case": "ads"}')
        files: Audio files (MP3 or WAV)

    Returns:
        VoiceCloneResponse with voice_id

    Requirements:
        - At least 1 audio sample (3+ recommended)
        - Clean speech, single speaker
        - No background music/noise
        - WAV or MP3 format

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/voice/clone" \\
          -F "name=CEO Voice" \\
          -F "description=Our CEO's voice for announcements" \\
          -F "files=@sample1.mp3" \\
          -F "files=@sample2.mp3"
        ```
    """
    if VoiceCloner is None:
        raise HTTPException(
            status_code=500,
            detail="Voice cloning not available. Install: uv add requests"
        )

    if not files:
        raise HTTPException(
            status_code=400,
            detail="At least 1 audio file required"
        )

    # Validate file types
    for file in files:
        if not file.filename.endswith(('.mp3', '.wav', '.m4a')):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Supported: .mp3, .wav, .m4a"
            )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_voice_cloning"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded files
        audio_paths = []
        for file in files:
            file_path = temp_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            audio_paths.append(str(file_path))

        # Parse labels
        import json
        labels_dict = json.loads(labels) if labels != "{}" else {}

        # Clone voice
        cloner = VoiceCloner()
        voice = cloner.clone_voice(
            name=name,
            audio_files=audio_paths,
            description=description,
            labels=labels_dict
        )

        # Cleanup temp files
        for path in audio_paths:
            os.remove(path)

        return VoiceCloneResponse(
            success=True,
            message=f"Voice cloned successfully: {voice.name}",
            voice_id=voice.voice_id,
            voice_name=voice.name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cloning voice: {str(e)}")


@router.get("/list", response_model=VoiceListResponse)
async def list_voices():
    """
    List all available voices (including cloned and premade).

    Returns:
        List of all available voices

    Example:
        ```bash
        curl "http://localhost:8000/api/voice/list"
        ```
    """
    if VoiceCloner is None:
        raise HTTPException(
            status_code=500,
            detail="Voice cloning not available"
        )

    try:
        cloner = VoiceCloner()
        voices = cloner.list_voices()

        voice_models = [
            VoiceModel(
                voice_id=v.voice_id,
                name=v.name,
                category=v.category,
                description=v.description,
                labels=v.labels,
                sample_count=len(v.samples)
            )
            for v in voices
        ]

        return VoiceListResponse(
            voices=voice_models,
            total=len(voice_models)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing voices: {str(e)}")


@router.get("/detail/{voice_id}", response_model=VoiceModel)
async def get_voice_detail(voice_id: str):
    """
    Get detailed information about a specific voice.

    Args:
        voice_id: Voice ID

    Returns:
        Detailed voice information
    """
    if VoiceCloner is None:
        raise HTTPException(
            status_code=500,
            detail="Voice cloning not available"
        )

    try:
        cloner = VoiceCloner()
        voice = cloner.get_voice(voice_id)

        return VoiceModel(
            voice_id=voice.voice_id,
            name=voice.name,
            category=voice.category,
            description=voice.description,
            labels=voice.labels,
            sample_count=len(voice.samples)
        )

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Voice not found: {str(e)}")


@router.delete("/delete/{voice_id}")
async def delete_voice(voice_id: str):
    """
    Delete a cloned voice.

    Args:
        voice_id: Voice ID to delete

    Returns:
        Success message

    Warning:
        Cannot delete premade voices, only custom cloned voices.
    """
    if VoiceCloner is None:
        raise HTTPException(
            status_code=500,
            detail="Voice cloning not available"
        )

    try:
        cloner = VoiceCloner()
        cloner.delete_voice(voice_id)

        return {"success": True, "message": f"Voice deleted: {voice_id}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting voice: {str(e)}")


@router.post("/generate-speech", response_model=SpeechGenerateResponse)
async def generate_speech(
    text: str = Form(...),
    voice_id: str = Form(...),
    content_type: str = Form("short"),
    model: str = Form("eleven_multilingual_v2"),
    stability: float = Form(None),
    similarity_boost: float = Form(None),
    style: float = Form(None),
    use_speaker_boost: bool = Form(None)
):
    """
    Generate speech from text using a voice.

    Args:
        text: Text to synthesize
        voice_id: Voice ID to use
        content_type: Content type preset (short, reel, ad, tutorial, storytelling, energetic)
        model: Model to use (eleven_multilingual_v2, eleven_monolingual_v1, eleven_turbo_v2)
        stability: Override stability setting (0.0-1.0)
        similarity_boost: Override similarity boost (0.0-1.0)
        style: Override style (0.0-1.0)
        use_speaker_boost: Override speaker boost

    Returns:
        SpeechGenerateResponse with download URL

    Content Type Presets:
        - short: Optimized for TikTok/Reels (expressive, high energy)
        - reel: Similar to short
        - ad: Professional, clear, confident
        - tutorial: Clear, stable, easy to understand
        - storytelling: Expressive with emotion
        - energetic: High energy, enthusiastic

    Models:
        - eleven_multilingual_v2: Best quality, 29 languages
        - eleven_monolingual_v1: English only, faster
        - eleven_turbo_v2: Fastest, good quality

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/voice/generate-speech" \\
          -F "text=Welcome to our channel!" \\
          -F "voice_id=abc123" \\
          -F "content_type=short"
        ```
    """
    if VoiceCloner is None:
        raise HTTPException(
            status_code=500,
            detail="Voice cloning not available"
        )

    # Validate content type
    valid_content_types = ["short", "reel", "ad", "tutorial", "storytelling", "energetic", "custom"]
    if content_type not in valid_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid content_type. Must be one of: {', '.join(valid_content_types)}"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_voice_speech"
        temp_dir.mkdir(exist_ok=True)

        # Generate output path
        output_filename = f"speech_{voice_id}_{int(time.time())}.mp3"
        output_path = temp_dir / output_filename

        # Create cloner
        cloner = VoiceCloner()

        # Build settings if custom values provided
        settings = None
        if any(x is not None for x in [stability, similarity_boost, style, use_speaker_boost]):
            # Get preset as base
            from features.audio.voice_cloning import VoiceSettings
            if content_type != "custom" and content_type in cloner.CONTENT_PRESETS:
                settings = cloner.CONTENT_PRESETS[content_type]
            else:
                settings = VoiceSettings()

            # Override with custom values
            if stability is not None:
                settings.stability = stability
            if similarity_boost is not None:
                settings.similarity_boost = similarity_boost
            if style is not None:
                settings.style = style
            if use_speaker_boost is not None:
                settings.use_speaker_boost = use_speaker_boost

        # Generate speech
        import time
        result_path = cloner.generate_speech(
            text=text,
            voice_id=voice_id,
            output_path=str(output_path),
            model=model,
            settings=settings,
            content_type=content_type if content_type != "custom" else None
        )

        return SpeechGenerateResponse(
            success=True,
            message="Speech generated successfully",
            output_path=str(result_path),
            download_url=f"/api/voice/download/{output_filename}",
            character_count=len(text)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")


@router.get("/download/{filename}")
async def download_speech(filename: str):
    """
    Download generated speech file.

    Args:
        filename: Speech file name

    Returns:
        Audio file for download
    """
    temp_dir = Path(tempfile.gettempdir()) / "media_empire_voice_speech"
    file_path = temp_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="audio/mpeg",
        filename=filename
    )


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats():
    """
    Get API usage statistics.

    Returns:
        Usage information (character count, quota, tier, etc.)

    Example:
        ```bash
        curl "http://localhost:8000/api/voice/usage"
        ```
    """
    if VoiceCloner is None:
        raise HTTPException(
            status_code=500,
            detail="Voice cloning not available"
        )

    try:
        cloner = VoiceCloner()
        stats = cloner.get_usage_stats()

        return UsageStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching usage: {str(e)}")


@router.get("/presets")
async def list_content_presets():
    """
    List all available content type presets with their settings.

    Returns:
        Dictionary of content presets and their voice settings
    """
    if VoiceCloner is None:
        raise HTTPException(
            status_code=500,
            detail="Voice cloning not available"
        )

    from features.audio.voice_cloning import VoiceCloner

    presets = {}
    for content_type, settings in VoiceCloner.CONTENT_PRESETS.items():
        presets[content_type] = {
            "stability": settings.stability,
            "similarity_boost": settings.similarity_boost,
            "style": settings.style,
            "use_speaker_boost": settings.use_speaker_boost,
            "description": _get_preset_description(content_type)
        }

    return {
        "presets": presets,
        "total": len(presets)
    }


def _get_preset_description(content_type: str) -> str:
    """Get description for content type preset."""
    descriptions = {
        "short": "Optimized for TikTok/Reels - expressive, high energy, engaging",
        "reel": "Similar to short - great for Instagram Reels",
        "ad": "Professional, clear, confident - perfect for advertisements",
        "tutorial": "Clear, stable, easy to understand - ideal for tutorials",
        "storytelling": "Expressive with emotion - brings stories to life",
        "energetic": "High energy, enthusiastic - grabs attention"
    }
    return descriptions.get(content_type, "Custom preset")
