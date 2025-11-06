"""
Professional cinematic styles library.
Curated by a world-class film producer and director.
"""

from typing import List
from pydantic import BaseModel


class CinematicStyle(BaseModel):
    """Professional cinematic style definition"""
    name: str
    description: str
    lighting: str
    color_grading: str
    camera_work: str
    mood: str
    reference_films: List[str]


# ============================================================================
# PROFESSIONAL CINEMATIC STYLES
# ============================================================================

CINEMATIC_STYLES = {
    "hollywood_blockbuster": CinematicStyle(
        name="Hollywood Blockbuster",
        description="Epic, high-budget Hollywood production quality with theatrical gravitas",
        lighting="Three-point dramatic lighting with strong key lights at 45°, subtle rim lighting for separation, professional studio-grade illumination, contrast ratio 4:1, motivated practical sources",
        color_grading="Rich, saturated colors with lifted blacks (never crushed), warm-cool contrast for depth, Arri Alexa organic look, subtle teal-orange complementary color scheme, 2.39:1 cinematic framing aesthetic",
        camera_work="Smooth steadicam gliding movements, professional gimbal work with precise operator control, rack focus pulls for emphasis, shallow depth of field (T2.8-T4), 24mm-85mm prime lenses, dynamic composition with leading lines",
        mood="Epic, powerful, emotionally engaging, larger than life",
        reference_films=["Inception (Wally Pfister)", "The Dark Knight (Wally Pfister)", "Interstellar (Hoyte van Hoytema)", "Dune (Greig Fraser)"]
    ),

    "indie_cinema": CinematicStyle(
        name="Independent Cinema",
        description="Naturalistic, character-driven indie film aesthetic with raw authenticity",
        lighting="Natural window light, soft diffusion through 4x4 silks, practical lamps as motivated sources, minimal artificial lighting, golden hour magic hour timing, contrast ratio 2:1 for gentle falloff",
        color_grading="Desaturated natural tones, subtle film grain emulation (35mm 500T), low contrast organic look, warm amber undertones, preserving skin tone integrity, slight green push for naturalism",
        camera_work="Intimate handheld with operator breathing, close-up character work, shallow depth of field for isolation (T2-T2.8), following natural character movement, imperfect framing for authenticity, 35mm-50mm focal lengths",
        mood="Intimate, contemplative, authentic, emotionally honest",
        reference_films=["Moonlight (James Laxton)", "Lady Bird (Sam Levy)", "The Florida Project (Alexis Zabe)", "Nomadland (Joshua James Richards)"]
    ),

    "commercial_luxury": CinematicStyle(
        name="Luxury Brand Commercial",
        description="High-end premium brand commercial aesthetic with flawless execution",
        lighting="Perfect studio lighting with softboxes and large diffusion sources, flawless product lighting with mirror boards, dramatic shadows with precise control, pristine highlights without clipping, 8:1 contrast for drama",
        color_grading="Crisp, clean whites (never blown), rich inky blacks with detail, premium metallic tones with specular highlights, jewel-like saturated colors, teal-gold luxury palette, perfect skin tones",
        camera_work="Slow motion product reveals at 120fps minimum, precise motorized slider movements, macro detail shots with focus breathing compensation, locked-off perfection shots, dynamic Dutch angles for energy",
        mood="Sophisticated, aspirational, premium, desire-inducing",
        reference_films=["Apple 'Shot on iPhone' campaigns", "Lexus 'Amazing in Motion'", "Chanel N°5 films", "Mercedes-Benz 'The Best or Nothing'"]
    ),

    "documentary_real": CinematicStyle(
        name="Documentary Realism",
        description="Authentic documentary filmmaking style with journalistic integrity",
        lighting="Available light only with reflectors for fill, natural exposure curves, real-world imperfections embraced, no artificial lighting sources, honest exposure even if underexposed",
        color_grading="Neutral, truthful colors with minimal grading intervention, preserving reality, slight desaturation for objectivity, contrast matched to shooting conditions, natural skin tones without manipulation",
        camera_work="Observational camera with handheld spontaneity, reactive framing following action, documentary-style following movements, focus pulls for emphasis, 24-70mm zoom for flexibility",
        mood="Honest, real, unfiltered, journalistic, truthful",
        reference_films=["Planet Earth II (BBC)", "Free Solo (Jimmy Chin)", "13th (Ava DuVernay)", "Won't You Be My Neighbor (Nicholas Ma)"]
    ),

    "music_video_stylized": CinematicStyle(
        name="Music Video Stylized",
        description="Bold, creative music video aesthetic with artistic freedom",
        lighting="Dramatic colored gels (Rosco/Lee filters), practical neon fixtures, bold shadow play with hard sources, creative light painting, smoke and atmosphere for depth, contrasting color temperatures",
        color_grading="High contrast with crushed blacks and blown highlights for style, bold color choices with complementary clashes, creative LUTs and film emulation, experimental grading pushing boundaries",
        camera_work="Dynamic camera movements synchronized to rhythm, creative Dutch angles and perspective distortion, whip pans and crash zooms, slow motion at 240fps for emphasis, ultra-wide 14mm to telephoto 200mm",
        mood="Energetic, bold, artistic, rhythm-driven, unconventional",
        reference_films=["Childish Gambino 'This Is America' (Hiro Murai)", "Kendrick Lamar 'HUMBLE.' (Dave Meyers)", "Billie Eilish 'bad guy' (Dave Meyers)"]
    ),

    "noir_dramatic": CinematicStyle(
        name="Film Noir Dramatic",
        description="Classic noir aesthetic with dramatic chiaroscuro lighting",
        lighting="Hard single source lighting creating stark shadows, venetian blind patterns and dramatic slats, smoke and fog for atmospheric depth, motivated streetlights and practicals, 16:1 contrast ratio for maximum drama",
        color_grading="High contrast with deep blacks and bright highlights, desaturated with blue-teal color push, or pure black and white with controlled silver tones, preserving shadow detail for mood",
        camera_work="Low angle compositions for dramatic perspective, Dutch angles for psychological unease, static tripod for noir stillness, dramatic foreground elements for depth, 35mm-50mm classic focal lengths",
        mood="Mysterious, tense, atmospheric, morally ambiguous, shadowy",
        reference_films=["Blade Runner (Jordan Cronenweth)", "Drive (Newton Thomas Sigel)", "Sin City (Robert Rodriguez)", "The Batman (Greig Fraser)"]
    ),

    "social_media_native": CinematicStyle(
        name="Social Media Native",
        description="Modern social media optimized aesthetic for viral content",
        lighting="Ring light beauty lighting for flattering skin, RGB LED panels for trending colored backgrounds, soft frontal lighting to minimize shadows, bright and punchy for small screens",
        color_grading="Vibrant saturated colors that pop on mobile, lifted shadows for visibility, warm skin tones with peachy undertones, trendy color palettes (millennial pink, gen-z yellow)",
        camera_work="Vertical 9:16 framing for stories/reels, direct-to-camera POV style, dynamic quick cuts, smooth gimbal moves, close-ups optimized for small screens",
        mood="Energetic, relatable, authentic, engaging, trendy",
        reference_films=["MrBeast productions", "Emma Chamberlain vlogs", "TikTok trending formats", "Instagram Reels viral content"]
    ),

    "scifi_futuristic": CinematicStyle(
        name="Sci-Fi Futuristic",
        description="High-tech science fiction aesthetic with futuristic vision",
        lighting="Cool blue-cyan lighting for technology, hard rim lights for separation, practical LED panels and screens as sources, volumetric fog for atmosphere, contrast between warm humans and cool tech",
        color_grading="Blue-teal futuristic palette, desaturated except for accent colors, clean highlights suggesting advanced technology, subtle purple undertones, enhanced contrast for definition",
        camera_work="Precise mechanical camera movements suggesting automation, slow push-ins on technology, symmetrical framing for artificial environments, wide establishing shots of futuristic spaces",
        mood="Futuristic, technological, clinical, awe-inspiring, otherworldly",
        reference_films=["Ex Machina (Rob Hardy)", "Blade Runner 2049 (Roger Deakins)", "Her (Hoyte van Hoytema)", "Arrival (Bradford Young)"]
    ),

    "horror_atmospheric": CinematicStyle(
        name="Horror Atmospheric",
        description="Psychological horror aesthetic with dread and tension",
        lighting="Low key lighting with deep shadows concealing threats, motivated practical sources creating pools of light, hard backlight creating silhouettes, underexposed for mystery, 12:1 contrast",
        color_grading="Desaturated with sickly green or cold blue undertones, lifted blacks for oppressive darkness, muted colors suggesting decay, selective color for symbolic elements",
        camera_work="Slow creeping push-ins building tension, low angles suggesting powerlessness, wide shots showing isolation, handheld for claustrophobic scenes, Dutch angles for psychological horror",
        mood="Tense, unsettling, dreadful, mysterious, oppressive",
        reference_films=["Hereditary (Pawel Pogorzelski)", "The Witch (Jarin Blaschke)", "It Follows (Mike Gioulakis)", "Midsommar (Pawel Pogorzelski)"]
    ),

    "vintage_nostalgia": CinematicStyle(
        name="Vintage Nostalgia",
        description="Warm nostalgic aesthetic evoking memories and simpler times",
        lighting="Soft diffused sunlight through windows, warm golden hour lighting, practical tungsten lamps for warmth, gentle falloff, 3:1 contrast for softness",
        color_grading="Warm amber and honey tones throughout, slightly faded colors suggesting age, film grain and halation, subtle vignetting, lifted blacks for vintage softness",
        camera_work="Gentle slow zooms suggesting memory, soft focus with vintage glass character, static compositions suggesting photographs, center-framed subjects",
        mood="Nostalgic, warm, comforting, sentimental, timeless",
        reference_films=["Call Me By Your Name (Sayombhu Mukdeeprom)", "The Grand Budapest Hotel (Robert Yeoman)", "Carol (Ed Lachman)", "Amélie (Bruno Delbonnel)"]
    ),
}


def get_style(style_name: str) -> CinematicStyle:
    """Get a cinematic style by name."""
    return CINEMATIC_STYLES.get(style_name, CINEMATIC_STYLES["hollywood_blockbuster"])


def list_all_styles() -> List[str]:
    """List all available cinematic style names."""
    return list(CINEMATIC_STYLES.keys())


def search_styles(mood: str = None, keyword: str = None) -> List[CinematicStyle]:
    """
    Search styles by mood or keyword.

    Examples:
        search_styles(mood="epic")
        search_styles(keyword="documentary")
    """
    results = []

    for style in CINEMATIC_STYLES.values():
        if mood and mood.lower() in style.mood.lower():
            results.append(style)
        elif keyword and keyword.lower() in (style.description + style.name).lower():
            results.append(style)

    return results
