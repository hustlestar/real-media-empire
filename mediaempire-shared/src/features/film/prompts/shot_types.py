"""
Professional shot types and compositions.
Based on industry-standard cinematography practices.
"""

from typing import Dict
from pydantic import BaseModel


class ShotComposition(BaseModel):
    """Professional shot composition definition"""
    name: str
    description: str
    composition: str
    camera_angle: str
    lens: str
    movement: str
    purpose: str
    duration_range: tuple[int, int]  # (min, max) seconds


# ============================================================================
# PROFESSIONAL SHOT TYPES
# ============================================================================

SHOT_COMPOSITIONS = {
    "establishing_wide": ShotComposition(
        name="Establishing Wide Shot",
        description="Wide shot establishing the scene location and context",
        composition="Rule of thirds placement with horizon on upper or lower third, leading lines drawing eye into frame, depth layers (foreground/midground/background) for dimensional storytelling, negative space for scale",
        camera_angle="Eye level 5-6 feet for neutral human perspective, or slight high angle 8-10 feet for god's eye establishing context and geography",
        lens="Wide angle 24-35mm full frame equivalent for expansive field of view, deep depth of field T8-T11 keeping everything sharp from foreground to infinity",
        movement="Slow subtle push-in on dolly or slider (1-2 feet) to draw viewer into the world, or static locked-off establishing allowing viewer to absorb scene details",
        purpose="Establish location geography and context, set scale and atmosphere, orient viewer in space and time, create sense of place before moving to closer coverage",
        duration_range=(4, 8)
    ),

    "wide_master": ShotComposition(
        name="Wide Master Shot",
        description="Scene-covering wide shot showing all action and blocking",
        composition="Frame all subjects and key action areas, maintain consistent headroom and look space, show spatial relationships between characters, use architecture and set elements for natural framing",
        camera_angle="Eye level matching actor eyelines, adjusted based on blocking to maintain clear view of all action without obstruction",
        lens="Medium-wide 28-40mm full frame equivalent, moderate depth of field T5.6-T8 keeping main subjects sharp with slight background softness for separation",
        movement="Following master blocking with smooth dolly or steadicam moves, maintaining consistent coverage of scene geography, motivated by character movement",
        purpose="Cover entire scene action as safety coverage, establish spatial relationships between subjects, maintain continuity reference for editing tighter shots",
        duration_range=(5, 15)
    ),

    "medium_shot": ShotComposition(
        name="Medium Shot",
        description="Waist-up framing balancing character and environment",
        composition="Chest to head framing with proper headroom (hand's width from top of frame), look space in direction of gaze (more space ahead than behind), diagonal body positioning for dynamic composition, rule of thirds eye placement",
        camera_angle="Eye level for neutral perspective and character equality, slight low angle (below eye) for power and authority, subtle high angle (above eye) for vulnerability",
        lens="Standard focal length 50mm full frame equivalent mimicking natural human vision, moderate depth of field T2.8-T5.6 keeping subject sharp with gradual background falloff",
        movement="Subtle reframe with dolly or jib following natural character movement, smooth pan with head turns maintaining proper look space, motivated by subject blocking",
        purpose="Show character emotion and body language while maintaining environmental context, ideal for dialogue and moderate action, connects wide establishing with intimate close-ups",
        duration_range=(3, 8)
    ),

    "medium_closeup": ShotComposition(
        name="Medium Close-Up (MCU)",
        description="Chest-up framing emphasizing facial expressions",
        composition="Bottom of frame at chest/shoulders, face filling frame with proper headroom, eyes on upper third line, look space maintained, tight enough for emotion but wide enough for hand gestures",
        camera_angle="Eye level for connection and honesty, slight low angle for confidence, subtle high angle for introspection or defeat",
        lens="Portrait lens 75-85mm full frame equivalent, shallow depth of field T2-T2.8 isolating subject from background with smooth bokeh",
        movement="Minimal movement to maintain intimacy, locked-off for emotional intensity, very subtle slow push-in (6 inches) for dramatic moments",
        purpose="Capture detailed facial expressions and micro-emotions, ideal for emotional dialogue and character reactions, bridge between medium shots and extreme close-ups",
        duration_range=(2, 6)
    ),

    "closeup_character": ShotComposition(
        name="Close-Up",
        description="Face-filling close-up for maximum emotional impact",
        composition="Full face filling frame with eyes on upper third, minimal headroom (fingers width), very tight framing for intensity, leaving just enough space to feel composed not claustrophobic",
        camera_angle="Eye level for direct emotional connection with audience, matching their gaze for intimacy and truth, slight variations for specific emotional states",
        lens="Portrait lens 85-135mm full frame equivalent, very shallow depth of field T1.4-T2.8 with sharp focus on eyes, smooth bokeh blur on background and even closer foreground",
        movement="Locked-off for maximum intensity and focus on performance, no camera movement to distract from raw emotion, stationary as emotional anchor point",
        purpose="Maximum emotional impact and character revelation, see every micro-expression and thought, create intimacy between character and audience, punctuate emotional beats",
        duration_range=(2, 5)
    ),

    "extreme_closeup": ShotComposition(
        name="Extreme Close-Up (ECU)",
        description="Detail-focused extreme close-up for emphasis",
        composition="Isolated facial feature (eyes, lips, hands) or important object detail filling entire frame, abstract framing removing context, texture and detail emphasis",
        camera_angle="Varies based on subject, often perpendicular to surface for detail emphasis, motivated by narrative intent rather than realism",
        lens="Macro lens or long telephoto 100-200mm for compression and isolation, extremely shallow depth of field T1.4-T2 with razor-thin focus plane",
        movement="Slow reveal or rack focus for discovery, minimal movement to maintain detail sharpness, sometimes locked-off for frozen moment emphasis",
        purpose="Emphasize critical story detail or object importance, create intrigue and questions, provide sensory detail and texture, isolate important element from context",
        duration_range=(1, 3)
    ),

    "over_shoulder": ShotComposition(
        name="Over-the-Shoulder Shot (OTS)",
        description="Shot framing subject over another character's shoulder",
        composition="1/3 of frame showing shoulder and back of head of foreground character, 2/3 showing face of background subject, eye-line preserved, depth and relationship established through layering",
        camera_angle="Matching eye-line between characters, positioning camera at speaking character's eye level for proper perspective and natural interaction feel",
        lens="Standard to portrait 50-85mm, moderate depth of field T2.8-T4 with foreground shoulder soft but recognizable, background subject sharp and in focus",
        movement="Smooth transition between matching OTS angles following dialogue, maintaining 180-degree axis rule, motivated pans with character head turns",
        purpose="Establish spatial relationship and interaction between characters, maintain dialogue geography, create sense of conversation participation, show both speakers in context of each other",
        duration_range=(2, 6)
    ),

    "two_shot": ShotComposition(
        name="Two Shot",
        description="Framing two subjects showing their relationship",
        composition="Both subjects visible with balanced composition, can be symmetrical for equality or asymmetrical for dynamic relationship, rule of thirds placing subjects, negative space between them suggesting relationship distance",
        camera_angle="Eye level for neutral relationship observation, adjusted based on power dynamics and scene needs",
        lens="Standard to medium-wide 40-50mm capturing both subjects comfortably, depth of field T2.8-T5.6 keeping both subjects sharp",
        movement="Slow push-in toward subjects as scene intensifies, or pull-out as relationship fractures, motivated by emotional beats and blocking",
        purpose="Show character relationship and interaction dynamics, establish connection or conflict between subjects, efficient coverage for dialogue and interaction",
        duration_range=(3, 8)
    ),

    "action_dynamic": ShotComposition(
        name="Dynamic Action Shot",
        description="High-energy shot capturing fast movement and action",
        composition="Leading the action with space ahead of movement, motion blur for energy and speed, diagonal lines for dynamism, tight framing for intensity",
        camera_angle="Low angle 2-3 feet off ground for dramatic heroic feel and power, handheld for kinetic energy and immediacy",
        lens="Wide to standard 24-50mm for capturing full action, sometimes long lens 85-200mm for compression and intensity, deep depth of field T5.6-T8 keeping action sharp",
        movement="Following action with Steadicam or gimbal, whip pans between action beats, crash zooms for emphasis, kinetic camera work matching action energy",
        purpose="Convey energy, excitement, and momentum, immerse audience in action, create visceral physical experience, heighten tension and stakes",
        duration_range=(1, 4)
    ),

    "pov_subjective": ShotComposition(
        name="Point of View (POV)",
        description="Camera as character's eyes showing their perspective",
        composition="Framing exactly what character sees from their eye level and position, environmental elements framing edges suggesting peripheral vision, sometimes slight handheld breathing for realism",
        camera_angle="Exact character eye level and direction of gaze, matching their physical position and body orientation precisely",
        lens="Standard 40-50mm matching human vision field of view naturally, depth of field matching human focus T2.8-T4",
        movement="Natural head movements - pans for looking around, tilts for looking up/down, subtle handheld breathing rhythm, motivated by character action",
        purpose="Create subjective experience and audience identification with character, show world from character's unique perspective, heighten tension in thriller/horror",
        duration_range=(2, 6)
    ),

    "insert_detail": ShotComposition(
        name="Insert Detail Shot",
        description="Close shot of object or action detail",
        composition="Object centered and clearly visible, neutral background for emphasis, hands often included for context and scale, clean composition without distraction",
        camera_angle="Perpendicular to action or object for clarity, high angle for reading material, angle that shows object most clearly",
        lens="Macro 60-100mm for small objects, standard 50mm for hand actions, depth of field optimized for object T2.8-T5.6",
        movement="Static for clarity and detail reading, slow push-in for emphasis and revelation, rack focus from object to character reaction",
        purpose="Convey crucial information audience needs to see, emphasize important prop or story element, show specific action detail, punctuate moments",
        duration_range=(1, 3)
    ),

    "reaction_shot": ShotComposition(
        name="Reaction Shot",
        description="Close-up capturing character's reaction to action or dialogue",
        composition="Face-filling frame, tight on emotional expression, eyes on upper third, minimal headroom for intensity",
        camera_angle="Eye level for neutral emotional observation, subtle adjustments based on specific emotion being shown",
        lens="Portrait 85-135mm, shallow depth T1.4-T2.8 isolating character's face, soft background blur",
        movement="Locked off for emotional intensity, no distracting movement, let performance carry the shot",
        purpose="Show character processing information, emotional response to scene events, create dramatic irony, build tension through delayed revelation",
        duration_range=(1, 4)
    ),
}


def get_shot_type(shot_name: str) -> ShotComposition:
    """Get a shot composition by name."""
    return SHOT_COMPOSITIONS.get(shot_name, SHOT_COMPOSITIONS["medium_shot"])


def get_shot_by_purpose(purpose_keyword: str) -> list[ShotComposition]:
    """Find shots by purpose keyword."""
    results = []
    keyword_lower = purpose_keyword.lower()

    for shot in SHOT_COMPOSITIONS.values():
        if keyword_lower in shot.purpose.lower():
            results.append(shot)

    return results


def get_recommended_shot_sequence(pacing: str = "medium") -> list[str]:
    """
    Get recommended shot sequence for a scene based on pacing.

    Args:
        pacing: "slow", "medium", "dynamic", or "action"

    Returns:
        List of shot type keys in recommended sequence
    """
    sequences = {
        "slow": [
            "establishing_wide",
            "wide_master",
            "medium_shot",
            "medium_closeup",
            "closeup_character",
            "reaction_shot",
            "medium_shot"
        ],
        "medium": [
            "establishing_wide",
            "medium_shot",
            "over_shoulder",
            "medium_closeup",
            "closeup_character",
            "two_shot"
        ],
        "dynamic": [
            "establishing_wide",
            "action_dynamic",
            "medium_shot",
            "closeup_character",
            "insert_detail",
            "reaction_shot"
        ],
        "action": [
            "establishing_wide",
            "action_dynamic",
            "pov_subjective",
            "extreme_closeup",
            "action_dynamic",
            "reaction_shot"
        ]
    }

    return sequences.get(pacing, sequences["medium"])
