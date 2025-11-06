"""
Film Generation API routes - Professional cinematic prompt generation.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import film prompt system
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from features.film.prompts.builder import CinematicPromptBuilder
from features.film.prompts.styles import list_all_styles, get_style, search_styles
from features.film.prompts.shot_types import get_shot_type, get_shot_by_purpose, get_recommended_shot_sequence
from features.film.prompts.lighting import get_lighting, find_lighting_by_mood, get_lighting_for_time_of_day
from features.film.prompts.emotions import get_emotion, find_emotions_by_energy, get_complementary_emotions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/film", tags=["film"])


# ============================================================================
# Request/Response Models
# ============================================================================

class GenerateShotRequest(BaseModel):
    """Request to generate single shot prompt."""
    subject: str = Field(..., description="Subject/character description")
    action: str = Field(..., description="Action or story beat")
    location: str = Field(..., description="Location and setting")
    style: str = Field("hollywood_blockbuster", description="Cinematic style")
    shotType: str = Field("medium_shot", description="Shot type")
    lighting: str = Field("three_point_studio", description="Lighting setup")
    emotion: str = Field("contemplation_reflection", description="Emotional beat")
    additionalDetails: Optional[str] = Field(None, description="Additional details")
    characterConsistency: Optional[str] = Field(None, description="Character consistency reference")
    cameraMotion: Optional[str] = Field(None, description="Camera movement")
    aiEnhance: bool = Field(False, description="Enable AI post-processing enhancement")


class GenerateSceneRequest(BaseModel):
    """Request to generate complete scene."""
    scene_description: str = Field(..., description="Scene description")
    characters: List[str] = Field(..., description="List of characters")
    location: str = Field(..., description="Location")
    num_shots: int = Field(5, ge=1, le=20, description="Number of shots")
    style: str = Field("hollywood_blockbuster", description="Cinematic style")
    pacing: str = Field("medium", description="Scene pacing (slow/medium/dynamic/action)")
    aiEnhance: bool = Field(False, description="Enable AI post-processing enhancement")


class EnhancePromptRequest(BaseModel):
    """Request to enhance existing prompt."""
    prompt: str = Field(..., description="Original prompt to enhance")
    style: str = Field("hollywood_blockbuster", description="Target style")
    focus: Optional[str] = Field(None, description="Enhancement focus (visual/emotion/technical/all)")


# ============================================================================
# Prompt Generation Endpoints
# ============================================================================

@router.post("/generate-shot")
async def generate_shot(request: GenerateShotRequest):
    """
    Generate professional cinematic prompt for a single shot.

    Returns detailed prompt with director's notes and technical specifications.
    """
    try:
        builder = CinematicPromptBuilder()

        # Generate base prompt
        result = builder.build_shot(
            subject=request.subject,
            action=request.action,
            location=request.location,
            style=request.style,
            shot_type=request.shotType,
            lighting=request.lighting,
            emotion=request.emotion,
            additional_details=request.additionalDetails,
            character_consistency=request.characterConsistency,
            camera_motion=request.cameraMotion
        )

        # Convert to dict
        response = {
            "prompt": result.prompt,
            "negative_prompt": result.negative_prompt,
            "metadata": result.metadata,
            "director_notes": result.director_notes,
            "technical_notes": result.technical_notes
        }

        # AI Enhancement if requested
        if request.aiEnhance:
            enhanced = await enhance_prompt_with_ai(
                prompt=result.prompt,
                style=request.style,
                focus="all"
            )
            response["prompt"] = enhanced["enhanced_prompt"]
            response["ai_enhanced"] = True
            response["original_prompt"] = result.prompt

        return response

    except Exception as e:
        logger.error(f"Error generating shot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-scene")
async def generate_scene(request: GenerateSceneRequest):
    """
    Generate complete scene with professional shot coverage.

    Returns sequence of shots with proper cinematic coverage.
    """
    try:
        builder = CinematicPromptBuilder()

        # Generate scene sequence
        scene_shots = builder.build_scene_sequence(
            scene_description=request.scene_description,
            characters=request.characters,
            location=request.location,
            num_shots=request.num_shots,
            style=request.style,
            pacing=request.pacing
        )

        # Convert to list of dicts
        shots = []
        for idx, shot in enumerate(scene_shots, 1):
            shot_data = {
                "shot_number": idx,
                "prompt": shot.prompt,
                "negative_prompt": shot.negative_prompt,
                "metadata": shot.metadata,
                "duration_seconds": shot.metadata.get("duration", 3)
            }

            # AI Enhancement if requested
            if request.aiEnhance:
                enhanced = await enhance_prompt_with_ai(
                    prompt=shot.prompt,
                    style=request.style,
                    focus="all"
                )
                shot_data["prompt"] = enhanced["enhanced_prompt"]
                shot_data["ai_enhanced"] = True
                shot_data["original_prompt"] = shot.prompt

            shots.append(shot_data)

        return {
            "shots": shots,
            "total_duration": sum(s["duration_seconds"] for s in shots),
            "style": request.style,
            "pacing": request.pacing
        }

    except Exception as e:
        logger.error(f"Error generating scene: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance-prompt")
async def enhance_prompt(request: EnhancePromptRequest):
    """
    Enhance existing prompt using AI post-processing.

    Takes a good prompt and makes it even better with more cinematic detail,
    creative direction, and professional polish.
    """
    try:
        enhanced = await enhance_prompt_with_ai(
            prompt=request.prompt,
            style=request.style,
            focus=request.focus or "all"
        )

        return enhanced

    except Exception as e:
        logger.error(f"Error enhancing prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI Enhancement Helper
# ============================================================================

async def enhance_prompt_with_ai(prompt: str, style: str, focus: str = "all") -> dict:
    """
    Use GPT to enhance prompt with additional cinematic detail.

    Args:
        prompt: Original prompt
        style: Cinematic style
        focus: Enhancement focus (visual/emotion/technical/all)

    Returns:
        Dict with enhanced_prompt and enhancement_notes
    """
    try:
        from openai import AsyncOpenAI
        from config import CONFIG

        client = AsyncOpenAI(api_key=CONFIG.get("OPEN_AI_API_KEY"))

        # Get style information for context
        style_obj = get_style(style)

        focus_instructions = {
            "visual": "Focus on enhancing visual details, cinematography, and composition.",
            "emotion": "Focus on deepening emotional resonance and character performance.",
            "technical": "Focus on technical precision, camera work, and lighting details.",
            "all": "Enhance all aspects: visual beauty, emotional depth, and technical precision."
        }

        system_prompt = f"""You are a world-class cinematographer and director with expertise from masters like Roger Deakins, Emmanuel Lubezki, and Greig Fraser.

Your task is to take an already professional cinematic prompt and enhance it further with:
- More vivid and precise visual language
- Deeper sensory details (not just what's seen, but implied atmosphere)
- Stronger emotional resonance
- More specific technical direction
- Creative metaphors and visual poetry

Style Context: {style_obj.name}
- Description: {style_obj.description}
- Mood: {style_obj.mood}
- Reference Films: {', '.join(style_obj.reference_films)}

Enhancement Focus: {focus_instructions.get(focus, focus_instructions['all'])}

Rules:
1. Keep the core subject, action, and location intact
2. Add 20-40% more detail and specificity
3. Use professional cinematography terminology
4. Maintain the original style's aesthetic
5. Make it more evocative and cinematic
6. Don't change the fundamental shot - enhance it
7. Output ONLY the enhanced prompt, no explanations"""

        user_prompt = f"""Original Prompt:
{prompt}

Enhance this prompt to be even more cinematic, detailed, and professionally directed."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=800
        )

        enhanced_prompt = response.choices[0].message.content.strip()

        return {
            "enhanced_prompt": enhanced_prompt,
            "original_prompt": prompt,
            "enhancement_notes": [
                f"Enhanced with AI using {response.model}",
                f"Focus: {focus}",
                f"Style: {style_obj.name}",
                f"Added approximately {len(enhanced_prompt) - len(prompt)} characters of detail"
            ]
        }

    except Exception as e:
        logger.error(f"AI enhancement failed: {e}")
        # Fallback to original prompt if AI fails
        return {
            "enhanced_prompt": prompt,
            "original_prompt": prompt,
            "enhancement_notes": [f"AI enhancement failed: {str(e)}. Using original prompt."]
        }


# ============================================================================
# Reference Data Endpoints
# ============================================================================

@router.get("/styles")
async def list_styles():
    """List all available cinematic styles."""
    styles = list_all_styles()
    return {"styles": styles}


@router.get("/styles/{style_name}")
async def get_style_details(style_name: str):
    """Get details for specific style."""
    try:
        style = get_style(style_name)
        return style.dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/styles/search")
async def search_styles_endpoint(mood: Optional[str] = None, keyword: Optional[str] = None):
    """Search styles by mood or keyword."""
    results = search_styles(mood=mood, keyword=keyword)
    return {"results": [s.dict() for s in results]}


@router.get("/shot-types/{shot_name}")
async def get_shot_type_details(shot_name: str):
    """Get details for specific shot type."""
    try:
        shot = get_shot_type(shot_name)
        return shot.dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/shot-types/by-purpose/{purpose}")
async def find_shots_by_purpose(purpose: str):
    """Find shot types by purpose keyword."""
    results = get_shot_by_purpose(purpose)
    return {"results": [s.dict() for s in results]}


@router.get("/shot-sequences/{pacing}")
async def get_shot_sequence(pacing: str):
    """Get recommended shot sequence for pacing."""
    sequence = get_recommended_shot_sequence(pacing)
    return {"sequence": sequence, "pacing": pacing}


@router.get("/lighting/{setup_name}")
async def get_lighting_details(setup_name: str):
    """Get details for specific lighting setup."""
    try:
        lighting = get_lighting(setup_name)
        return lighting.dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/lighting/by-mood/{mood}")
async def find_lighting_by_mood_endpoint(mood: str):
    """Find lighting setups by mood."""
    results = find_lighting_by_mood(mood)
    return {"results": [l.dict() for l in results]}


@router.get("/lighting/by-time/{time}")
async def get_lighting_by_time(time: str):
    """Get lighting setups for time of day."""
    results = get_lighting_for_time_of_day(time)
    return {"results": [l.dict() for l in results]}


@router.get("/emotions/{emotion_name}")
async def get_emotion_details(emotion_name: str):
    """Get details for specific emotion."""
    try:
        emotion = get_emotion(emotion_name)
        return emotion.dict()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/emotions/by-energy/{energy}")
async def find_emotions_by_energy_endpoint(energy: str):
    """Find emotions by energy level."""
    results = find_emotions_by_energy(energy)
    return {"results": [e.dict() for e in results]}


@router.get("/emotions/{emotion_name}/complementary")
async def get_complementary_emotions_endpoint(emotion_name: str):
    """Get emotions that work well in sequence."""
    results = get_complementary_emotions(emotion_name)
    return {"complementary": results}
