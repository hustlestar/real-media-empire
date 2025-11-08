"""
API endpoints for automated subtitle generation.

Note: This router expects features.video module to be importable.
If running from director-ui/, set PYTHONPATH to include src/:
    PYTHONPATH=../src uvicorn src.api.app:app --reload
"""

import os
import tempfile
from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Direct import - ensure PYTHONPATH includes src/
try:
    from features.video.subtitles import SubtitleGenerator, SubtitleStyle
except ImportError:
    SubtitleGenerator = None


router = APIRouter(prefix="/api/subtitles", tags=["subtitles"])


class SubtitleRequest(BaseModel):
    """Request model for subtitle generation"""
    style: SubtitleStyle = "tiktok"
    highlight_keywords: bool = True
    max_words_per_line: int = 5
    language: str = "en"


class SubtitleResponse(BaseModel):
    """Response model for subtitle generation"""
    success: bool
    message: str
    output_path: Optional[str] = None
    download_url: Optional[str] = None
    cost_saved: Optional[float] = None  # USD saved by using text-based method


@router.post("/add-from-text", response_model=SubtitleResponse)
async def add_subtitles_from_text(
    video: UploadFile = File(...),
    text: str = Form(...),
    style: str = Form("tiktok"),
    highlight_keywords: bool = Form(True),
    max_words_per_line: int = Form(5)
):
    """
    Add subtitles to video using pre-existing text (FREE - no API cost!).

    Use this for AI-generated videos where you already have the script.
    This method is FREE and doesn't require OpenAI API key!

    Args:
        video: Video file to process
        text: The script text (what's spoken in the video)
        style: Caption style (tiktok, instagram, mr_beast, minimal, professional)
        highlight_keywords: Whether to highlight important words
        max_words_per_line: Maximum words per subtitle line

    Returns:
        SubtitleResponse with download link

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/subtitles/add-from-text" \\
          -F "video=@generated_video.mp4" \\
          -F "text=Welcome to my channel! This is amazing content." \\
          -F "style=tiktok"
        ```

    Cost: FREE (no API calls)
    """
    if SubtitleGenerator is None:
        raise HTTPException(
            status_code=500,
            detail="Subtitle generation not available. Install: uv add moviepy"
        )

    # Validate file type
    if not video.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Supported: .mp4, .mov, .avi, .mkv"
        )

    # Validate style
    valid_styles = ["tiktok", "instagram", "mr_beast", "minimal", "professional"]
    if style not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_subtitles"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        input_path = temp_dir / f"input_{video.filename}"
        with open(input_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Calculate cost savings (vs Whisper transcription)
        from moviepy.editor import VideoFileClip
        vid = VideoFileClip(str(input_path))
        duration_minutes = vid.duration / 60
        vid.close()
        cost_saved = duration_minutes * 0.006  # Whisper costs $0.006/min

        # Generate output path
        output_filename = f"subtitled_text_{style}_{video.filename}"
        output_path = temp_dir / output_filename

        # Generate subtitles from text (NO API COST!)
        generator = SubtitleGenerator()  # No API key needed!

        result_path = generator.add_subtitles_from_text(
            video_path=str(input_path),
            text=text,
            output_path=str(output_path),
            style=style,
            highlight_keywords=highlight_keywords,
            max_words_per_line=max_words_per_line
        )

        return SubtitleResponse(
            success=True,
            message=f"Subtitles added successfully (saved ${cost_saved:.3f})",
            output_path=str(result_path),
            download_url=f"/api/subtitles/download/{output_filename}",
            cost_saved=cost_saved
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@router.post("/add", response_model=SubtitleResponse)
async def add_subtitles(
    video: UploadFile = File(...),
    style: str = Form("tiktok"),
    highlight_keywords: bool = Form(True),
    max_words_per_line: int = Form(5),
    language: str = Form("en")
):
    """
    Add subtitles to uploaded video.

    Args:
        video: Video file to process
        style: Caption style (tiktok, instagram, mr_beast, minimal, professional)
        highlight_keywords: Whether to highlight important words
        max_words_per_line: Maximum words per subtitle line
        language: Language code for transcription

    Returns:
        SubtitleResponse with download link

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/subtitles/add" \\
          -F "video=@input.mp4" \\
          -F "style=tiktok" \\
          -F "highlight_keywords=true"
        ```
    """
    if SubtitleGenerator is None:
        raise HTTPException(
            status_code=500,
            detail="Subtitle generation not available. Install dependencies: uv add openai moviepy"
        )

    # Validate file type
    if not video.filename.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Supported: .mp4, .mov, .avi, .mkv"
        )

    # Validate style
    valid_styles = ["tiktok", "instagram", "mr_beast", "minimal", "professional"]
    if style not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_subtitles"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        input_path = temp_dir / f"input_{video.filename}"
        with open(input_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Generate output path
        output_filename = f"subtitled_{style}_{video.filename}"
        output_path = temp_dir / output_filename

        # Generate subtitles
        generator = SubtitleGenerator()

        result_path = generator.add_subtitles(
            video_path=str(input_path),
            output_path=str(output_path),
            style=style,
            highlight_keywords=highlight_keywords,
            max_words_per_line=max_words_per_line,
            language=language
        )

        return SubtitleResponse(
            success=True,
            message="Subtitles added successfully",
            output_path=str(result_path),
            download_url=f"/api/subtitles/download/{output_filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@router.get("/download/{filename}")
async def download_subtitled_video(filename: str):
    """
    Download a subtitled video.

    Args:
        filename: Name of the subtitled video file

    Returns:
        Video file for download
    """
    temp_dir = Path(tempfile.gettempdir()) / "media_empire_subtitles"
    file_path = temp_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=filename
    )


@router.post("/export-transcript", response_model=SubtitleResponse)
async def export_transcript(
    video: UploadFile = File(...),
    format: Literal["srt", "vtt", "json", "txt"] = Form("srt")
):
    """
    Export video transcript in various formats.

    Args:
        video: Video file to transcribe
        format: Output format (srt, vtt, json, txt)

    Returns:
        SubtitleResponse with download link
    """
    if SubtitleGenerator is None:
        raise HTTPException(
            status_code=500,
            detail="Subtitle generation not available"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_subtitles"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        input_path = temp_dir / f"input_{video.filename}"
        with open(input_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Generate output path
        output_filename = f"transcript.{format}"
        output_path = temp_dir / output_filename

        # Export transcript
        generator = SubtitleGenerator()

        result_path = generator.export_transcript(
            video_path=str(input_path),
            output_path=str(output_path),
            format=format
        )

        return SubtitleResponse(
            success=True,
            message=f"Transcript exported as {format}",
            output_path=str(result_path),
            download_url=f"/api/subtitles/download-transcript/{output_filename}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@router.get("/download-transcript/{filename}")
async def download_transcript(filename: str):
    """Download a transcript file"""
    temp_dir = Path(tempfile.gettempdir()) / "media_empire_subtitles"
    file_path = temp_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type
    media_types = {
        ".srt": "text/plain",
        ".vtt": "text/vtt",
        ".json": "application/json",
        ".txt": "text/plain"
    }

    file_ext = Path(filename).suffix
    media_type = media_types.get(file_ext, "text/plain")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename
    )


@router.get("/styles")
async def list_subtitle_styles():
    """
    List all available subtitle styles with their configurations.

    Returns:
        Dictionary of available styles and their settings
    """
    if SubtitleGenerator is None:
        raise HTTPException(
            status_code=500,
            detail="Subtitle generation not available"
        )

    from features.video.subtitles import SubtitleStyleConfig

    return {
        "styles": list(SubtitleStyleConfig.STYLES.keys()),
        "configurations": SubtitleStyleConfig.STYLES
    }
