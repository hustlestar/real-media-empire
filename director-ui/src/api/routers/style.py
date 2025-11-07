"""
Visual style API endpoints for style management.

Supports:
- Style preset management (save, load, list)
- Reference image analysis
- Color palette extraction
- Camera settings presets
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import uuid
import logging
import json
import os
from PIL import Image
import colorsys

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================


class StyleReference(BaseModel):
    """Individual style reference"""
    id: str
    name: str
    category: Literal['cinematographer', 'director', 'genre', 'era', 'artist', 'custom']
    weight: float = Field(..., ge=0, le=100)
    description: Optional[str] = None
    keywords: List[str] = []


class ColorConfig(BaseModel):
    """Individual color in palette"""
    id: str
    name: str
    hex: str
    role: Literal['primary', 'secondary', 'accent', 'background', 'highlight']
    weight: float = Field(..., ge=0, le=100)


class ColorGrading(BaseModel):
    """Color grading settings"""
    temperature: int = Field(0, ge=-100, le=100)
    tint: int = Field(0, ge=-100, le=100)
    saturation: int = Field(100, ge=0, le=200)
    contrast: int = Field(100, ge=0, le=200)
    brightness: int = Field(0, ge=-100, le=100)
    shadows: str  # hex color
    midtones: str  # hex color
    highlights: str  # hex color


class CameraSettings(BaseModel):
    """Camera and lens settings"""
    focal_length: int = Field(50, ge=14, le=200)
    aperture: float = Field(2.8, ge=1.4, le=22)
    sensor: Literal['full-frame', 'super35', 'micro43', 'IMAX']
    depth_of_field: Literal['shallow', 'medium', 'deep']
    focus_distance: float = Field(3.0, ge=0.5, le=100)
    shot_size: Literal['extreme-closeup', 'closeup', 'medium', 'full', 'wide', 'extreme-wide']
    angle: Literal['low', 'eye-level', 'high', 'dutch', 'birds-eye', 'worms-eye']
    composition: Literal['centered', 'rule-of-thirds', 'golden-ratio', 'symmetric']
    movement: Literal['static', 'pan', 'tilt', 'dolly', 'crane', 'handheld', 'steadicam', 'drone']
    movement_speed: Literal['slow', 'medium', 'fast']
    bokeh: Literal['circular', 'hexagonal', 'anamorphic']
    lens_flares: bool = False
    vignette: int = Field(20, ge=0, le=100)


class ReferenceImageAnalysis(BaseModel):
    """Analysis results for reference image"""
    dominant_colors: List[str]  # hex colors
    mood: str
    composition: str
    lighting: str
    keywords: List[str]


class StylePreset(BaseModel):
    """Complete visual style preset"""
    id: str
    name: str
    description: Optional[str] = None
    style_references: List[StyleReference] = []
    color_palette: List[ColorConfig] = []
    color_grading: Optional[ColorGrading] = None
    camera_settings: Optional[CameraSettings] = None
    created_at: datetime
    updated_at: datetime


class CreateStylePresetRequest(BaseModel):
    """Request to create style preset"""
    name: str
    description: Optional[str] = None
    style_references: List[StyleReference] = []
    color_palette: List[ColorConfig] = []
    color_grading: Optional[ColorGrading] = None
    camera_settings: Optional[CameraSettings] = None


class StylePresetResponse(BaseModel):
    """Response with style preset"""
    preset: StylePreset


class StylePresetsListResponse(BaseModel):
    """Response with list of style presets"""
    presets: List[StylePreset]
    total: int


class ImageAnalysisResponse(BaseModel):
    """Response with image analysis"""
    analysis: ReferenceImageAnalysis


# ============================================================================
# Helper Functions
# ============================================================================


def extract_dominant_colors(image_path: str, num_colors: int = 5) -> List[str]:
    """
    Extract dominant colors from image using PIL.

    Returns list of hex color strings.
    """
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        img = img.resize((150, 150))  # Resize for performance

        # Get all pixels
        pixels = list(img.getdata())

        # Simple color quantization - get most common colors
        from collections import Counter

        # Round colors to reduce variety
        rounded_pixels = [
            (r // 32 * 32, g // 32 * 32, b // 32 * 32)
            for r, g, b in pixels
        ]

        # Count occurrences
        color_counts = Counter(rounded_pixels)
        most_common = color_counts.most_common(num_colors)

        # Convert to hex
        hex_colors = [
            '#{:02x}{:02x}{:02x}'.format(r, g, b)
            for (r, g, b), count in most_common
        ]

        return hex_colors

    except Exception as e:
        logger.error(f"Color extraction failed: {e}")
        return ['#000000', '#808080', '#ffffff']  # Default fallback


def analyze_image_mood(dominant_colors: List[str]) -> str:
    """
    Analyze mood based on dominant colors.

    Simplified heuristic based on color temperature and saturation.
    """
    # Convert hex to HSV
    hsvs = []
    for hex_color in dominant_colors:
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hsvs.append((h, s, v))

    # Average hue, saturation, value
    avg_h = sum(h for h, s, v in hsvs) / len(hsvs)
    avg_s = sum(s for h, s, v in hsvs) / len(hsvs)
    avg_v = sum(v for h, s, v in hsvs) / len(hsvs)

    # Determine mood
    if avg_s < 0.2:
        return "Monochromatic and minimalist"
    elif avg_v < 0.3:
        return "Dark and moody"
    elif avg_h < 0.1 or avg_h > 0.9:  # Red/orange
        return "Warm and energetic"
    elif 0.45 < avg_h < 0.7:  # Blue/cyan
        return "Cool and calm"
    elif 0.15 < avg_h < 0.45:  # Yellow/green
        return "Vibrant and lively"
    else:
        return "Balanced and neutral"


def analyze_reference_image(image_path: str) -> ReferenceImageAnalysis:
    """
    Analyze reference image for visual characteristics.

    Extracts dominant colors, analyzes mood, composition, lighting.
    """
    try:
        # Extract dominant colors
        dominant_colors = extract_dominant_colors(image_path)

        # Analyze mood from colors
        mood = analyze_image_mood(dominant_colors)

        # Placeholder analysis (in production, use computer vision models)
        analysis = ReferenceImageAnalysis(
            dominant_colors=dominant_colors,
            mood=mood,
            composition="Balanced composition with clear focal point",
            lighting="Natural, diffused lighting with soft shadows",
            keywords=["cinematic", "atmospheric", "professional", "balanced"]
        )

        return analysis

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


# In-memory storage (in production, use database)
STYLE_PRESETS_STORAGE: Dict[str, StylePreset] = {}


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/presets", response_model=StylePresetResponse)
async def create_style_preset(request: CreateStylePresetRequest):
    """
    Create a new style preset.

    Saves all visual style settings including style references,
    color palette, color grading, and camera settings.
    """
    try:
        preset_id = str(uuid.uuid4())
        now = datetime.now()

        preset = StylePreset(
            id=preset_id,
            name=request.name,
            description=request.description,
            style_references=request.style_references,
            color_palette=request.color_palette,
            color_grading=request.color_grading,
            camera_settings=request.camera_settings,
            created_at=now,
            updated_at=now
        )

        STYLE_PRESETS_STORAGE[preset_id] = preset

        logger.info(f"Created style preset: {preset.name} ({preset_id})")

        return StylePresetResponse(preset=preset)

    except Exception as e:
        logger.error(f"Create preset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets", response_model=StylePresetsListResponse)
async def list_style_presets(
    category: Optional[str] = None,
    limit: int = 50
):
    """
    List all style presets.

    Optional filtering by category.
    """
    try:
        presets = list(STYLE_PRESETS_STORAGE.values())

        # Sort by updated_at descending
        presets.sort(key=lambda p: p.updated_at, reverse=True)

        # Apply limit
        presets = presets[:limit]

        return StylePresetsListResponse(
            presets=presets,
            total=len(STYLE_PRESETS_STORAGE)
        )

    except Exception as e:
        logger.error(f"List presets error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/{preset_id}", response_model=StylePresetResponse)
async def get_style_preset(preset_id: str):
    """Get style preset by ID."""
    preset = STYLE_PRESETS_STORAGE.get(preset_id)

    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")

    return StylePresetResponse(preset=preset)


@router.put("/presets/{preset_id}", response_model=StylePresetResponse)
async def update_style_preset(preset_id: str, request: CreateStylePresetRequest):
    """Update existing style preset."""
    if preset_id not in STYLE_PRESETS_STORAGE:
        raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")

    preset = STYLE_PRESETS_STORAGE[preset_id]

    # Update fields
    preset.name = request.name
    preset.description = request.description
    preset.style_references = request.style_references
    preset.color_palette = request.color_palette
    preset.color_grading = request.color_grading
    preset.camera_settings = request.camera_settings
    preset.updated_at = datetime.now()

    STYLE_PRESETS_STORAGE[preset_id] = preset

    logger.info(f"Updated style preset: {preset.name} ({preset_id})")

    return StylePresetResponse(preset=preset)


@router.delete("/presets/{preset_id}")
async def delete_style_preset(preset_id: str):
    """Delete style preset."""
    if preset_id not in STYLE_PRESETS_STORAGE:
        raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")

    deleted = STYLE_PRESETS_STORAGE.pop(preset_id)

    logger.info(f"Deleted style preset: {deleted.name} ({preset_id})")

    return {"success": True, "message": f"Preset {preset_id} deleted"}


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze reference image for visual characteristics.

    Extracts dominant colors, mood, composition, lighting.
    Returns analysis that can be used to guide generation.
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/ref_{uuid.uuid4()}_{file.filename}"

        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Analyze image
        analysis = analyze_reference_image(temp_path)

        # Clean up
        os.remove(temp_path)

        return ImageAnalysisResponse(analysis=analysis)

    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-prompt")
async def generate_style_prompt(preset_id: str):
    """
    Generate comprehensive style prompt from preset.

    Combines all style elements into a single prompt for image generation.
    """
    try:
        preset = STYLE_PRESETS_STORAGE.get(preset_id)

        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset {preset_id} not found")

        prompt_parts = []

        # Style references
        if preset.style_references:
            sorted_styles = sorted(preset.style_references, key=lambda s: s.weight, reverse=True)
            style_desc = ', '.join([
                f"{int(s.weight)}% {s.name}" for s in sorted_styles if s.weight > 5
            ])
            prompt_parts.append(f"Visual style: {style_desc}")

        # Color palette
        if preset.color_palette:
            color_names = [c.name for c in preset.color_palette if c.weight > 10]
            if color_names:
                prompt_parts.append(f"Color palette: {', '.join(color_names)}")

        # Color grading
        if preset.color_grading:
            grading = preset.color_grading
            temp_desc = "warm" if grading.temperature > 0 else "cool" if grading.temperature < 0 else "neutral"
            sat_desc = "saturated" if grading.saturation > 110 else "muted" if grading.saturation < 90 else "natural"
            contrast_desc = "high contrast" if grading.contrast > 110 else "low contrast" if grading.contrast < 90 else "balanced contrast"

            prompt_parts.append(f"{temp_desc} color temperature, {sat_desc} colors, {contrast_desc}")

        # Camera settings
        if preset.camera_settings:
            cam = preset.camera_settings
            prompt_parts.append(
                f"Shot on {cam.sensor} sensor with {cam.focal_length}mm lens at f/{cam.aperture}. "
                f"{cam.shot_size.replace('-', ' ')} shot from {cam.angle.replace('-', ' ')} angle. "
                f"{cam.depth_of_field} depth of field. "
                f"{cam.composition.replace('-', ' ')} composition."
            )

        # Combine
        final_prompt = '. '.join(prompt_parts)
        final_prompt += ". Professional cinematography, high production value, masterful composition."

        return {
            "preset_id": preset_id,
            "preset_name": preset.name,
            "prompt": final_prompt
        }

    except Exception as e:
        logger.error(f"Generate prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
