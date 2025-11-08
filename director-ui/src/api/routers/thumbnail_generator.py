"""
API endpoints for thumbnail generation and optimization.

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
from pydantic import BaseModel, Field

# Direct import - ensure PYTHONPATH includes src/
try:
    from features.video.thumbnail_generator import ThumbnailGenerator, ThumbnailScore, ThumbnailStyle, Platform
except ImportError:
    ThumbnailGenerator = None


router = APIRouter(prefix="/api/thumbnail", tags=["thumbnail_generator"])


# Request/Response Models

class ThumbnailCreateResponse(BaseModel):
    """Thumbnail creation response"""
    success: bool
    message: str
    thumbnail_path: Optional[str] = None
    download_url: Optional[str] = None
    file_size_mb: Optional[float] = None


class ThumbnailScoreResponse(BaseModel):
    """Thumbnail scoring response"""
    success: bool
    overall_score: float
    grade: str
    face_score: float
    contrast_score: float
    text_score: float
    emotion_score: float
    composition_score: float
    recommendations: List[str] = []
    warnings: List[str] = []
    variant_id: Optional[str] = None


class ThumbnailABTestResponse(BaseModel):
    """A/B test response"""
    success: bool
    winner: Optional[str] = None
    thumbnails: List[str]
    download_urls: List[str]
    scores: Optional[List[ThumbnailScoreResponse]] = None


class ThumbnailTemplateInfo(BaseModel):
    """Template information"""
    name: str
    description: str
    best_for: List[str]
    example_use: str


# Endpoints

@router.post("/create", response_model=ThumbnailCreateResponse)
async def create_thumbnail(
    video: UploadFile = File(...),
    text: Optional[str] = Form(None),
    style: str = Form("viral"),
    platform: str = Form("youtube"),
    frame_time: Optional[float] = Form(None),
    auto_select_frame: bool = Form(True)
):
    """
    Create thumbnail from video.

    Thumbnails determine 90% of clicks! Use this to create eye-catching thumbnails
    optimized for maximum CTR.

    Args:
        video: Video file to extract thumbnail from
        text: Text overlay (keep under 4 words for best results!)
        style: Thumbnail style (viral, professional, minimal, energetic, mystery, educational)
        platform: Target platform (youtube, tiktok, instagram, facebook, twitter, linkedin)
        frame_time: Specific time to extract frame (seconds), or None for auto-select
        auto_select_frame: Auto-select best frame based on faces/emotion/contrast

    Returns:
        Thumbnail file with download URL

    Thumbnail Styles:
        - viral: Yellow text, high contrast, bold - for maximum attention
        - professional: Clean, subtle, business-appropriate
        - minimal: Simple, elegant, less is more
        - energetic: Bright red text, high energy, exciting
        - mystery: Blue tones, intrigue, curiosity
        - educational: Blue/white, clear, trustworthy

    Best Practices:
        - Keep text under 4 words
        - Show expressive faces (surprised = +41% CTR)
        - Use high contrast colors
        - Close-up shots (faces 40-60% of frame)
        - Test multiple variations (A/B testing can double CTR)

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/thumbnail/create" \\
          -F "video=@myvideo.mp4" \\
          -F "text=SHOCKING!" \\
          -F "style=viral" \\
          -F "platform=youtube"
        ```
    """
    if ThumbnailGenerator is None:
        raise HTTPException(
            status_code=500,
            detail="Thumbnail generator not available. Install: uv add moviepy pillow opencv-python"
        )

    # Validate style
    valid_styles = ["viral", "professional", "minimal", "energetic", "mystery", "educational"]
    if style not in valid_styles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}"
        )

    # Validate platform
    valid_platforms = ["youtube", "tiktok", "instagram", "facebook", "twitter", "linkedin"]
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_thumbnails"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        video_path = temp_dir / f"source_{video.filename}"
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Generate output path
        output_filename = f"thumbnail_{platform}_{style}.jpg"
        output_path = temp_dir / output_filename

        # Create thumbnail
        generator = ThumbnailGenerator()
        result_path = generator.create_thumbnail(
            video_path=str(video_path),
            output_path=str(output_path),
            text=text,
            style=style,
            platform=platform,
            frame_time=frame_time,
            auto_select_frame=auto_select_frame
        )

        # Get file size
        file_size_mb = os.path.getsize(result_path) / (1024 * 1024)

        # Cleanup source video
        os.remove(video_path)

        return ThumbnailCreateResponse(
            success=True,
            message="Thumbnail created successfully",
            thumbnail_path=str(result_path),
            download_url=f"/api/thumbnail/download/{output_filename}",
            file_size_mb=round(file_size_mb, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating thumbnail: {str(e)}")


@router.post("/ab-test", response_model=ThumbnailABTestResponse)
async def create_ab_test_thumbnails(
    video: UploadFile = File(...),
    text_variations: str = Form(...),  # Comma-separated
    style: str = Form("viral"),
    platform: str = Form("youtube"),
    analyze: bool = Form(True)
):
    """
    Create multiple thumbnail variations for A/B testing.

    A/B testing thumbnails can double your CTR! Upload one video and get
    multiple thumbnail variations to test which performs best.

    Args:
        video: Video file
        text_variations: Comma-separated text options (e.g., "SHOCKING,WOW,UNBELIEVABLE")
        style: Thumbnail style
        platform: Target platform
        analyze: Include quality analysis for each variation

    Returns:
        List of thumbnails with optional scoring

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/thumbnail/ab-test" \\
          -F "video=@myvideo.mp4" \\
          -F "text_variations=SHOCKING,UNBELIEVABLE,MUST SEE" \\
          -F "style=viral" \\
          -F "platform=youtube" \\
          -F "analyze=true"
        ```
    """
    if ThumbnailGenerator is None:
        raise HTTPException(
            status_code=500,
            detail="Thumbnail generator not available"
        )

    # Parse text variations
    texts = [t.strip() for t in text_variations.split(",")]
    if len(texts) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 text variations required for A/B testing"
        )

    if len(texts) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 variations for A/B testing"
        )

    try:
        # Create temp directories
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_thumbnails"
        temp_dir.mkdir(exist_ok=True)

        output_dir = temp_dir / "ab_test"
        output_dir.mkdir(exist_ok=True)

        # Save uploaded video
        video_path = temp_dir / f"source_{video.filename}"
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Create variations
        generator = ThumbnailGenerator()
        thumbnail_paths = generator.create_ab_test_variations(
            video_path=str(video_path),
            output_dir=str(output_dir),
            text_variations=texts,
            style=style,
            platform=platform
        )

        # Generate download URLs
        download_urls = [
            f"/api/thumbnail/download/{Path(p).name}"
            for p in thumbnail_paths
        ]

        # Analyze if requested
        scores_response = None
        winner = None
        if analyze:
            scores = []
            for i, path in enumerate(thumbnail_paths):
                variant_id = f"variant_{chr(65 + i)}"  # A, B, C, etc.
                score = generator.analyze_thumbnail(path, variant_id=variant_id)
                scores.append(ThumbnailScoreResponse(
                    success=True,
                    **score.to_dict()
                ))

            scores_response = scores

            # Find winner
            best_score = max(scores, key=lambda s: s.overall_score)
            winner = best_score.variant_id

        # Cleanup source video
        os.remove(video_path)

        return ThumbnailABTestResponse(
            success=True,
            winner=winner,
            thumbnails=[Path(p).name for p in thumbnail_paths],
            download_urls=download_urls,
            scores=scores_response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating A/B test: {str(e)}")


@router.post("/analyze", response_model=ThumbnailScoreResponse)
async def analyze_thumbnail(
    thumbnail: UploadFile = File(...)
):
    """
    Analyze thumbnail quality and get recommendations.

    Upload an existing thumbnail to get quality score and actionable
    recommendations for improvement.

    Args:
        thumbnail: Thumbnail image file

    Returns:
        Quality score (0-100) with recommendations

    Scoring Factors:
        - Face presence and size (35%)
        - Contrast and vibrancy (25%)
        - Emotion/expression (25%)
        - Composition (15%)

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/thumbnail/analyze" \\
          -F "thumbnail=@mythumb.jpg"
        ```
    """
    if ThumbnailGenerator is None:
        raise HTTPException(
            status_code=500,
            detail="Thumbnail generator not available"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_thumbnails"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded thumbnail
        thumb_path = temp_dir / f"analyze_{thumbnail.filename}"
        with open(thumb_path, "wb") as f:
            content = await thumbnail.read()
            f.write(content)

        # Analyze
        generator = ThumbnailGenerator()
        score = generator.analyze_thumbnail(str(thumb_path))

        # Cleanup
        os.remove(thumb_path)

        return ThumbnailScoreResponse(
            success=True,
            **score.to_dict()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing thumbnail: {str(e)}")


@router.get("/download/{filename}")
async def download_thumbnail(filename: str):
    """
    Download generated thumbnail.

    Args:
        filename: Thumbnail file name

    Returns:
        Thumbnail image file
    """
    temp_dir = Path(tempfile.gettempdir()) / "media_empire_thumbnails"

    # Check both root and ab_test subdirectory
    file_path = temp_dir / filename
    if not file_path.exists():
        file_path = temp_dir / "ab_test" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(
        path=str(file_path),
        media_type="image/jpeg",
        filename=filename
    )


@router.get("/styles")
async def list_styles():
    """
    List available thumbnail styles with descriptions.

    Returns:
        Available styles and their use cases

    Example:
        ```bash
        curl "http://localhost:8000/api/thumbnail/styles"
        ```
    """
    styles = {
        "viral": {
            "name": "Viral",
            "description": "Yellow text with high contrast and bold styling",
            "best_for": ["TikTok", "YouTube Shorts", "Instagram Reels"],
            "example_use": "Attention-grabbing content, trending topics, shocking reveals",
            "colors": "Yellow text on dark background with black outline"
        },
        "professional": {
            "name": "Professional",
            "description": "Clean, subtle, business-appropriate",
            "best_for": ["LinkedIn", "Corporate YouTube", "Business content"],
            "example_use": "Educational content, business updates, professional tutorials",
            "colors": "White text with subtle black outline"
        },
        "minimal": {
            "name": "Minimal",
            "description": "Simple, elegant, less is more",
            "best_for": ["Artistic content", "Photography", "Design"],
            "example_use": "Aesthetic content, portfolios, creative work",
            "colors": "White text, no outline, clean composition"
        },
        "energetic": {
            "name": "Energetic",
            "description": "Bright red text with high energy and excitement",
            "best_for": ["Gaming", "Sports", "Action content"],
            "example_use": "Gaming highlights, sports clips, high-energy content",
            "colors": "Bright red text with white outline"
        },
        "mystery": {
            "name": "Mystery",
            "description": "Blue tones with intrigue and curiosity",
            "best_for": ["Story-telling", "Mystery", "Drama"],
            "example_use": "Unsolved mysteries, story-time, dramatic reveals",
            "colors": "Light blue text with dark blue outline"
        },
        "educational": {
            "name": "Educational",
            "description": "Blue/white tones, clear and trustworthy",
            "best_for": ["Tutorials", "How-to", "Explanations"],
            "example_use": "Educational videos, tutorials, how-to guides",
            "colors": "Blue text with white outline"
        }
    }

    return {
        "styles": styles,
        "total": len(styles)
    }


@router.get("/best-practices")
async def get_best_practices(platform: str = "youtube"):
    """
    Get thumbnail best practices for a specific platform.

    Args:
        platform: Target platform (youtube, tiktok, instagram, etc.)

    Returns:
        Platform-specific best practices and tips

    Example:
        ```bash
        curl "http://localhost:8000/api/thumbnail/best-practices?platform=youtube"
        ```
    """
    best_practices = {
        "youtube": {
            "dimensions": "1280x720 (16:9)",
            "max_file_size": "2 MB",
            "formats": ["JPG", "PNG"],
            "text_limit": "3-4 words maximum",
            "tips": [
                "Show expressive faces (surprised/shocked = +41% CTR)",
                "Use high contrast colors (yellow on dark works best)",
                "Face should fill 40-60% of thumbnail",
                "Keep text large and readable on mobile",
                "Test at small size (thumbnails often viewed small)",
                "Use close-up shots, not wide angles",
                "Avoid clutter - single focal point",
                "Match thumbnail to video content (no clickbait)"
            ],
            "avoid": [
                "Too much text",
                "Low contrast",
                "Small faces",
                "Blurry images",
                "Misleading clickbait",
                "Text-only thumbnails"
            ],
            "examples": [
                "❌ Wide shot with tiny person",
                "✅ Close-up of surprised face + '3 SECRETS' text",
                "❌ Paragraph of text",
                "✅ 2-3 words max in large font"
            ]
        },
        "tiktok": {
            "dimensions": "1080x1920 (9:16)",
            "max_file_size": "5 MB",
            "formats": ["JPG", "PNG"],
            "text_limit": "1-2 words",
            "tips": [
                "Show action/movement in thumbnail",
                "Use vertical format (9:16)",
                "Bright, vibrant colors",
                "Face close-ups work best",
                "Keep very simple (viewed quickly)"
            ],
            "avoid": [
                "Too much detail",
                "Horizontal framing",
                "Dull colors"
            ],
            "examples": []
        },
        "instagram": {
            "dimensions": "1080x1080 (1:1)",
            "max_file_size": "8 MB",
            "formats": ["JPG", "PNG"],
            "text_limit": "2-3 words",
            "tips": [
                "Use square format (1:1)",
                "Aesthetic > clickbait",
                "Match feed aesthetic",
                "High quality images",
                "Consistent style across posts"
            ],
            "avoid": [
                "Low quality",
                "Inconsistent style",
                "Too busy"
            ],
            "examples": []
        }
    }

    platform_lower = platform.lower()
    if platform_lower not in best_practices:
        return {
            "platform": platform,
            "error": "Platform not found",
            "available_platforms": list(best_practices.keys())
        }

    return {
        "platform": platform,
        **best_practices[platform_lower]
    }


@router.get("/stats")
async def get_thumbnail_stats():
    """
    Get thumbnail impact statistics.

    Returns:
        Key stats about thumbnail importance

    Stats:
        - Thumbnails determine 90% of clicks
        - Good thumbnail = 10x more views
        - Faces in thumbnails = +38% CTR
        - Surprised/shocked faces = +41% CTR
        - A/B testing can double CTR
    """
    return {
        "importance": {
            "click_through_rate_impact": "90%",
            "description": "Thumbnails determine 90% of whether someone clicks"
        },
        "view_multiplier": {
            "factor": "10x",
            "description": "Good thumbnails can get 10x more views"
        },
        "face_impact": {
            "increase": "+38%",
            "description": "Thumbnails with faces get 38% higher CTR"
        },
        "emotion_impact": {
            "increase": "+41%",
            "description": "Surprised/shocked facial expressions increase CTR by 41%"
        },
        "ab_testing": {
            "improvement": "2x",
            "description": "A/B testing thumbnails can double your CTR"
        },
        "optimal_composition": {
            "face_size": "40-60% of frame",
            "text_length": "Under 4 words",
            "contrast": "High contrast colors (yellow on dark)",
            "expression": "Surprised, shocked, or excited"
        }
    }
