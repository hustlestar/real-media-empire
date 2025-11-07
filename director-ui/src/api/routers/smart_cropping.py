"""
API endpoints for smart cropping with subject tracking.

Note: This router expects features.video module to be importable.
If running from director-ui/, set PYTHONPATH to include src/:
    PYTHONPATH=../src uvicorn src.api.app:app --reload
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Direct import - ensure PYTHONPATH includes src/
try:
    from features.video.smart_cropping import SmartCropper, smart_crop_video, DetectionMode
except ImportError:
    SmartCropper = None


router = APIRouter(prefix="/api/smart-crop", tags=["smart_cropping"])


# Request/Response Models

class SmartCropResponse(BaseModel):
    """Smart crop response"""
    success: bool
    message: str
    output_path: Optional[str] = None
    download_url: Optional[str] = None
    detection_mode: str
    subjects_tracked: bool


class TrackingInfoResponse(BaseModel):
    """Subject tracking information"""
    success: bool
    total_frames: int
    subjects_detected: int
    primary_subject: str
    tracking_quality: str


# Endpoints

@router.post("/crop", response_model=SmartCropResponse)
async def smart_crop(
    video: UploadFile = File(...),
    target_width: int = Form(1080),
    target_height: int = Form(1920),
    detection_mode: str = Form("balanced"),
    track_subject: bool = Form(True)
):
    """
    Apply smart cropping with subject tracking.

    Automatically detects and tracks main subjects (faces, people, objects)
    and keeps them in frame when cropping to different aspect ratios.

    Args:
        video: Video file to crop
        target_width: Target width in pixels
        target_height: Target height in pixels
        detection_mode: Detection mode (fast, balanced, accurate)
        track_subject: Enable subject tracking across frames

    Returns:
        Cropped video with subjects kept in frame

    Detection Modes:
        - fast: Faster but less accurate (every 10 frames)
        - balanced: Good speed/accuracy balance (every 5 frames) [recommended]
        - accurate: Best accuracy (every frame) - slower

    Subject Detection Priority:
        1. Faces (highest priority)
        2. People/persons
        3. Animals (dogs, cats, horses)
        4. Objects (phones, laptops, etc.)

    Example:
        ```bash
        # Crop to TikTok format (9:16) with subject tracking
        curl -X POST "http://localhost:8000/api/smart-crop/crop" \\
          -F "video=@input.mp4" \\
          -F "target_width=1080" \\
          -F "target_height=1920" \\
          -F "detection_mode=balanced" \\
          -F "track_subject=true"
        ```
    """
    if SmartCropper is None:
        raise HTTPException(
            status_code=500,
            detail="Smart cropping not available. Install: uv add moviepy opencv-python"
        )

    # Validate detection mode
    valid_modes = ["fast", "balanced", "accurate"]
    if detection_mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid detection_mode. Must be one of: {', '.join(valid_modes)}"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_smart_crop"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        video_path = temp_dir / f"input_{video.filename}"
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Generate output path
        output_filename = f"smartcrop_{target_width}x{target_height}_{video.filename}"
        output_path = temp_dir / output_filename

        # Apply smart crop
        cropper = SmartCropper(detection_mode=detection_mode)
        result_path = cropper.apply_smart_crop(
            video_path=str(video_path),
            output_path=str(output_path),
            target_size=(target_width, target_height),
            track=track_subject
        )

        # Cleanup input
        os.remove(video_path)

        return SmartCropResponse(
            success=True,
            message="Smart crop completed successfully",
            output_path=str(result_path),
            download_url=f"/api/smart-crop/download/{output_filename}",
            detection_mode=detection_mode,
            subjects_tracked=track_subject
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying smart crop: {str(e)}")


@router.post("/track-info", response_model=TrackingInfoResponse)
async def get_tracking_info(
    video: UploadFile = File(...),
    detection_mode: str = Form("balanced")
):
    """
    Get subject tracking information without cropping.

    Analyzes video and returns information about detected subjects
    and tracking quality.

    Args:
        video: Video file to analyze
        detection_mode: Detection mode (fast, balanced, accurate)

    Returns:
        Subject tracking information

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/smart-crop/track-info" \\
          -F "video=@input.mp4" \\
          -F "detection_mode=balanced"
        ```
    """
    if SmartCropper is None:
        raise HTTPException(
            status_code=500,
            detail="Smart cropping not available"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_smart_crop"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        video_path = temp_dir / f"analyze_{video.filename}"
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Track subjects
        cropper = SmartCropper(detection_mode=detection_mode)
        crop_centers = cropper.track_subject(
            video_path=str(video_path),
            target_aspect_ratio=(9, 16)  # Default
        )

        # Analyze tracking quality
        # Check for variation in positions (indicates subject movement)
        if len(crop_centers) > 1:
            variations = []
            for i in range(len(crop_centers) - 1):
                dx = crop_centers[i+1][0] - crop_centers[i][0]
                dy = crop_centers[i+1][1] - crop_centers[i][1]
                dist = (dx**2 + dy**2) ** 0.5
                variations.append(dist)

            avg_variation = sum(variations) / len(variations) if variations else 0

            if avg_variation < 0.02:
                quality = "stable"  # Subject mostly stationary
            elif avg_variation < 0.05:
                quality = "good"    # Normal movement
            elif avg_variation < 0.10:
                quality = "active"  # High movement
            else:
                quality = "very_active"  # Very dynamic
        else:
            quality = "unknown"

        # Cleanup
        os.remove(video_path)

        # Get first frame detection to identify primary subject
        from moviepy.editor import VideoFileClip
        test_video = VideoFileClip(str(video_path))
        first_frame = test_video.get_frame(0)
        test_video.close()

        detections = cropper._detect_subjects(first_frame)
        primary_subject = "none"
        if detections:
            primary = cropper._select_primary_subject(detections)
            primary_subject = primary.class_name

        return TrackingInfoResponse(
            success=True,
            total_frames=len(crop_centers),
            subjects_detected=len(detections),
            primary_subject=primary_subject,
            tracking_quality=quality
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing tracking: {str(e)}")


@router.get("/download/{filename}")
async def download_cropped(filename: str):
    """
    Download smart-cropped video.

    Args:
        filename: Video file name

    Returns:
        Cropped video file
    """
    temp_dir = Path(tempfile.gettempdir()) / "media_empire_smart_crop"
    file_path = temp_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=filename
    )


@router.get("/detection-info")
async def get_detection_info():
    """
    Get information about detection capabilities.

    Returns:
        Information about available detection methods and supported objects

    Example:
        ```bash
        curl "http://localhost:8000/api/smart-crop/detection-info"
        ```
    """
    if SmartCropper is None:
        return {
            "available": False,
            "error": "Smart cropping not installed"
        }

    cropper = SmartCropper()

    return {
        "available": True,
        "yolo_enabled": cropper.yolo_available,
        "detection_methods": {
            "face_detection": {
                "available": True,
                "method": "OpenCV Haar Cascade",
                "priority": 1,
                "description": "Detects human faces (highest priority)"
            },
            "yolo_detection": {
                "available": cropper.yolo_available,
                "method": "YOLOv3 on COCO dataset",
                "priority": 2,
                "description": "Detects 80+ object classes"
            },
            "saliency_detection": {
                "available": True,
                "method": "Laplacian edge detection",
                "priority": 3,
                "description": "Fallback: detects regions with most detail"
            }
        },
        "supported_objects": [
            "face (priority 1)",
            "person (priority 2)",
            "cat (priority 3)",
            "dog (priority 3)",
            "horse (priority 3)",
            "laptop (priority 4)",
            "cell phone (priority 4)",
            "mouse (priority 5)",
            "keyboard (priority 5)",
            "remote (priority 5)"
        ] if cropper.yolo_available else ["face (priority 1)", "salient regions (priority 6)"],
        "detection_modes": {
            "fast": "Process every 10th frame (fastest, less smooth)",
            "balanced": "Process every 5th frame (recommended)",
            "accurate": "Process every frame (slowest, smoothest)"
        },
        "notes": [
            "Faces are always detected with OpenCV (works without YOLO)",
            "YOLO detection requires downloading weight files separately",
            "Download YOLO weights from: https://pjreddie.com/darknet/yolo/",
            "Subject tracking uses motion interpolation for smooth results"
        ]
    }


@router.get("/presets")
async def list_platform_presets():
    """
    List common platform cropping presets.

    Returns:
        Common aspect ratios and sizes for social media platforms

    Example:
        ```bash
        curl "http://localhost:8000/api/smart-crop/presets"
        ```
    """
    return {
        "presets": {
            "tiktok": {
                "width": 1080,
                "height": 1920,
                "aspect_ratio": "9:16",
                "description": "TikTok vertical format"
            },
            "youtube_shorts": {
                "width": 1080,
                "height": 1920,
                "aspect_ratio": "9:16",
                "description": "YouTube Shorts vertical format"
            },
            "instagram_reels": {
                "width": 1080,
                "height": 1920,
                "aspect_ratio": "9:16",
                "description": "Instagram Reels vertical format"
            },
            "instagram_feed": {
                "width": 1080,
                "height": 1350,
                "aspect_ratio": "4:5",
                "description": "Instagram feed portrait"
            },
            "instagram_square": {
                "width": 1080,
                "height": 1080,
                "aspect_ratio": "1:1",
                "description": "Instagram square post"
            },
            "youtube": {
                "width": 1920,
                "height": 1080,
                "aspect_ratio": "16:9",
                "description": "YouTube horizontal format"
            },
            "twitter": {
                "width": 1280,
                "height": 720,
                "aspect_ratio": "16:9",
                "description": "Twitter video format"
            },
            "linkedin": {
                "width": 1200,
                "height": 1200,
                "aspect_ratio": "1:1",
                "description": "LinkedIn square format"
            }
        },
        "recommendation": "Use 'balanced' detection mode for best speed/quality trade-off"
    }
