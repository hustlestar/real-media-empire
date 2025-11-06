"""
World-class cinematic prompt builder.
Acts as your personal film director and cinematographer.

This module combines professional knowledge from:
- Master cinematographers (Roger Deakins, Emmanuel Lubezki, Hoyte van Hoytema)
- Award-winning directors (Christopher Nolan, Denis Villeneuve, Alfonso Cuarón)
- Film production best practices
- Hollywood and independent cinema techniques
"""

from typing import Optional, List, Dict
from pydantic import BaseModel

from .styles import CINEMATIC_STYLES, CinematicStyle, get_style
from .shot_types import SHOT_COMPOSITIONS, ShotComposition, get_shot_type, get_recommended_shot_sequence
from .lighting import LIGHTING_SETUPS, LightingSetup, get_lighting
from .emotions import EMOTIONAL_BEATS, EmotionalBeat, get_emotion


class PromptResult(BaseModel):
    """Result from prompt builder"""
    prompt: str
    negative_prompt: str
    metadata: Dict
    technical_notes: str
    director_notes: str


class CinematicPromptBuilder:
    """
    Professional cinematic prompt builder.

    This class acts as your personal film director and cinematographer,
    building world-class prompts using professional filmmaking knowledge.

    Example:
        builder = CinematicPromptBuilder()

        result = builder.build_shot(
            subject="Emma, professional woman in her 30s",
            action="typing on laptop, discovering breakthrough moment",
            location="modern tech office, glass walls, city skyline visible",
            style="hollywood_blockbuster",
            shot_type="medium_closeup",
            lighting="golden_hour_exterior",
            emotion="triumph_victory"
        )

        print(result.prompt)
        print(result.director_notes)
    """

    def __init__(self):
        self.styles = CINEMATIC_STYLES
        self.shots = SHOT_COMPOSITIONS
        self.lighting = LIGHTING_SETUPS
        self.emotions = EMOTIONAL_BEATS

    def build_shot(
        self,
        subject: str,
        action: str,
        location: str,
        style: str = "hollywood_blockbuster",
        shot_type: str = "medium_shot",
        lighting: str = "three_point_studio",
        emotion: str = "contemplation_reflection",
        additional_details: Optional[str] = None,
        character_consistency: Optional[str] = None,
        camera_motion: Optional[str] = None
    ) -> PromptResult:
        """
        Build a professional cinematic prompt for a single shot.

        Args:
            subject: Character or subject description (e.g., "Emma, 30s professional woman")
            action: What the subject is doing (e.g., "typing on laptop, moment of realization")
            location: Where the scene takes place (e.g., "modern office, glass walls")
            style: Cinematic style from CINEMATIC_STYLES (default: "hollywood_blockbuster")
            shot_type: Shot composition from SHOT_COMPOSITIONS (default: "medium_shot")
            lighting: Lighting setup from LIGHTING_SETUPS (default: "three_point_studio")
            emotion: Emotional beat from EMOTIONAL_BEATS (default: "contemplation_reflection")
            additional_details: Optional extra details to include
            character_consistency: Optional character reference for consistency
            camera_motion: Optional specific camera movement

        Returns:
            PromptResult with complete prompt, negative prompt, and metadata
        """

        # Get professional definitions
        style_def = get_style(style)
        shot_def = get_shot_type(shot_type)
        lighting_def = get_lighting(lighting)
        emotion_def = get_emotion(emotion)

        # Build prompt with layered professional detail
        prompt_parts = []

        # Format and camera
        prompt_parts.append(
            "8K ultra high definition cinematic film production, "
            "professional Hollywood grade cinematography, "
            "pristine image quality, "
            "shot on ARRI Alexa 65 camera with Panavision anamorphic lenses, "
            "film grain texture, "
            "cinematic aspect ratio composition,"
        )

        # Shot composition and camera
        prompt_parts.append(
            f"{shot_def.description}, "
            f"{shot_def.composition}, "
            f"camera angle: {shot_def.camera_angle}, "
            f"lens choice: {shot_def.lens}, "
        )

        # Camera movement
        if camera_motion:
            prompt_parts.append(f"camera movement: {camera_motion},")
        else:
            prompt_parts.append(f"camera movement: {shot_def.movement},")

        # Subject and action
        if character_consistency:
            prompt_parts.append(f"character: {subject} ({character_consistency}), ")
        else:
            prompt_parts.append(f"subject: {subject}, ")

        prompt_parts.append(f"action: {action},")

        # Emotional beat
        prompt_parts.append(
            f"emotional state: {emotion_def.description}, "
            f"facial expression: {emotion_def.facial_expression}, "
            f"body language: {emotion_def.body_language}, "
            f"eyes: {emotion_def.eyes},"
        )

        # Location
        prompt_parts.append(f"location setting: {location},")

        # Lighting
        prompt_parts.append(
            f"lighting setup: {lighting_def.description}, "
            f"key light: {lighting_def.key_light}, "
            f"fill light: {lighting_def.fill_light}, "
            f"practical lights: {lighting_def.practicals}, "
            f"atmosphere: {lighting_def.atmosphere}, "
            f"color temperature: {lighting_def.color_temp},"
        )

        # Visual style
        prompt_parts.append(
            f"cinematography style: {style_def.description}, "
            f"{style_def.lighting}, "
            f"color grading: {style_def.color_grading}, "
            f"color palette: {emotion_def.color_palette},"
        )

        # Mood and atmosphere
        prompt_parts.append(
            f"mood: {style_def.mood}, "
            f"{emotion_def.visual_metaphor}, "
            f"atmospheric depth, "
            f"dimensional storytelling through layers,"
        )

        # Technical excellence
        prompt_parts.append(
            "perfect focus with precise focus pulling, "
            "professional color grading in post, "
            "35mm film grain texture and character, "
            "cinematic lens breathing, "
            "natural bokeh, "
            "award-winning cinematography, "
            "festival quality production value, "
            "masterful composition,"
        )

        # Reference films
        prompt_parts.append(
            f"cinematography inspired by {', '.join(style_def.reference_films[:2])}, "
        )

        # Additional details
        if additional_details:
            prompt_parts.append(additional_details + ",")

        # Final quality markers
        prompt_parts.append(
            "theatrical release quality, "
            "professional filmmaking, "
            "master cinematographer level work,"
        )

        # Compile final prompt
        final_prompt = " ".join(prompt_parts)

        # Build professional negative prompt
        negative_prompt = self._build_negative_prompt()

        # Create director's notes
        director_notes = self._create_director_notes(
            shot_def, style_def, lighting_def, emotion_def
        )

        # Technical notes for production
        technical_notes = self._create_technical_notes(
            shot_def, lighting_def, style_def
        )

        return PromptResult(
            prompt=final_prompt,
            negative_prompt=negative_prompt,
            metadata={
                "style": style,
                "shot_type": shot_type,
                "lighting": lighting,
                "emotion": emotion,
                "reference_films": style_def.reference_films,
                "duration_range": shot_def.duration_range,
                "contrast_ratio": lighting_def.contrast_ratio,
                "color_temp": lighting_def.color_temp,
            },
            technical_notes=technical_notes,
            director_notes=director_notes
        )

    def build_scene_sequence(
        self,
        scene_description: str,
        characters: List[str],
        location: str,
        num_shots: int = 5,
        style: str = "hollywood_blockbuster",
        pacing: str = "medium",
        emotional_arc: Optional[List[str]] = None
    ) -> List[PromptResult]:
        """
        Build a complete scene with professional shot coverage.

        This method applies professional filmmaking principles:
        - Establishing wide to orient audience
        - Coverage from multiple angles
        - Emotional escalation through shot progression
        - Proper shot variety and pacing

        Args:
            scene_description: Overall scene description
            characters: List of character names/descriptions
            location: Scene location
            num_shots: Number of shots to generate (default: 5)
            style: Cinematic style to use throughout
            pacing: "slow", "medium", "dynamic", or "action"
            emotional_arc: Optional list of emotions for each shot

        Returns:
            List of PromptResult objects for each shot in sequence
        """

        # Get recommended shot sequence for pacing
        shot_sequence = get_recommended_shot_sequence(pacing)

        # Extend or trim to match requested number of shots
        if len(shot_sequence) < num_shots:
            # Repeat pattern
            multiplier = (num_shots // len(shot_sequence)) + 1
            shot_sequence = (shot_sequence * multiplier)[:num_shots]
        else:
            shot_sequence = shot_sequence[:num_shots]

        # Build emotional arc if not provided
        if not emotional_arc:
            emotional_arc = self._build_emotional_arc(num_shots, pacing)

        # Lighting progression
        lighting_progression = self._build_lighting_progression(num_shots, pacing)

        # Build each shot
        results = []
        for i, (shot_type, emotion, lighting) in enumerate(zip(shot_sequence, emotional_arc, lighting_progression)):
            # Determine subject focus
            if i == 0:
                # Establishing shot
                subject = f"wide view of {location}"
                action = "establishing scene context and geography"
            else:
                # Rotate through characters or focus on main character
                character = characters[i % len(characters)] if characters else "character"
                subject = character
                action = f"scene action beat {i + 1}: {scene_description}"

            result = self.build_shot(
                subject=subject,
                action=action,
                location=location,
                style=style,
                shot_type=shot_type,
                lighting=lighting,
                emotion=emotion,
                additional_details=f"shot {i + 1} of {num_shots}, {pacing} pacing"
            )

            results.append(result)

        return results

    def _build_negative_prompt(self) -> str:
        """
        Build comprehensive negative prompt.

        Based on common AI image generation artifacts and issues that
        professional filmmakers would want to avoid.
        """
        return (
            # Quality issues
            "low quality, poor quality, amateur, home video, phone camera footage, "
            "webcam quality, security camera footage, low resolution, pixelated, "
            "compression artifacts, jpeg artifacts, noise artifacts, banding, "

            # Lighting issues
            "bad lighting, poor lighting, overexposed, underexposed, blown highlights, "
            "crushed blacks without detail, flat lighting, harsh unflattering light, "
            "mixed color temperatures (unintentional), muddy shadows, "

            # Focus and camera issues
            "blurry, out of focus, motion blur artifacts, focus hunting, "
            "soft focus (unless intended), depth of field errors, "
            "lens distortion artifacts, chromatic aberration, vignetting (unless intended), "

            # Composition issues
            "bad composition, awkward framing, poor framing, cluttered composition, "
            "distracting background elements, unmotivated Dutch angle, "
            "inconsistent horizon line, poor headroom, bad look space, "

            # Subject issues
            "distorted proportions, unnatural anatomy, awkward poses, "
            "stiff unnatural positioning, mannequin-like, "
            "disconnected body parts, incorrect number of fingers, "

            # Style issues
            "cartoon, anime, cel-shaded, 3D render, CGI (unless intended), "
            "video game graphics, artificial, plastic appearance, "
            "over-processed, Instagram filters, amateur color grading, "
            "oversaturated, neon colors (unless intended), garish colors, "

            # Skin and faces
            "uncanny valley, dead eyes, lifeless expression (unless intended), "
            "unnatural skin tones, plastic skin, waxy appearance, "
            "bad makeup application, visible face smoothing, beauty filter artifacts, "

            # Text and watermarks
            "watermark, text overlay, subtitles (unless intended), "
            "letterbox bars (unless intended), logo overlay, time stamp, "
            "duplicate subjects, clones, repeated patterns, "

            # Camera artifacts
            "lens flare (unless motivated), light leaks (unless intended), "
            "rolling shutter artifacts, sensor artifacts, dead pixels"
        )

    def _create_director_notes(
        self,
        shot: ShotComposition,
        style: CinematicStyle,
        lighting: LightingSetup,
        emotion: EmotionalBeat
    ) -> str:
        """Create director's notes for the shot"""
        return f"""
DIRECTOR'S NOTES:

Shot Purpose: {shot.purpose}

Performance Direction:
- Emotional state: {emotion.description}
- Energy level: {emotion.energy_level}
- Body language: {emotion.body_language}
- Breathing: {emotion.breath_pattern}

Cinematography:
- Style reference: {', '.join(style.reference_films[:2])}
- Mood to achieve: {style.mood}
- Visual metaphor: {emotion.visual_metaphor}

Lighting Notes:
- Key light: {lighting.key_light}
- Mood effect: {lighting.mood_effect}
- Color temperature: {lighting.color_temp}

Duration: {shot.duration_range[0]}-{shot.duration_range[1]} seconds
        """.strip()

    def _create_technical_notes(
        self,
        shot: ShotComposition,
        lighting: LightingSetup,
        style: CinematicStyle
    ) -> str:
        """Create technical notes for cinematographer"""
        return f"""
TECHNICAL NOTES:

Camera Setup:
- Lens: {shot.lens}
- Camera angle: {shot.camera_angle}
- Movement: {shot.movement}

Lighting Setup:
- Key: {lighting.key_light}
- Fill: {lighting.fill_light}
- Back: {lighting.back_light}
- Practicals: {lighting.practicals}
- Contrast ratio: {lighting.contrast_ratio}
- Color temp: {lighting.color_temp}

Post-Production:
- Color grading: {style.color_grading}
- Look: {style.name}
        """.strip()

    def _build_emotional_arc(self, num_shots: int, pacing: str) -> List[str]:
        """Build emotional progression for scene"""
        # Professional emotional arcs based on pacing
        arcs = {
            "slow": [
                "contemplation_reflection",
                "curiosity_interest",
                "contemplation_reflection",
                "melancholy_sadness",
                "determination_resolve"
            ],
            "medium": [
                "curiosity_interest",
                "tension_anxiety",
                "determination_resolve",
                "triumph_victory",
                "joy_delight"
            ],
            "dynamic": [
                "determination_resolve",
                "tension_anxiety",
                "surprise_shock",
                "triumph_victory",
                "exhaustion_defeat"
            ],
            "action": [
                "determination_resolve",
                "tension_anxiety",
                "fear_terror",
                "anger_rage",
                "triumph_victory"
            ]
        }

        arc = arcs.get(pacing, arcs["medium"])

        # Extend or trim
        if len(arc) < num_shots:
            multiplier = (num_shots // len(arc)) + 1
            arc = (arc * multiplier)[:num_shots]
        else:
            arc = arc[:num_shots]

        return arc

    def _build_lighting_progression(self, num_shots: int, pacing: str) -> List[str]:
        """Build lighting progression for scene"""
        # Lighting typically intensifies through scene
        progressions = {
            "slow": [
                "natural_window_light",
                "overcast_soft",
                "natural_window_light",
                "dramatic_single_source",
                "magic_hour_backlight"
            ],
            "medium": [
                "three_point_studio",
                "natural_window_light",
                "dramatic_single_source",
                "three_point_studio",
                "golden_hour_exterior"
            ],
            "dynamic": [
                "three_point_studio",
                "dramatic_single_source",
                "neon_urban_night",
                "low_key_noir",
                "high_key_commercial"
            ],
            "action": [
                "low_key_noir",
                "dramatic_single_source",
                "neon_urban_night",
                "firelight_warm",
                "magic_hour_backlight"
            ]
        }

        progression = progressions.get(pacing, progressions["medium"])

        # Extend or trim
        if len(progression) < num_shots:
            multiplier = (num_shots // len(progression)) + 1
            progression = (progression * multiplier)[:num_shots]
        else:
            progression = progression[:num_shots]

        return progression


# Convenience functions for quick prompt building

def quick_shot(subject: str, action: str, location: str, **kwargs) -> str:
    """
    Quick prompt builder for simple use cases.

    Returns just the prompt string.
    """
    builder = CinematicPromptBuilder()
    result = builder.build_shot(subject, action, location, **kwargs)
    return result.prompt


def quick_scene(description: str, characters: List[str], location: str, **kwargs) -> List[str]:
    """
    Quick scene builder for simple use cases.

    Returns list of prompt strings.
    """
    builder = CinematicPromptBuilder()
    results = builder.build_scene_sequence(description, characters, location, **kwargs)
    return [r.prompt for r in results]
