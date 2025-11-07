"""
POV (Point-of-View) Prompt Engineering Templates

Advanced prompt templates for generating cinematic, immersive visual content
optimized for AI video and image generation (Flux, Kling, Minimax, Runway).
"""

from typing import Literal, Optional
from pydantic import BaseModel


class POVPromptStyle(BaseModel):
    """POV prompt style configuration."""
    name: str
    description: str
    camera_angle: str
    perspective: str
    motion_style: str
    lighting_preference: str
    example: str


# POV Style Presets

POV_STYLES = {
    "gopro_action": POVPromptStyle(
        name="GoPro Action",
        description="First-person action camera perspective with dynamic motion",
        camera_angle="First person view POV GoPro shot",
        perspective="Viewer sees their own hands, limbs, feet in frame",
        motion_style="Fast-paced, handheld, lots of movement",
        lighting_preference="Natural lighting, high contrast",
        example="First person view POV GoPro shot of my hands gripping a mountain bike handlebar as I race down a forest trail, dirt flying under spinning wheels; in the background, pine trees blur past, sunlight strobing through branches, the smell of pine and earth hitting my senses as my heart pounds from the adrenaline rush."
    ),

    "casual_phone": POVPromptStyle(
        name="Casual Phone",
        description="Natural smartphone recording perspective, UGC-style",
        camera_angle="POV phone camera view",
        perspective="Handheld, slightly shaky, casual framing",
        motion_style="Gentle, natural movements",
        lighting_preference="Indoor/outdoor natural light",
        example="POV phone camera view of my hand holding a coffee cup in a cozy cafe, steam rising from the dark liquid; in the background, soft morning light streams through large windows, barista working an espresso machine, the warm smell of roasted beans and quiet chatter filling the air."
    ),

    "desktop_work": POVPromptStyle(
        name="Desktop Work",
        description="Working at desk perspective, productivity content",
        camera_angle="POV looking down at desk",
        perspective="Top-down or slight angle, shows workspace",
        motion_style="Minimal movement, focused actions",
        lighting_preference="Desk lamp or natural window light",
        example="POV looking down at my hands typing on a sleek laptop, fingers flying across keys; in the background, a minimalist desk setup with a coffee mug, notebook, and desk lamp casting warm light, the quiet hum of productivity and soft keyboard clicks filling the workspace."
    ),

    "cinematic_pov": POVPromptStyle(
        name="Cinematic POV",
        description="Film-quality first-person perspective with dramatic flair",
        camera_angle="Cinematic first-person perspective",
        perspective="Steady, professional framing with visible body parts",
        motion_style="Smooth, intentional camera movements",
        lighting_preference="Dramatic, well-lit, professional",
        example="Cinematic first-person perspective of my hand reaching for a golden doorknob in a grand hallway, light reflecting off polished brass; in the background, ornate ceiling details, soft chandelier glow, marble floors gleaming, the weight of anticipation heavy in the silent, luxurious space."
    ),

    "tiktok_trending": POVPromptStyle(
        name="TikTok Trending",
        description="Viral TikTok style with trendy aesthetics",
        camera_angle="POV TikTok camera view",
        perspective="Casual, relatable, showing action in progress",
        motion_style="Quick cuts implied, energetic",
        lighting_preference="Bright, colorful, ring light or natural",
        example="POV TikTok camera view of my freshly manicured hand holding a trendy iced matcha latte, aesthetic green swirls visible through clear cup; in the background, a chic coffee shop with plants, neon signs, and soft lo-fi music playing, perfect for that viral moment."
    ),

    "car_driving": POVPromptStyle(
        name="Car Driving",
        description="Inside car perspective, road trip vibes",
        camera_angle="POV from driver seat",
        perspective="Shows steering wheel, hands, dashboard",
        motion_style="Steady forward motion, slight vibrations",
        lighting_preference="Dashboard glow, street lights, sunset",
        example="POV from driver seat of my hands gripping a leather steering wheel, dashboard glowing softly in twilight; in the background, an open highway stretching ahead, sun setting on the horizon painting sky orange and pink, radio playing low, sense of freedom and adventure."
    ),

    "workout_training": POVPromptStyle(
        name="Workout Training",
        description="Gym or exercise perspective, motivation content",
        camera_angle="POV workout shot",
        perspective="Shows body during exercise, mirror reflection optional",
        motion_style="Dynamic, shows physical effort",
        lighting_preference="Gym lighting, natural contrast",
        example="POV workout shot of my hands chalk-dusted gripping a barbell, veins visible from exertion; in the background, gym equipment, mirrors reflecting focused determination, the clang of weights and heavy breathing, sweat and adrenaline fueling the grind."
    ),

    "cooking_food": POVPromptStyle(
        name="Cooking Food",
        description="Kitchen cooking perspective, recipe content",
        camera_angle="POV looking down at cooking surface",
        perspective="Shows hands preparing food",
        motion_style="Methodical, step-by-step actions",
        lighting_preference="Kitchen overhead lights, natural window light",
        example="POV looking down at my hands dicing fresh vegetables on a wooden cutting board, knife gliding through vibrant red tomatoes; in the background, a bright kitchen with pots simmering on the stove, herbs hanging to dry, the aroma of garlic and olive oil filling the warm space."
    )
}


class POVPromptGenerator:
    """
    Generate cinematic POV prompts for AI image/video generation.

    Creates detailed, sensory-rich prompts optimized for platforms like
    Flux, Kling, Minimax, and Runway.
    """

    def generate_pov_prompt(
        self,
        scene_description: str,
        style: Literal[
            "gopro_action",
            "casual_phone",
            "desktop_work",
            "cinematic_pov",
            "tiktok_trending",
            "car_driving",
            "workout_training",
            "cooking_food"
        ] = "gopro_action",
        environment: Optional[str] = None,
        add_sensory_details: bool = True
    ) -> str:
        """
        Generate a POV prompt from a basic scene description.

        Args:
            scene_description: Basic description (e.g., "working on laptop at cafe")
            style: POV style preset to use
            environment: Optional environment descriptor to weave in
            add_sensory_details: Add sensory details (smell, sound, temperature)

        Returns:
            Detailed POV prompt ready for AI generation

        Example:
            >>> generator = POVPromptGenerator()
            >>> prompt = generator.generate_pov_prompt(
            ...     "drinking coffee at cafe",
            ...     style="casual_phone"
            ... )
        """
        style_config = POV_STYLES[style]

        # Build prompt structure
        prompt_parts = []

        # 1. Camera angle + foreground action
        foreground = f"{style_config.camera_angle} of {scene_description}"

        # 2. Add visible body parts if not specified
        if "hand" not in scene_description.lower() and "foot" not in scene_description.lower():
            foreground += ", hands visible in frame"

        prompt_parts.append(foreground)

        # 3. Background and environment
        if environment:
            background = f"in the background, {environment}"
        else:
            background = "in the background, detailed environment with depth"

        prompt_parts.append(background)

        # 4. Sensory details
        if add_sensory_details:
            sensory = self._generate_sensory_details(scene_description, style)
            if sensory:
                prompt_parts.append(sensory)

        # 5. Add lighting hint based on style
        lighting = style_config.lighting_preference.lower()
        if "natural" in lighting:
            prompt_parts.append("natural lighting")
        elif "dramatic" in lighting:
            prompt_parts.append("dramatic cinematic lighting")

        # Combine into single flowing sentence
        full_prompt = "; ".join(prompt_parts) + "."

        # Clean up formatting
        full_prompt = full_prompt.replace(";;", ";").replace("..", ".")

        return full_prompt

    def _generate_sensory_details(
        self,
        scene_description: str,
        style: str
    ) -> Optional[str]:
        """Generate sensory details based on scene and style."""
        scene_lower = scene_description.lower()

        # Context-based sensory details
        sensory_map = {
            "coffee": "the rich aroma of coffee and warm atmosphere",
            "cafe": "the warm smell of roasted beans and quiet chatter",
            "laptop": "the soft hum of typing and focused concentration",
            "typing": "keyboard clicks and screen glow",
            "workout": "sweat and adrenaline, the clang of weights",
            "weights": "sweat and adrenaline, the clang of weights",
            "gym": "sweat and adrenaline, the smell of rubber mats",
            "cooking": "aromatic spices and sizzling sounds",
            "kitchen": "the warmth of the stove and savory scents",
            "driving": "engine hum and sense of motion",
            "car": "dashboard lights and road vibrations",
            "bike": "wind rushing past and heart pounding",
            "running": "breathing heavy and muscles burning",
            "phone": "screen brightness and notification sounds",
            "scrolling": "blue light glow and endless content",
        }

        for keyword, sensory in sensory_map.items():
            if keyword in scene_lower:
                return sensory

        return None

    def get_style_recommendations(
        self,
        platform: Literal["tiktok", "youtube", "instagram", "twitter", "linkedin"]
    ) -> list[str]:
        """
        Get recommended POV styles for a platform.

        Args:
            platform: Target social media platform

        Returns:
            List of recommended style names
        """
        platform_styles = {
            "tiktok": ["tiktok_trending", "casual_phone", "gopro_action"],
            "youtube": ["cinematic_pov", "gopro_action", "desktop_work"],
            "instagram": ["tiktok_trending", "casual_phone", "cooking_food"],
            "twitter": ["casual_phone", "desktop_work"],
            "linkedin": ["desktop_work", "cinematic_pov"]
        }

        return platform_styles.get(platform, ["gopro_action", "casual_phone"])

    def optimize_for_ai_model(
        self,
        prompt: str,
        model: Literal["flux", "kling", "minimax", "runway"] = "flux"
    ) -> str:
        """
        Optimize prompt for specific AI model characteristics.

        Args:
            prompt: Base POV prompt
            model: Target AI model

        Returns:
            Optimized prompt
        """
        # Model-specific optimizations
        if model == "flux":
            # Flux likes detailed, photorealistic descriptions
            if "realistic" not in prompt.lower():
                prompt += " Photorealistic, high detail, professional quality."

        elif model == "kling":
            # Kling is video-focused, add motion cues
            if "motion" not in prompt.lower() and "moving" not in prompt.lower():
                prompt += " Smooth camera movement, cinematic motion."

        elif model == "minimax":
            # Minimax likes specific camera movements
            prompt += " Camera pan and zoom, dynamic framing."

        elif model == "runway":
            # Runway Gen-3 likes artistic descriptions
            prompt += " Cinematic composition, film-quality aesthetic."

        return prompt


# Export all POV styles for easy access
def get_all_pov_styles() -> dict:
    """Get all available POV style configurations."""
    return {name: style.dict() for name, style in POV_STYLES.items()}


def get_pov_style(name: str) -> Optional[POVPromptStyle]:
    """Get a specific POV style by name."""
    return POV_STYLES.get(name)
