"""
Professional emotional beats and character states.
Knowledge from method acting and directing techniques.
"""

from typing import Dict
from pydantic import BaseModel


class EmotionalBeat(BaseModel):
    """Professional emotional beat definition"""
    name: str
    description: str
    facial_expression: str
    body_language: str
    eyes: str
    energy_level: str
    breath_pattern: str
    visual_metaphor: str
    lighting_suggestion: str
    color_palette: str


# ============================================================================
# EMOTIONAL BEATS LIBRARY
# ============================================================================

EMOTIONAL_BEATS = {
    "triumph_victory": EmotionalBeat(
        name="Triumph/Victory",
        description="Victorious moment of achievement and success",
        facial_expression="Genuine smile reaching eyes (Duchenne smile), raised eyebrows in joy, relaxed forehead, open expression, teeth visible, cheeks lifted",
        body_language="Raised chin, chest out and shoulders back, open stance, fists pumped or arms raised, upright confident posture, forward energy",
        eyes="Bright and wide open, crinkling at corners from genuine smile, direct gaze forward or skyward, shining with accomplishment",
        energy_level="High energy, victorious, elevated, powerful, explosive release",
        breath_pattern="Deep satisfied exhale, triumphant breathing, expanded lungs",
        visual_metaphor="Rising sun, mountain summit reached, breaking through clouds",
        lighting_suggestion="Bright uplighting, rim light creating halo effect, warm golden tones, lens flares",
        color_palette="Golds, warm yellows, bright oranges, saturated colors, lifted blacks"
    ),

    "contemplation_reflection": EmotionalBeat(
        name="Contemplation/Reflection",
        description="Quiet moment of deep thought and internal processing",
        facial_expression="Soft neutral expression, slightly furrowed brow in thought, lips naturally closed or slightly parted, distant look, serene face",
        body_language="Still and quiet, possibly sitting or leaning, hand to chin or temple, turned slightly away from camera, weighted relaxed posture",
        eyes="Soft unfocused gaze into middle distance, looking away from camera, eyes suggesting internal vision rather than external observation",
        energy_level="Low to medium energy, introspective, turned inward, peaceful stillness",
        breath_pattern="Slow deep breathing, contemplative rhythm, peaceful measured breaths",
        visual_metaphor="Still water reflecting, lone tree, window looking out",
        lighting_suggestion="Soft window light from side, gentle falloff, contemplative shadows, natural quiet light",
        color_palette="Muted tones, desaturated blues and grays, soft earth tones, gentle contrast"
    ),

    "tension_anxiety": EmotionalBeat(
        name="Tension/Anxiety",
        description="Building unease and nervous anticipation",
        facial_expression="Tightened jaw, furrowed brow, compressed lips, darting eyes, tension in facial muscles, micro-expressions of worry",
        body_language="Hunched shoulders, closed body language, arms crossed or hands clenched, rigid posture, weight shifting, restless movement",
        eyes="Darting glances, widened with alertness, rapid blinking, avoiding direct gaze, watching periphery, hypervigilance",
        energy_level="High nervous energy, on edge, coiled spring, ready to react",
        breath_pattern="Shallow rapid breathing, held breath, uneven rhythm, chest breathing",
        visual_metaphor="Storm clouds gathering, tightrope walking, walls closing in",
        lighting_suggestion="Hard shadows, cross-lighting creating unease, cool tones, shadows creeping",
        color_palette="Desaturated colors, cool blue-grays, sickly greens, uncomfortable contrast"
    ),

    "joy_delight": EmotionalBeat(
        name="Joy/Delight",
        description="Pure happiness and genuine enjoyment",
        facial_expression="Genuine Duchenne smile with eye crinkles, raised cheeks, open relaxed face, laughing or about to laugh, spontaneous expression",
        body_language="Open body language, relaxed shoulders, possible movement or bounce, leaning forward toward joy source, uninhibited physicality",
        eyes="Bright and sparkling, crinkled at corners from genuine smile, wide and engaged, making happy contact",
        energy_level="Medium to high buoyant energy, light, effervescent, lifted",
        breath_pattern="Light quick breaths, possible laughter breathing, easy flowing breath",
        visual_metaphor="Sunlight through trees, children playing, flowers blooming",
        lighting_suggestion="Soft warm light, diffused sunlight, bright without harshness, lifted shadows",
        color_palette="Warm pastels, bright but soft colors, yellows and pinks, optimistic palette"
    ),

    "melancholy_sadness": EmotionalBeat(
        name="Melancholy/Sadness",
        description="Deep sadness and mournful emotion",
        facial_expression="Downturned mouth corners, heavy eyelids, soft unfocused eyes possibly glistening with tears, slack facial muscles, defeated expression",
        body_language="Slumped shoulders, head bowed or tilted down, curved spine, body weight sinking, withdrawn closed posture, possible hand to face",
        eyes="Downcast gaze avoiding contact, possibly moist or tearful, heavy lidded, looking down or away, burdened expression",
        energy_level="Low energy, weighted down, heavy, drained, depleted",
        breath_pattern="Deep sighs, slow heavy breathing, irregular catching breaths",
        visual_metaphor="Rain on window, wilting flower, falling leaves, gray overcast",
        lighting_suggestion="Soft diffused light, cool tones, gentle shadows, muted quality, low key",
        color_palette="Desaturated blues and grays, muted cool tones, low saturation, heavy blacks"
    ),

    "determination_resolve": EmotionalBeat(
        name="Determination/Resolve",
        description="Unwavering focus and committed resolve",
        facial_expression="Set jaw, focused intense eyes, slight furrow of concentration, firm closed or slightly compressed lips, determined brow",
        body_language="Square shoulders, straight spine, forward lean suggesting purpose, rooted stance, clenched fists showing resolve, solid grounded posture",
        eyes="Intense direct focused gaze, unblinking, locked on target or goal, steely expression, unwavering",
        energy_level="Medium to high controlled energy, contained power, coiled readiness",
        breath_pattern="Steady controlled breathing, measured rhythm, disciplined breath",
        visual_metaphor="Arrow drawn in bow, athlete at starting line, mountain climber ascending",
        lighting_suggestion="Dramatic directional light, strong shadows showing resolve, powerful contrast",
        color_palette="Strong saturated colors, deep shadows, powerful contrast, dramatic tones"
    ),

    "fear_terror": EmotionalBeat(
        name="Fear/Terror",
        description="Genuine fear and primal terror response",
        facial_expression="Wide eyes showing whites, raised eyebrows, open mouth possibly gasping, facial muscles tense, primitive fear response visible",
        body_language="Frozen or pulling back, protective hands raised, body recoiling, hunched defensive posture, possibly trembling",
        eyes="Wide open showing whites (scleral show), pupils dilated, fixed on threat or darting away, primal fear visible",
        energy_level="High panic energy, fight-or-flight response, adrenaline surge",
        breath_pattern="Rapid shallow gasping, held breath, hyperventilation, panic breathing",
        visual_metaphor="Cornered prey, cliff edge, darkness closing in, shadows lurking",
        lighting_suggestion="Hard dramatic shadows, darkness encroaching, underexposed with selective highlighting, ominous tones",
        color_palette="Desaturated with harsh contrast, blacks and dark blues, sickly greens, oppressive darkness"
    ),

    "anger_rage": EmotionalBeat(
        name="Anger/Rage",
        description="Building anger and potential rage",
        facial_expression="Furrowed brow, narrowed eyes, flared nostrils, clenched jaw, compressed or bared teeth, flushed face, tension radiating",
        body_language="Tense rigid posture, clenched fists, forward aggressive lean, squared shoulders, invasion of space, coiled aggression",
        eyes="Narrowed in anger, intense piercing gaze, burning stare, eyebrows drawn down and together, focused on anger target",
        energy_level="High aggressive energy, explosive potential, contained volcano, tension building",
        breath_pattern="Heavy forceful breathing, flared nostrils, aggressive exhalations",
        visual_metaphor="Gathering storm, volcano before eruption, lightning strike",
        lighting_suggestion="Hard dramatic lighting, red undertones, harsh shadows, high contrast, aggressive angles",
        color_palette="Reds and oranges, high contrast, saturated aggressive colors, harsh tones"
    ),

    "surprise_shock": EmotionalBeat(
        name="Surprise/Shock",
        description="Unexpected surprise and startled response",
        facial_expression="Raised eyebrows, wide open eyes, open mouth forming 'O' shape, momentary facial paralysis, unprepared expression",
        body_language="Sudden stop of movement, body pulled back, hands possibly raised defensively, frozen moment, interrupted motion",
        eyes="Wide open showing whites, focused on surprise source, eyebrows raised creating forehead wrinkles, alert startled look",
        energy_level="Sudden spike from stillness, interrupted energy, startled jolt",
        breath_pattern="Gasped inhale, held breath, catch in breathing",
        visual_metaphor="Lightning flash, door suddenly opening, unexpected reveal",
        lighting_suggestion="Sudden light change, flash of illumination, dramatic reveal lighting",
        color_palette="High contrast sudden change, bright highlights against darkness"
    ),

    "love_tenderness": EmotionalBeat(
        name="Love/Tenderness",
        description="Tender loving emotion and affection",
        facial_expression="Soft gentle smile, relaxed peaceful face, eyes showing warmth, open tender expression, vulnerable openness",
        body_language="Leaning toward subject of affection, open receptive posture, gentle reaching gestures, vulnerable open body language",
        eyes="Soft focused gaze on beloved, gentle eye contact, warmth radiating from eyes, slight sparkle, loving look",
        energy_level="Gentle warm energy, soft and open, vulnerable sharing",
        breath_pattern="Slow deep satisfied breathing, peaceful rhythm, contented sighs",
        visual_metaphor="Warm embrace, sunrise, gentle touch, flowers opening",
        lighting_suggestion="Soft warm light, gentle wrapping illumination, golden hour quality, tender glow",
        color_palette="Warm soft tones, peaches and golds, gentle pinks, warm shadows"
    ),

    "curiosity_interest": EmotionalBeat(
        name="Curiosity/Interest",
        description="Engaged curiosity and intellectual interest",
        facial_expression="Slightly raised eyebrows, focused expression, tilted head, alert face, open interested look, engaged features",
        body_language="Leaning forward toward object of interest, head tilted in curiosity, open body language, reaching gestures",
        eyes="Bright and alert, focused with interest, slightly widened, examining closely, engaged active looking",
        energy_level="Alert engaged energy, focused attention, intellectual activation",
        breath_pattern="Normal breathing with occasional held breath during focus, attentive rhythm",
        visual_metaphor="Detective examining clue, child discovering new thing, explorer finding path",
        lighting_suggestion="Clear focused light, good visibility, bright engaged quality, natural curiosity",
        color_palette="Clear bright colors, good visibility, natural balanced tones"
    ),

    "exhaustion_defeat": EmotionalBeat(
        name="Exhaustion/Defeat",
        description="Complete physical and emotional exhaustion",
        facial_expression="Slack facial muscles, heavy eyelids, possibly closed eyes, expressionless from depletion, mouth slightly open, defeated look",
        body_language="Collapsed or slumped posture, head hanging, arms hanging limp, body supported by wall or furniture, total energy depletion",
        eyes="Heavy lidded or closed, unfocused if open, dark circles visible, burdened by fatigue, vacant from exhaustion",
        energy_level="Zero energy, completely depleted, emptied out, running on nothing",
        breath_pattern="Heavy labored breathing or shallow weak breaths, irregular exhausted pattern",
        visual_metaphor="Marathon runner collapsed at finish, wilted plant, empty vessel",
        lighting_suggestion="Low key, minimal lighting suggesting energy drain, shadows dominant, depleted quality",
        color_palette="Desaturated washed out colors, grays, muted everything, lifeless tones"
    ),
}


def get_emotion(emotion_name: str) -> EmotionalBeat:
    """Get an emotional beat by name."""
    return EMOTIONAL_BEATS.get(emotion_name, EMOTIONAL_BEATS["contemplation_reflection"])


def find_emotions_by_energy(energy: str) -> list[EmotionalBeat]:
    """
    Find emotions matching energy level.

    Args:
        energy: "low", "medium", "high"
    """
    results = []
    energy_lower = energy.lower()

    for emotion in EMOTIONAL_BEATS.values():
        if energy_lower in emotion.energy_level.lower():
            results.append(emotion)

    return results


def get_complementary_emotions(emotion_name: str) -> list[str]:
    """
    Get emotions that work well in sequence with given emotion.

    Returns list of emotion keys that create good dramatic arc.
    """
    sequences = {
        "triumph_victory": ["determination_resolve", "tension_anxiety"],
        "contemplation_reflection": ["melancholy_sadness", "curiosity_interest"],
        "tension_anxiety": ["fear_terror", "determination_resolve"],
        "joy_delight": ["love_tenderness", "surprise_shock"],
        "melancholy_sadness": ["contemplation_reflection", "determination_resolve"],
        "determination_resolve": ["triumph_victory", "exhaustion_defeat"],
        "fear_terror": ["tension_anxiety", "surprise_shock"],
        "anger_rage": ["determination_resolve", "exhaustion_defeat"],
        "surprise_shock": ["joy_delight", "fear_terror"],
        "love_tenderness": ["joy_delight", "melancholy_sadness"],
        "curiosity_interest": ["surprise_shock", "determination_resolve"],
        "exhaustion_defeat": ["determination_resolve", "contemplation_reflection"],
    }

    return sequences.get(emotion_name, ["contemplation_reflection"])
