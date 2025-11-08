"""
API endpoints for hook optimization and analysis.

Note: This router expects features.video module to be importable.
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
    from features.video.hook_optimizer import HookOptimizer, HookScore, Platform
except ImportError:
    HookOptimizer = None


router = APIRouter(prefix="/api/hook", tags=["hook_optimizer"])


# Request/Response Models

class PlatformEnum(str, Enum):
    """Supported platforms"""
    tiktok = "tiktok"
    youtube_shorts = "youtube_shorts"
    instagram_reels = "instagram_reels"
    youtube = "youtube"
    generic = "generic"


class HookAnalysisResponse(BaseModel):
    """Hook analysis response"""
    success: bool
    overall_score: float
    grade: str
    visual_score: float
    text_score: float
    audio_score: float
    motion_score: float
    color_impact: float
    face_presence: float
    text_hook_strength: float
    curiosity_gap: float
    voice_energy: float
    hook_type: str
    pattern_interrupts: List[str] = []
    power_words: List[str] = []
    recommendations: List[str] = []
    warnings: List[str] = []
    variant_id: Optional[str] = None


class HookComparisonResponse(BaseModel):
    """Hook comparison response"""
    success: bool
    winner: str
    results: List[HookAnalysisResponse]
    summary: Dict[str, any]


class HookVariationResponse(BaseModel):
    """Hook variation generation response"""
    success: bool
    variations: List[str]
    download_urls: List[str]


# Endpoints

@router.post("/analyze", response_model=HookAnalysisResponse)
async def analyze_hook(
    video: UploadFile = File(...),
    text: Optional[str] = Form(None),
    platform: PlatformEnum = Form(PlatformEnum.generic),
    hook_duration: float = Form(3.0)
):
    """
    Analyze video hook (first 3 seconds) for retention optimization.

    The first 3 seconds are CRITICAL:
    - 65% of viewers decide in first 2 seconds
    - 80% decision made by 3 seconds
    - Strong hooks = 2-5x higher retention

    Args:
        video: Video file to analyze
        text: Hook text/script (first few words)
        platform: Target platform (tiktok, youtube_shorts, instagram_reels, youtube, generic)
        hook_duration: Duration to analyze in seconds (default 3.0)

    Returns:
        Detailed hook analysis with score and recommendations

    Scoring:
        - 90-100 (A+): Excellent hook, very likely to retain viewers
        - 80-89 (A/B+): Good hook, should perform well
        - 70-79 (B/C+): Decent hook, room for improvement
        - 60-69 (C/D): Weak hook, needs work
        - <60 (F): Poor hook, reshoot recommended

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/hook/analyze" \\
          -F "video=@myvideo.mp4" \\
          -F "text=Did you know this iPhone trick?" \\
          -F "platform=tiktok"
        ```
    """
    if HookOptimizer is None:
        raise HTTPException(
            status_code=500,
            detail="Hook optimizer not available. Install: uv add moviepy opencv-python numpy"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_hooks"
        temp_dir.mkdir(exist_ok=True)

        # Save uploaded video
        video_path = temp_dir / f"hook_analysis_{video.filename}"
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Analyze hook
        optimizer = HookOptimizer()
        score = optimizer.analyze_hook(
            video_path=str(video_path),
            text=text,
            platform=platform.value,
            hook_duration=hook_duration
        )

        # Cleanup
        os.remove(video_path)

        # Convert to response
        return HookAnalysisResponse(
            success=True,
            **score.to_dict()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing hook: {str(e)}")


@router.post("/compare", response_model=HookComparisonResponse)
async def compare_hooks(
    videos: List[UploadFile] = File(...),
    texts: Optional[str] = Form(None),  # Comma-separated
    platform: PlatformEnum = Form(PlatformEnum.generic)
):
    """
    Compare multiple hook variations for A/B testing.

    Upload 2-5 different hook variations and get a ranked comparison
    to determine which performs best.

    Args:
        videos: List of video files (2-5 variations)
        texts: Comma-separated hook texts (optional)
        platform: Target platform

    Returns:
        Ranked comparison with winner and detailed scores

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/hook/compare" \\
          -F "videos=@hook_a.mp4" \\
          -F "videos=@hook_b.mp4" \\
          -F "videos=@hook_c.mp4" \\
          -F "texts=Did you know...,Watch this...,Check out..." \\
          -F "platform=tiktok"
        ```
    """
    if HookOptimizer is None:
        raise HTTPException(
            status_code=500,
            detail="Hook optimizer not available"
        )

    if len(videos) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 videos required for comparison"
        )

    if len(videos) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 videos for comparison"
        )

    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_hooks"
        temp_dir.mkdir(exist_ok=True)

        # Parse texts
        text_list = None
        if texts:
            text_list = [t.strip() for t in texts.split(",")]
            if len(text_list) != len(videos):
                raise HTTPException(
                    status_code=400,
                    detail=f"Number of texts ({len(text_list)}) must match number of videos ({len(videos)})"
                )

        # Save uploaded videos
        video_paths = []
        for i, video in enumerate(videos):
            video_path = temp_dir / f"compare_{i}_{video.filename}"
            with open(video_path, "wb") as f:
                content = await video.read()
                f.write(content)
            video_paths.append(str(video_path))

        # Compare hooks
        optimizer = HookOptimizer()
        scores = optimizer.compare_hooks(
            video_paths=video_paths,
            texts=text_list,
            platform=platform.value
        )

        # Cleanup
        for path in video_paths:
            os.remove(path)

        # Convert to response
        results = [
            HookAnalysisResponse(success=True, **score.to_dict())
            for score in scores
        ]

        # Summary
        summary = {
            "winner_variant": scores[0].variant_id,
            "winner_score": round(scores[0].overall_score, 1),
            "score_range": round(scores[0].overall_score - scores[-1].overall_score, 1),
            "avg_score": round(sum(s.overall_score for s in scores) / len(scores), 1),
            "top_recommendations": scores[0].recommendations[:3]
        }

        return HookComparisonResponse(
            success=True,
            winner=scores[0].variant_id,
            results=results,
            summary=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing hooks: {str(e)}")


@router.post("/generate-variations", response_model=HookVariationResponse)
async def generate_hook_variations(
    video: UploadFile = File(...),
    num_variations: int = Form(3)
):
    """
    Generate hook variations with different effects for A/B testing.

    Creates multiple variations of the same hook with different speeds,
    zooms, and effects to test which performs best.

    Args:
        video: Source video file
        num_variations: Number of variations to create (2-5)

    Returns:
        List of variation file URLs

    Variations created:
        1. Original
        2. 10% faster
        3. Slight zoom (1.05x)
        4. Faster + zoom

    Example:
        ```bash
        curl -X POST "http://localhost:8000/api/hook/generate-variations" \\
          -F "video=@source.mp4" \\
          -F "num_variations=4"
        ```
    """
    if HookOptimizer is None:
        raise HTTPException(
            status_code=500,
            detail="Hook optimizer not available"
        )

    if num_variations < 2 or num_variations > 5:
        raise HTTPException(
            status_code=400,
            detail="num_variations must be between 2 and 5"
        )

    try:
        # Create temp directories
        temp_dir = Path(tempfile.gettempdir()) / "media_empire_hooks"
        temp_dir.mkdir(exist_ok=True)

        output_dir = temp_dir / "variations"
        output_dir.mkdir(exist_ok=True)

        # Save uploaded video
        video_path = temp_dir / f"source_{video.filename}"
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)

        # Create variations
        variations = [
            {"speed": 1.0, "zoom": 1.0, "name": "original"},
            {"speed": 1.1, "zoom": 1.0, "name": "faster"},
            {"speed": 1.0, "zoom": 1.05, "name": "zoom"},
            {"speed": 1.1, "zoom": 1.05, "name": "faster_zoom"},
            {"speed": 1.2, "zoom": 1.0, "name": "very_fast"}
        ][:num_variations]

        optimizer = HookOptimizer()
        output_paths = optimizer.create_hook_variations(
            video_path=str(video_path),
            output_dir=str(output_dir),
            variations=variations
        )

        # Cleanup source
        os.remove(video_path)

        # Generate download URLs
        download_urls = [
            f"/api/hook/download-variation/{Path(p).name}"
            for p in output_paths
        ]

        return HookVariationResponse(
            success=True,
            variations=[Path(p).name for p in output_paths],
            download_urls=download_urls
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating variations: {str(e)}")


@router.get("/download-variation/{filename}")
async def download_variation(filename: str):
    """
    Download generated hook variation.

    Args:
        filename: Variation file name

    Returns:
        Video file for download
    """
    temp_dir = Path(tempfile.gettempdir()) / "media_empire_hooks" / "variations"
    file_path = temp_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=filename
    )


@router.get("/best-practices")
async def get_best_practices(platform: PlatformEnum = PlatformEnum.generic):
    """
    Get best practices for creating effective hooks.

    Args:
        platform: Target platform

    Returns:
        Platform-specific best practices and tips

    Example:
        ```bash
        curl "http://localhost:8000/api/hook/best-practices?platform=tiktok"
        ```
    """
    best_practices = {
        "tiktok": {
            "optimal_duration": "2-3 seconds",
            "tips": [
                "Start with a question to create curiosity",
                "Use fast-paced editing and quick cuts",
                "Show results/transformation immediately",
                "Use trending sounds or music",
                "Add text overlay in first frame",
                "Create pattern interrupt (unexpected action)",
                "Show emotion or excitement in thumbnail",
                "Use power words: 'secret', 'hack', 'trick', 'hidden'"
            ],
            "avoid": [
                "Slow intros or setup",
                "Asking viewers to subscribe first",
                "Generic greetings ('Hey guys!')",
                "Long explanations before value"
            ],
            "examples": [
                "❌ 'Hey everyone, welcome back to my channel...'",
                "✅ 'This iPhone trick will blow your mind!'",
                "❌ 'In this video I'm going to show you...'",
                "✅ 'Watch what happens when I drop this...'"
            ]
        },
        "youtube_shorts": {
            "optimal_duration": "3 seconds",
            "tips": [
                "Hook with question or bold statement",
                "Show the payoff early",
                "Use clear, readable text overlays",
                "Create curiosity gap (what happens next?)",
                "Leverage trending topics/challenges",
                "Start with action or result",
                "Use dynamic camera movements"
            ],
            "avoid": [
                "Channel intros in shorts",
                "Slow pacing",
                "Too much setup",
                "Asking for likes first"
            ],
            "examples": [
                "❌ 'Today I'm going to teach you about...'",
                "✅ 'Did you know your phone can do THIS?'",
                "❌ 'Before we start, please subscribe...'",
                "✅ '3 secrets your dentist doesn't tell you'"
            ]
        },
        "instagram_reels": {
            "optimal_duration": "2-2.5 seconds",
            "tips": [
                "Strong visual hook in first frame",
                "Use trending audio",
                "Create 'scroll-stopper' moment",
                "Add engaging text in first frame",
                "Show transformation/before-after",
                "Use high energy and enthusiasm",
                "Leverage FOMO (fear of missing out)"
            ],
            "avoid": [
                "Talking head without action",
                "Slow reveals",
                "Generic content",
                "Poor lighting"
            ],
            "examples": [
                "❌ 'Hi friends, in today's reel...'",
                "✅ 'POV: You just discovered this makeup hack'",
                "❌ 'Let me tell you about my day...'",
                "✅ 'I tested viral recipes so you don't have to'"
            ]
        },
        "youtube": {
            "optimal_duration": "5-8 seconds",
            "tips": [
                "Tease the value/outcome",
                "Create curiosity about the topic",
                "Promise specific benefit",
                "Use pattern interrupt or surprise",
                "Show credibility/authority",
                "Preview most interesting part"
            ],
            "avoid": [
                "Long channel intros",
                "Irrelevant rambling",
                "Over-the-top clickbait",
                "Generic topic introduction"
            ],
            "examples": [
                "❌ 'What's up guys, it's [name] and welcome...'",
                "✅ 'This mistake cost me $10,000. Here's how to avoid it.'",
                "❌ 'Today we're talking about productivity...'",
                "✅ 'I tried every productivity app. Only one survived.'"
            ]
        },
        "generic": {
            "optimal_duration": "3 seconds",
            "tips": [
                "Start with value, not introduction",
                "Create immediate curiosity",
                "Use power words (secret, discover, trick)",
                "Show don't tell",
                "Promise specific outcome",
                "Use pattern interrupts"
            ],
            "avoid": [
                "Slow intros",
                "Generic greetings",
                "Setup without payoff",
                "Boring first frame"
            ],
            "examples": []
        }
    }

    return {
        "platform": platform.value,
        **best_practices.get(platform.value, best_practices["generic"])
    }


@router.get("/power-words")
async def get_power_words():
    """
    Get list of power words for creating effective hooks.

    Returns:
        Categorized list of power words

    Power word categories:
        - Curiosity: Creates intrigue and desire to learn more
        - Urgency: Creates FOMO and immediate action
        - Exclusivity: Makes viewer feel special/insider
        - Authority: Builds trust and credibility
        - Emotional: Triggers emotional response
        - Negative: Uses reverse psychology
        - Question: Prompts viewer engagement
    """
    from features.video.hook_optimizer import HookOptimizer

    return {
        "power_words": HookOptimizer.POWER_WORDS,
        "usage_tips": [
            "Use 1-2 power words per hook (more = diluted impact)",
            "Combine curiosity + urgency for max effect",
            "Match power words to your niche/audience",
            "Test different combinations in A/B tests",
            "Avoid overused words in your niche"
        ],
        "examples": {
            "curiosity": "This SECRET iPhone trick...",
            "urgency": "Do this NOW before...",
            "exclusivity": "ONLY 1% of people know...",
            "authority": "PROVEN method to...",
            "emotional": "This AMAZING discovery...",
            "negative": "STOP doing this mistake...",
            "question": "WHY does nobody talk about..."
        }
    }
