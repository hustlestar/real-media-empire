"""
Professional lighting setups and techniques.
Knowledge from master cinematographers and gaffers.
"""

from typing import Dict
from pydantic import BaseModel


class LightingSetup(BaseModel):
    """Professional lighting setup definition"""
    name: str
    description: str
    key_light: str
    fill_light: str
    back_light: str
    practicals: str
    atmosphere: str
    color_temp: str
    contrast_ratio: str
    mood_effect: str


# ============================================================================
# PROFESSIONAL LIGHTING SETUPS
# ============================================================================

LIGHTING_SETUPS = {
    "golden_hour_exterior": LightingSetup(
        name="Golden Hour Exterior",
        description="Magical hour sunlight for exterior scenes",
        key_light="Soft warm directional sunlight from low angle 15-30° above horizon, natural sun as primary source creating long shadows and golden glow",
        fill_light="Open sky ambient providing natural fill from above and reflected light bouncing from environment, ratio 3:1 for gentle modeling",
        back_light="Sun positioned behind subject creating rim light separation and hair light, practical use of natural rim for depth",
        practicals="None needed, relying on natural light only, possible reflectors or neg fill for control",
        atmosphere="Diffused airborne particles catching light rays, slight haze for atmospheric perspective, warm amber glow throughout",
        color_temp="5500-6500K warming toward orange as sun sets, golden amber quality with peachy undertones",
        contrast_ratio="3:1 to 4:1 for gentle dramatic modeling without harshness",
        mood_effect="Magical, warm, romantic, nostalgic, dreamlike, optimistic"
    ),

    "blue_hour_twilight": LightingSetup(
        name="Blue Hour Twilight",
        description="Cool twilight ambiance for dramatic evening scenes",
        key_light="Residual skylight from twilight creating soft ambient glow, cool blue directionless light from sky dome",
        fill_light="Ambient skylight providing wraparound illumination, no distinct fill needed as light is omnidirectional",
        back_light="Practical street lamps, building lights, or car lights creating warm accent rims and depth separation",
        practicals="Tungsten street lamps 3200K, neon signs, lit windows, car headlights - all warm sources contrasting cool ambient",
        atmosphere="Deep blue saturated sky, warm-cool contrast between practical sources and natural light creating visual interest",
        color_temp="8000-12000K blue ambient light from sky, 2700-3200K warm practicals for contrast",
        contrast_ratio="2:1 ambient with practical accent lights creating pools of warm light in cool environment",
        mood_effect="Moody, mysterious, contemplative, transitional, urban solitude"
    ),

    "three_point_studio": LightingSetup(
        name="Three-Point Studio Perfect",
        description="Classic professional studio lighting setup",
        key_light="Primary light source 45° horizontal and 30° vertical from subject, soft source through 4x4 diffusion creating directional but gentle illumination",
        fill_light="Opposite side from key at camera axis height, bounced or diffused light filling shadows, set to achieve 4:1 ratio with key",
        back_light="Behind subject elevated 45°, hard focused source creating rim separation from background, flagged to avoid lens flare",
        practicals="None in controlled studio environment, complete artificial control",
        atmosphere="Clean controlled environment with optional fog for atmosphere, black flags controlling spill and creating negative fill",
        color_temp="5600K daylight balanced for all sources, matched precisely with color meter",
        contrast_ratio="4:1 classic ratio providing good modeling without excessive drama, can adjust for specific mood",
        mood_effect="Professional, controlled, polished, confident, clear"
    ),

    "natural_window_light": LightingSetup(
        name="Natural Window Light",
        description="Soft diffused window light for intimate scenes",
        key_light="Large window as single primary source, diffused through sheer curtains or on overcast day, soft directional quality wrapping around subject",
        fill_light="Room bounce and opposite wall reflection providing gentle fill, white cards or poly boards for extra control if needed",
        back_light="None typically, relying on natural falloff and depth through subject-to-background distance",
        practicals="Possible table lamp or ceiling light for background depth and practical motivation, kept subtle",
        atmosphere="Soft wrapping quality, gentle falloff creating dimensional modeling, peaceful still ambiance",
        color_temp="5000-6500K depending on time of day and cloud cover, natural daylight quality",
        contrast_ratio="2:1 to 3:1 very gentle modeling from soft large source",
        mood_effect="Intimate, peaceful, natural, honest, contemplative, quiet"
    ),

    "dramatic_single_source": LightingSetup(
        name="Dramatic Single Hard Light",
        description="Film noir style dramatic lighting with stark contrast",
        key_light="Single hard direct source from 90° side (cross light) or 45° angle, creating dramatic deep shadows and stark highlight/shadow divide",
        fill_light="Minimal to none intentionally, allowing shadows to go black for dramatic effect, possible 8:1 ratio or greater",
        back_light="Optional hard rim light for edge definition if subject merging with dark background, kept subtle",
        practicals="Motivated practical lamp, street light, or window as apparent source justifying the hard light direction",
        atmosphere="Smoke or haze revealing light beams, atmospheric depth showing hard light quality, noir ambiance",
        color_temp="Varies based on motivated source - 3200K for tungsten lamp, 4300K for HMI street light, 5600K for window",
        contrast_ratio="8:1 or higher for maximum drama and film noir aesthetic",
        mood_effect="Dramatic, mysterious, tense, noir, high-stakes, dangerous"
    ),

    "neon_urban_night": LightingSetup(
        name="Neon Urban Night",
        description="Practical neon signs and urban lighting",
        key_light="Practical neon signs as key sources - pink, blue, green neon tubes creating pools of colored light",
        fill_light="Ambient urban bounce - reflected light from wet streets, storefronts, other practicals creating complex fill pattern",
        back_light="Street lamps, car lights, other practical sources behind subject creating depth separation",
        practicals="Neon signs, LED signage, car headlights/taillights, shop windows, street lamps - all motivated practical sources creating lighting",
        atmosphere="Rain-wet streets reflecting colored lights, urban haze diffusing neon glow, nighttime city ambiance",
        color_temp="Mixed sources - 2700K warm street lamps, 6500K cool LEDs, colored gels from neon (unmeasurable, creative)",
        contrast_ratio="Varies wildly, pools of light in darkness, high contrast urban nightscape",
        mood_effect="Urban, nocturnal, neon-noir, cyberpunk, energetic, gritty"
    ),

    "firelight_warm": LightingSetup(
        name="Firelight Warm Flicker",
        description="Motivated fireplace or campfire lighting",
        key_light="Simulated fire source - dimmed tungsten fresnel with orange gel on dimmer creating flicker effect, positioned low as fire would be",
        fill_light="Ambient room bounce or natural fill, kept very subtle to maintain fire as dominant source",
        back_light="Possible motivated candle or lantern behind subject for separation, also orange tungsten quality",
        practicals="Actual fire in background (controlled), candles, lanterns - all warm tungsten quality sources",
        atmosphere="Smoke or haze revealing light quality, warm orange glow washing over scene, flickering dancing shadows",
        color_temp="2000-2700K very warm orange fire quality, deep amber tones",
        contrast_ratio="Variable due to flicker, approximately 4:1 average but constantly changing",
        mood_effect="Cozy, intimate, primitive, warm, comfort, nostalgic, storytelling"
    ),

    "overcast_soft": LightingSetup(
        name="Overcast Soft Daylight",
        description="Cloudy day's soft shadowless light",
        key_light="Entire overcast sky as one giant softbox, directionless soft light from above, shadowless illumination",
        fill_light="Not needed as light is completely diffused and wraparound, no distinct key and fill just ambient soft light",
        back_light="None, relying on depth and color separation rather than lighting contrast",
        practicals="None, purely natural overcast daylight",
        atmosphere="Soft muted ambiance, desaturated quality, peaceful stillness, slight diffusion",
        color_temp="6500-7000K slightly cool daylight, can have blue-gray cast",
        contrast_ratio="1:1 to 1.5:1 extremely low contrast, almost flat lighting",
        mood_effect="Melancholic, contemplative, muted, realistic, documentary feel"
    ),

    "high_key_commercial": LightingSetup(
        name="High Key Commercial",
        description="Bright, evenly lit commercial advertising look",
        key_light="Large soft source from 45°, bright and flattering, beauty light quality",
        fill_light="Strong fill from camera axis reducing shadows nearly to nothing, ratio 2:1 for bright commercial look",
        back_light="Bright rim light separating subject from background, background also lit brightly",
        practicals="Additional background lights, practical lamps all on, everything bright and cheerful",
        atmosphere="Clean, bright, positive, no shadows or mystery, everything visible and crisp",
        color_temp="5600K daylight balanced throughout for clean commercial look",
        contrast_ratio="2:1 very low contrast, bright and even, minimizing all shadows",
        mood_effect="Happy, optimistic, commercial, clean, positive, energetic, welcoming"
    ),

    "low_key_noir": LightingSetup(
        name="Low Key Noir",
        description="Dark moody noir with selective lighting",
        key_light="Hard small source from extreme angle (side or back-side), creating selective illumination on parts of subject",
        fill_light="Very minimal fill or none, allowing 90% of frame to fall into darkness, ratio 10:1 or greater",
        back_light="Hard rim light defining edge against black background, creating separation through edge light only",
        practicals="Single motivated practical (desk lamp, street light) justifying the hard directional key",
        atmosphere="Smoke revealing light shafts, venetian blind patterns, deep inky blacks, mystery in shadows",
        color_temp="Mixed - often warm key 3200K from tungsten practical with cool rim 5600K for separation",
        contrast_ratio="10:1 or higher, most of frame in darkness with selective bright highlights",
        mood_effect="Noir, mysterious, dangerous, secretive, tense, cinematic drama"
    ),

    "magic_hour_backlight": LightingSetup(
        name="Magic Hour Backlight",
        description="Golden hour backlit sun flare glory",
        key_light="Sun behind subject creating backlight and rim light, subject in shadow but glowing with rim",
        fill_light="Open sky from front and bounce from environment providing soft fill on shadow side of subject, 3:1 ratio",
        back_light="Sun itself creating strong rim and hair light, lens flares and golden atmosphere",
        practicals="None needed, natural lighting only",
        atmosphere="Sun flares, golden rim light, dust particles illuminated, atmospheric haze, dreamy quality",
        color_temp="3200-5000K very warm golden orange, increasingly warm as sun lowers",
        contrast_ratio="4:1 with fill from environment, backlit subjects with glowing rims",
        mood_effect="Dreamlike, romantic, magical, nostalgic, hopeful, cinematic beauty"
    ),
}


def get_lighting(setup_name: str) -> LightingSetup:
    """Get a lighting setup by name."""
    return LIGHTING_SETUPS.get(setup_name, LIGHTING_SETUPS["three_point_studio"])


def find_lighting_by_mood(mood: str) -> list[LightingSetup]:
    """Find lighting setups matching a mood keyword."""
    results = []
    mood_lower = mood.lower()

    for setup in LIGHTING_SETUPS.values():
        if mood_lower in setup.mood_effect.lower():
            results.append(setup)

    return results


def get_lighting_for_time_of_day(time: str) -> list[LightingSetup]:
    """
    Get recommended lighting setups for time of day.

    Args:
        time: "morning", "midday", "afternoon", "evening", "night", "golden_hour", "blue_hour"
    """
    time_mapping = {
        "morning": ["natural_window_light", "overcast_soft"],
        "midday": ["overcast_soft", "high_key_commercial"],
        "afternoon": ["natural_window_light", "three_point_studio"],
        "golden_hour": ["golden_hour_exterior", "magic_hour_backlight"],
        "evening": ["blue_hour_twilight", "dramatic_single_source"],
        "blue_hour": ["blue_hour_twilight"],
        "night": ["neon_urban_night", "low_key_noir", "firelight_warm"],
    }

    setup_names = time_mapping.get(time.lower(), ["three_point_studio"])
    return [LIGHTING_SETUPS[name] for name in setup_names if name in LIGHTING_SETUPS]
