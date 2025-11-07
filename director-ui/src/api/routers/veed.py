"""
VEED.io Talking Avatar API Router

Endpoints for creating AI talking avatar videos from photos and audio.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional

from film.providers.veed import VEEDProvider, VEEDConfig
import os

router = APIRouter()


# Dependency injection
_veed_provider: Optional[VEEDProvider] = None


async def get_veed_provider() -> VEEDProvider:
    """Get or create VEED provider singleton."""
    global _veed_provider
    if _veed_provider is None:
        fal_api_key = os.getenv("FAL_API_KEY")
        if not fal_api_key:
            raise HTTPException(
                status_code=500,
                detail="FAL_API_KEY environment variable not set"
            )
        config = VEEDConfig(fal_api_key=fal_api_key)
        _veed_provider = VEEDProvider(config)
    return _veed_provider


# Request/Response Models

class GenerateTalkingAvatarRequest(BaseModel):
    """Request to generate a talking avatar video."""
    image_url: HttpUrl
    audio_url: HttpUrl
    resolution: Literal["480p", "720p", "1080p"] = "720p"


class GenerateTalkingAvatarResponse(BaseModel):
    """Response from talking avatar generation."""
    request_id: str
    video_url: str
    status: str
    provider: str
    cost: float
    metadata: dict


class TalkingAvatarStatusResponse(BaseModel):
    """Status check response for talking avatar generation."""
    request_id: str
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None


# Endpoints

@router.post("/generate-talking-avatar", response_model=GenerateTalkingAvatarResponse)
async def generate_talking_avatar(
    request: GenerateTalkingAvatarRequest,
    provider: VEEDProvider = Depends(get_veed_provider)
):
    """
    Generate an AI talking avatar video from a photo and audio.

    This creates a video where a static photo appears to speak with
    automatic lip-sync matching the provided audio.

    **Use Cases:**
    - Faceless content creation
    - UGC-style videos
    - Educational content
    - Product demonstrations
    - Social media shorts

    **Args:**
    - image_url: URL to source photo (must show a person's face)
    - audio_url: URL to audio file (voice-over)
    - resolution: Video quality (480p, 720p, or 1080p)

    **Returns:**
    - request_id: Unique ID for this generation
    - video_url: URL to the generated video
    - status: Generation status
    - cost: Approximate cost in USD
    """
    try:
        result = await provider.generate_talking_avatar(
            image_url=str(request.image_url),
            audio_url=str(request.audio_url),
            resolution=request.resolution
        )

        return GenerateTalkingAvatarResponse(
            request_id=result.video_id,
            video_url=result.video_url,
            status="completed",
            provider=result.provider,
            cost=result.cost,
            metadata=result.metadata
        )

    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/talking-avatar-info")
async def get_talking_avatar_info():
    """
    Get information about VEED talking avatar capabilities.

    Returns supported resolutions, pricing, and limitations.
    """
    return {
        "provider": "veed-fabric-1.0",
        "service": "FAL.ai",
        "capabilities": {
            "talking_avatar": True,
            "lip_sync": True,
            "resolutions": ["480p", "720p", "1080p"],
            "max_duration": "Matches audio duration",
            "supported_formats": ["mp4"]
        },
        "pricing": {
            "per_video": 0.10,
            "currency": "USD",
            "note": "Approximate cost, actual may vary"
        },
        "requirements": {
            "image": "Must contain visible face",
            "audio": "Any audio format supported by FAL.ai",
            "max_wait_time": "10 minutes"
        },
        "use_cases": [
            "Faceless content creation",
            "UGC-style videos",
            "Educational tutorials",
            "Product demonstrations",
            "Social media shorts",
            "Personalized video messages"
        ]
    }


@router.get("/talking-avatar-examples")
async def get_talking_avatar_examples():
    """Get example use cases and templates for talking avatars."""
    return {
        "examples": [
            {
                "name": "Product Review",
                "description": "Create product review videos without showing your face",
                "image": "Casual photo of person",
                "audio": "Voice-over reviewing product features",
                "resolution": "720p",
                "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"]
            },
            {
                "name": "Tutorial Content",
                "description": "Educational content with talking head",
                "image": "Professional headshot",
                "audio": "Step-by-step tutorial narration",
                "resolution": "1080p",
                "platforms": ["YouTube", "LinkedIn"]
            },
            {
                "name": "Social Media Hook",
                "description": "Attention-grabbing intro for social content",
                "image": "Expressive photo",
                "audio": "7-second hook script",
                "resolution": "480p",
                "platforms": ["TikTok", "Instagram Reels"]
            },
            {
                "name": "Testimonial",
                "description": "Customer testimonial videos",
                "image": "Customer photo",
                "audio": "Testimonial recording",
                "resolution": "720p",
                "platforms": ["Website", "Facebook", "Instagram"]
            }
        ]
    }
