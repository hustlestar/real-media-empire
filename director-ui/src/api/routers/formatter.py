"""
API endpoints for platform video formatting.

Note: This router expects features.video module to be importable.
If running from director-ui/, set PYTHONPATH to include src/:
    PYTHONPATH=../src uvicorn src.api.app:app --reload
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Direct import - ensure PYTHONPATH includes src/
try:
    from features.video.formatter import PlatformVideoFormatter, PlatformSpecs, Platform
except ImportError:
    PlatformVideoFormatter = None


router = APIRouter(prefix="/api/format", tags=["formatter"])


class FormatRequest(BaseModel):
    """Request model for video formatting"""
    platforms: List[str]
    smart_crop: bool = True
    add_padding: bool = False
    padding_color: str = "black"


class FormatResponse(BaseModel):
    """Response model for video formatting"""
    success: bool
    message: str
    versions: Optional[dict] = None  # {platform: download_url}


class ValidationResponse(BaseModel):
    """Response model for video validation"""
    platform: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    specs: dict


@router.post("/platforms", response_model=FormatResponse)
async def format_for_platforms(
    video: UploadFile = File(...),
    platforms: str = Form(...),  # Comma-separated list
    smart_crop: bool = Form(True),
    add_padding: bool = Form(False),
    padding_color: str = Form("black")
):
    """
    Format video for multiple social media platforms.

    Creates optimized versions of your video for each platform with correct
    aspect ratios, resolutions, and specifications.

    Args:
        video: Video file to format
        platforms: Comma-separated platform list (e.g., "tiktok,youtube,linkedin")
        smart_crop: Use intelligent cropping (detects faces/subjects)
        add_padding: Add padding instead of cropping
        padding_color: Padding color (black, white, blur)

    Returns:
        FormatResponse with download URLs for each platform

    Supported Platforms:
        - tiktok: 1080x1920 (9:16)
        - instagram_reels: 1080x1920 (9:16)
        - instagram_feed: 1080x1350 (4:5)
        - instagram_story: 1080x1920 (9:16)
        - youtube: 1920x1080 (16:9)
        - youtube_shorts: 1080x1920 (9:16)
        - linkedin: 1200x1200 (1:1)
        - facebook: 1920x1080 (16:9)
        - twitter: 1280x720 (16:9)

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/format/platforms" \\
          -F "video=@input.mp4" \\
          -F "platforms=tiktok,youtube,linkedin" \\
          -F "smart_crop=true"
        ```
    """
    if PlatformVideoFormatter is None:
        raise HTTPException(
            status_code=500,
            detail="Video formatter not available. Install: uv add moviepy opencv-python"
        )

    # Parse platforms
    platform_list = [p.strip() for p in platforms.split(",")]

    # Validate platforms
    valid_platforms = PlatformSpecs.list_platforms()
    invalid = [p for p in platform_list if p not in valid_platforms]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platforms: {', '.join(invalid)}. Valid: {', '.join(valid_platforms)}"
        )

    # Validate file type
    if not video.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Supported: .mp4, .mov, .avi, .mkv"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_formatter"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        input_path = temp_dir / f"input_{video.filename}"
        with open(input_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Format video
        formatter = PlatformVideoFormatter()

        results = formatter.create_all_versions(
            source_video=str(input_path),
            platforms=platform_list,
            smart_crop=smart_crop,
            add_padding=add_padding,
            padding_color=padding_color
        )

        # Generate download URLs
        download_urls = {}
        for platform, output_path in results.items():
            if output_path:
                filename = Path(output_path).name
                download_urls[platform] = f"/api/format/download/{filename}"

        return FormatResponse(
            success=True,
            message=f"Successfully formatted video for {len(download_urls)} platforms",
            versions=download_urls
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@router.get("/download/{filename}")
async def download_formatted_video(filename: str):
    """
    Download a formatted video.

    Args:
        filename: Name of the formatted video file

    Returns:
        Video file for download
    """
    temp_dir = Path(tempfile.gettempdir()) / "media_empire_formatter"
    file_path = temp_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=filename
    )


@router.post("/validate", response_model=List[ValidationResponse])
async def validate_video_for_platforms(
    video: UploadFile = File(...),
    platforms: str = Form(...)
):
    """
    Validate if video meets platform requirements.

    Check if your video meets the specifications for each platform
    (duration, file size, aspect ratio, etc.).

    Args:
        video: Video file to validate
        platforms: Comma-separated platform list

    Returns:
        List of validation results per platform

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/format/validate" \\
          -F "video=@input.mp4" \\
          -F "platforms=tiktok,youtube,instagram_reels"
        ```
    """
    if PlatformVideoFormatter is None:
        raise HTTPException(
            status_code=500,
            detail="Video formatter not available"
        )

    # Parse platforms
    platform_list = [p.strip() for p in platforms.split(",")]

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_formatter"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        input_path = temp_dir / f"validate_{video.filename}"
        with open(input_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Validate for each platform
        formatter = PlatformVideoFormatter()
        results = []

        for platform in platform_list:
            try:
                validation = formatter.validate_video(str(input_path), platform)
                results.append(ValidationResponse(
                    platform=platform,
                    valid=validation["valid"],
                    errors=validation["errors"],
                    warnings=validation["warnings"],
                    specs=validation["specs"]
                ))
            except Exception as e:
                results.append(ValidationResponse(
                    platform=platform,
                    valid=False,
                    errors=[str(e)],
                    warnings=[],
                    specs={}
                ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating video: {str(e)}")


@router.get("/platforms")
async def list_supported_platforms():
    """
    List all supported platforms with their specifications.

    Returns detailed specifications for each platform including:
    - Aspect ratio
    - Resolution
    - Max duration
    - Max file size
    - FPS

    Returns:
        Dictionary of platform specifications
    """
    if PlatformVideoFormatter is None:
        raise HTTPException(
            status_code=500,
            detail="Video formatter not available"
        )

    platforms = {}

    for platform_name, spec in PlatformSpecs.SPECS.items():
        platforms[platform_name] = {
            "name": spec.name,
            "aspect_ratio": f"{spec.aspect_ratio[0]}:{spec.aspect_ratio[1]}",
            "resolution": f"{spec.resolution[0]}x{spec.resolution[1]}",
            "max_duration": spec.max_duration,
            "fps": spec.fps,
            "max_file_size_mb": spec.max_file_size_mb
        }

    return {
        "platforms": platforms,
        "total": len(platforms)
    }
