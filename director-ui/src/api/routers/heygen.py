"""
HeyGen API router for avatar video generation.

Endpoints:
- POST /api/heygen/generate - Generate avatar video
- GET /api/heygen/avatars - List available avatars
- GET /api/heygen/voices - List available voices
- GET /api/heygen/videos/{video_id}/status - Get video status
"""

from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..dependencies import get_heygen_provider
from film.providers.heygen import (
    HeyGenProvider,
    HeyGenBackgroundConfig,
    HeyGenDimensionConfig,
    HeyGenVoiceConfig,
    HeyGenCharacterConfig
)

router = APIRouter()


class GenerateAvatarVideoRequest(BaseModel):
    """Request to generate avatar video."""
    script: str = Field(..., description="Text script for avatar to speak", min_length=1, max_length=10000)
    avatar_id: str = Field(..., description="HeyGen avatar ID")
    voice_id: str = Field(..., description="HeyGen voice ID")

    # Optional configurations
    aspect_ratio: Optional[Literal["9:16", "16:9", "1:1", "4:5"]] = Field(
        default="9:16",
        description="Video aspect ratio for social platforms"
    )

    # Background configuration
    background_type: Optional[Literal["color", "image", "video"]] = Field(
        default="color",
        description="Type of background"
    )
    background_value: Optional[str] = Field(
        default="#000000",
        description="Background color hex or URL for image/video"
    )

    # Voice settings
    voice_speed: float = Field(default=1.1, ge=0.5, le=2.0, description="Voice speed multiplier")
    voice_pitch: int = Field(default=50, ge=0, le=100, description="Voice pitch (0-100)")
    voice_emotion: Optional[str] = Field(default="Excited", description="Voice emotion")

    # Character settings
    avatar_scale: float = Field(default=1.0, ge=0.5, le=2.0, description="Avatar scale")
    has_green_screen: bool = Field(default=False, description="Avatar has background removed")
    avatar_offset_x: float = Field(default=0.0, description="Horizontal offset (-1 to 1)")
    avatar_offset_y: float = Field(default=0.0, description="Vertical offset (-1 to 1)")

    # Video settings
    title: Optional[str] = Field(default="", description="Video title")
    caption: bool = Field(default=False, description="Generate captions")
    test: bool = Field(default=False, description="Test mode (doesn't consume credits)")


class GenerateAvatarVideoResponse(BaseModel):
    """Response from avatar video generation."""
    video_id: str
    video_url: str
    status: str
    cost: float
    duration: float
    metadata: dict


class AvatarInfo(BaseModel):
    """Avatar information."""
    id: str
    name: str
    preview_image_url: Optional[str]
    preview_video_url: Optional[str]
    gender: Optional[str]
    is_green_screen: bool = False


class VoiceInfo(BaseModel):
    """Voice information."""
    id: str
    name: str
    language: str
    gender: Optional[str]
    preview_audio_url: Optional[str]


@router.post("/generate", response_model=GenerateAvatarVideoResponse)
async def generate_avatar_video(
    request: GenerateAvatarVideoRequest,
    provider: HeyGenProvider = Depends(get_heygen_provider)
):
    """
    Generate avatar video using HeyGen.

    This endpoint creates a video of an AI avatar speaking the provided script.

    Args:
        request: Avatar video generation parameters

    Returns:
        Video URL, ID, and metadata

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Build background configuration
        background = None
        if request.background_type:
            if request.background_type == "color":
                background = HeyGenBackgroundConfig(
                    type="color",
                    value=request.background_value or "#000000"
                )
            elif request.background_type in ["image", "video"]:
                background = HeyGenBackgroundConfig(
                    type=request.background_type,
                    url=request.background_value,
                    play_style="loop",
                    fit="cover"
                )

        # Build dimension from aspect ratio
        dimension = HeyGenDimensionConfig.from_aspect_ratio(request.aspect_ratio)

        # Build voice configuration
        voice_config = HeyGenVoiceConfig(
            input_text=request.script,
            voice_id=request.voice_id,
            speed=request.voice_speed,
            pitch=request.voice_pitch,
            emotion=request.voice_emotion
        )

        # Build character configuration
        character_config = HeyGenCharacterConfig(
            avatar_id=request.avatar_id,
            scale=request.avatar_scale,
            matting=request.has_green_screen
        )

        # Add offset if green screen
        if request.has_green_screen and (request.avatar_offset_x != 0 or request.avatar_offset_y != 0):
            character_config.offset = {
                "x": request.avatar_offset_x,
                "y": request.avatar_offset_y
            }

        # Generate video
        result = await provider.generate(
            script=request.script,
            avatar_id=request.avatar_id,
            voice_id=request.voice_id,
            background=background,
            dimension=dimension,
            voice_config=voice_config,
            character_config=character_config,
            title=request.title,
            caption=request.caption,
            test=request.test
        )

        return GenerateAvatarVideoResponse(
            video_id=result.metadata["video_id"],
            video_url=result.video_url,
            status="completed",
            cost=result.cost,
            duration=result.metadata["duration"],
            metadata=result.metadata
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/avatars", response_model=list[AvatarInfo])
async def list_avatars(
    provider: HeyGenProvider = Depends(get_heygen_provider)
):
    """
    List all available HeyGen avatars.

    Returns:
        List of avatars with IDs, names, and preview URLs
    """
    try:
        avatars = await provider.list_avatars()

        # Transform to response model
        return [
            AvatarInfo(
                id=avatar.get("avatar_id"),
                name=avatar.get("avatar_name"),
                preview_image_url=avatar.get("preview_image_url"),
                preview_video_url=avatar.get("preview_video_url"),
                gender=avatar.get("gender"),
                is_green_screen=avatar.get("is_green_screen", False)
            )
            for avatar in avatars
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices", response_model=list[VoiceInfo])
async def list_voices(
    language: Optional[str] = None,
    provider: HeyGenProvider = Depends(get_heygen_provider)
):
    """
    List all available HeyGen voices.

    Args:
        language: Optional filter by language code (e.g., "en", "es", "fr")

    Returns:
        List of voices with IDs, names, and preview URLs
    """
    try:
        voices = await provider.list_voices()

        # Filter by language if specified
        if language:
            voices = [v for v in voices if v.get("language", "").startswith(language)]

        # Transform to response model
        return [
            VoiceInfo(
                id=voice.get("voice_id"),
                name=voice.get("name"),
                language=voice.get("language", "en"),
                gender=voice.get("gender"),
                preview_audio_url=voice.get("preview_audio_url")
            )
            for voice in voices
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/{video_id}/status")
async def get_video_status(
    video_id: str,
    provider: HeyGenProvider = Depends(get_heygen_provider)
):
    """
    Get status of a HeyGen video generation.

    Args:
        video_id: HeyGen video ID

    Returns:
        Video status, progress, and URL when complete
    """
    try:
        status = await provider.get_video_status(video_id)
        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aspect-ratios")
async def list_aspect_ratios():
    """
    List supported aspect ratios and their use cases.

    Returns:
        Dictionary of aspect ratios with dimensions and recommended platforms
    """
    return {
        "9:16": {
            "width": 720,
            "height": 1280,
            "name": "Vertical",
            "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts", "Snapchat"],
            "description": "Mobile-first vertical video"
        },
        "16:9": {
            "width": 1280,
            "height": 720,
            "name": "Landscape",
            "platforms": ["YouTube", "LinkedIn", "Twitter", "Facebook"],
            "description": "Standard widescreen format"
        },
        "1:1": {
            "width": 1080,
            "height": 1080,
            "name": "Square",
            "platforms": ["Instagram Feed", "Facebook Feed", "Twitter"],
            "description": "Square format for feeds"
        },
        "4:5": {
            "width": 1080,
            "height": 1350,
            "name": "Portrait",
            "platforms": ["Instagram Feed", "Facebook Feed"],
            "description": "Tall portrait for mobile feeds"
        }
    }
