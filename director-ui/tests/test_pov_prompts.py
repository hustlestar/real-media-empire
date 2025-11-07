"""
Tests for POV prompt engineering templates.

Tests prompt generation, style presets, and AI model optimization.
"""

import pytest
from src.text.pov_prompts import (
    POVPromptGenerator,
    POVPromptStyle,
    POV_STYLES,
    get_all_pov_styles,
    get_pov_style
)


class TestPOVStyles:
    """Test POV style presets."""

    def test_all_styles_exist(self):
        """Test all expected styles are defined."""
        expected_styles = [
            "gopro_action",
            "casual_phone",
            "desktop_work",
            "cinematic_pov",
            "tiktok_trending",
            "car_driving",
            "workout_training",
            "cooking_food"
        ]

        for style_name in expected_styles:
            assert style_name in POV_STYLES

    def test_style_structure(self):
        """Test each style has required fields."""
        for style_name, style in POV_STYLES.items():
            assert isinstance(style, POVPromptStyle)
            assert style.name
            assert style.description
            assert style.camera_angle
            assert style.perspective
            assert style.motion_style
            assert style.lighting_preference
            assert style.example

    def test_get_pov_style(self):
        """Test getting a specific style."""
        style = get_pov_style("gopro_action")
        assert style is not None
        assert style.name == "GoPro Action"

    def test_get_pov_style_invalid(self):
        """Test getting invalid style returns None."""
        style = get_pov_style("invalid_style")
        assert style is None

    def test_get_all_pov_styles(self):
        """Test getting all styles as dict."""
        all_styles = get_all_pov_styles()
        assert isinstance(all_styles, dict)
        assert len(all_styles) > 0
        assert "gopro_action" in all_styles


class TestPOVPromptGenerator:
    """Test POV prompt generation."""

    @pytest.fixture
    def generator(self):
        """Create POV prompt generator."""
        return POVPromptGenerator()

    def test_basic_prompt_generation(self, generator):
        """Test generating basic POV prompt."""
        prompt = generator.generate_pov_prompt(
            scene_description="working on laptop at cafe",
            style="casual_phone"
        )

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "working on laptop at cafe" in prompt
        assert "pov" in prompt.lower()

    def test_prompt_includes_camera_angle(self, generator):
        """Test prompt includes style-specific camera angle."""
        prompt = generator.generate_pov_prompt(
            scene_description="cycling through forest",
            style="gopro_action"
        )

        assert "gopro" in prompt.lower() or "first person" in prompt.lower()

    def test_prompt_adds_hands_if_missing(self, generator):
        """Test prompt adds visible body parts if not specified."""
        prompt = generator.generate_pov_prompt(
            scene_description="drinking coffee",
            style="casual_phone"
        )

        # Should add hands if not already mentioned
        assert "hand" in prompt.lower()

    def test_prompt_with_custom_environment(self, generator):
        """Test prompt with custom environment descriptor."""
        prompt = generator.generate_pov_prompt(
            scene_description="typing on laptop",
            style="desktop_work",
            environment="cozy home office with plants and natural light"
        )

        assert "cozy home office" in prompt.lower()
        assert "plants" in prompt.lower()

    def test_prompt_with_sensory_details(self, generator):
        """Test prompt includes sensory details."""
        prompt = generator.generate_pov_prompt(
            scene_description="drinking coffee at cafe",
            style="casual_phone",
            add_sensory_details=True
        )

        # Should include sensory details about coffee/cafe
        assert any(word in prompt.lower() for word in ["aroma", "smell", "coffee", "warm"])

    def test_prompt_without_sensory_details(self, generator):
        """Test prompt without sensory details."""
        prompt = generator.generate_pov_prompt(
            scene_description="working on laptop",
            style="desktop_work",
            add_sensory_details=False
        )

        # May not include sensory details
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_all_style_presets(self, generator):
        """Test generating prompts with all style presets."""
        scene = "working on project"

        for style_name in POV_STYLES.keys():
            prompt = generator.generate_pov_prompt(
                scene_description=scene,
                style=style_name
            )

            assert isinstance(prompt, str)
            assert len(prompt) > 50  # Should be detailed


class TestSensoryDetails:
    """Test sensory detail generation."""

    @pytest.fixture
    def generator(self):
        """Create POV prompt generator."""
        return POVPromptGenerator()

    def test_coffee_sensory_details(self, generator):
        """Test coffee scene gets coffee sensory details."""
        sensory = generator._generate_sensory_details("coffee at cafe", "casual_phone")

        assert sensory is not None
        assert any(word in sensory.lower() for word in ["coffee", "aroma", "warm"])

    def test_workout_sensory_details(self, generator):
        """Test workout scene gets appropriate details."""
        sensory = generator._generate_sensory_details("lifting weights at gym", "workout_training")

        assert sensory is not None
        assert any(word in sensory.lower() for word in ["sweat", "weights", "adrenaline"])

    def test_cooking_sensory_details(self, generator):
        """Test cooking scene gets appropriate details."""
        sensory = generator._generate_sensory_details("cooking pasta in kitchen", "cooking_food")

        assert sensory is not None
        assert any(word in sensory.lower() for word in ["aroma", "spices", "warm"])

    def test_generic_scene_sensory_details(self, generator):
        """Test generic scene may not get sensory details."""
        sensory = generator._generate_sensory_details("generic activity", "cinematic_pov")

        # May return None for generic scenes
        assert sensory is None or isinstance(sensory, str)


class TestStyleRecommendations:
    """Test style recommendations for platforms."""

    @pytest.fixture
    def generator(self):
        """Create POV prompt generator."""
        return POVPromptGenerator()

    def test_tiktok_recommendations(self, generator):
        """Test TikTok style recommendations."""
        recommendations = generator.get_style_recommendations("tiktok")

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert "tiktok_trending" in recommendations

    def test_youtube_recommendations(self, generator):
        """Test YouTube style recommendations."""
        recommendations = generator.get_style_recommendations("youtube")

        assert isinstance(recommendations, list)
        assert "cinematic_pov" in recommendations or "gopro_action" in recommendations

    def test_instagram_recommendations(self, generator):
        """Test Instagram style recommendations."""
        recommendations = generator.get_style_recommendations("instagram")

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_linkedin_recommendations(self, generator):
        """Test LinkedIn style recommendations."""
        recommendations = generator.get_style_recommendations("linkedin")

        assert isinstance(recommendations, list)
        assert "desktop_work" in recommendations or "cinematic_pov" in recommendations

    def test_all_platforms_have_recommendations(self, generator):
        """Test all platforms have recommendations."""
        platforms = ["tiktok", "youtube", "instagram", "twitter", "linkedin"]

        for platform in platforms:
            recommendations = generator.get_style_recommendations(platform)
            assert len(recommendations) > 0


class TestAIModelOptimization:
    """Test AI model-specific prompt optimization."""

    @pytest.fixture
    def generator(self):
        """Create POV prompt generator."""
        return POVPromptGenerator()

    def test_flux_optimization(self, generator):
        """Test optimization for Flux model."""
        base_prompt = "POV shot of hands typing on keyboard"

        optimized = generator.optimize_for_ai_model(base_prompt, model="flux")

        assert "realistic" in optimized.lower() or "photorealistic" in optimized.lower()
        assert len(optimized) > len(base_prompt)

    def test_kling_optimization(self, generator):
        """Test optimization for Kling model."""
        base_prompt = "POV shot of walking down street"

        optimized = generator.optimize_for_ai_model(base_prompt, model="kling")

        assert "motion" in optimized.lower() or "camera" in optimized.lower()

    def test_minimax_optimization(self, generator):
        """Test optimization for Minimax model."""
        base_prompt = "POV of driving car"

        optimized = generator.optimize_for_ai_model(base_prompt, model="minimax")

        assert "camera" in optimized.lower() or "zoom" in optimized.lower()

    def test_runway_optimization(self, generator):
        """Test optimization for Runway model."""
        base_prompt = "POV artistic shot"

        optimized = generator.optimize_for_ai_model(base_prompt, model="runway")

        assert "cinematic" in optimized.lower() or "artistic" in optimized.lower()

    def test_optimization_preserves_base_prompt(self, generator):
        """Test optimization preserves original prompt."""
        base_prompt = "POV shot of specific unique action"

        for model in ["flux", "kling", "minimax", "runway"]:
            optimized = generator.optimize_for_ai_model(base_prompt, model=model)
            assert base_prompt in optimized


class TestPromptQuality:
    """Test prompt quality and structure."""

    @pytest.fixture
    def generator(self):
        """Create POV prompt generator."""
        return POVPromptGenerator()

    def test_prompt_is_complete_sentence(self, generator):
        """Test generated prompts are complete sentences."""
        prompt = generator.generate_pov_prompt(
            scene_description="working on laptop",
            style="desktop_work"
        )

        assert prompt.endswith('.')
        assert not prompt.endswith('..')

    def test_prompt_no_double_semicolons(self, generator):
        """Test prompts don't have formatting errors."""
        prompt = generator.generate_pov_prompt(
            scene_description="cooking dinner",
            style="cooking_food"
        )

        assert ';;' not in prompt
        assert '..' not in prompt

    def test_prompt_has_depth(self, generator):
        """Test prompts have foreground and background."""
        prompt = generator.generate_pov_prompt(
            scene_description="drinking coffee",
            style="casual_phone"
        )

        assert "background" in prompt.lower()

    def test_prompt_length_reasonable(self, generator):
        """Test prompts are not too short or too long."""
        prompt = generator.generate_pov_prompt(
            scene_description="working",
            style="desktop_work"
        )

        # Should be detailed but not excessive
        assert 50 < len(prompt) < 1000
