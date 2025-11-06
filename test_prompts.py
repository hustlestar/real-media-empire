"""
Quick test of the professional cinematic prompt system.

Run with: uv run python test_prompts.py
"""

from src.features.film.prompts import CinematicPromptBuilder

def test_single_shot():
    """Test building a single professional shot"""
    print("=" * 80)
    print("TEST 1: Single Shot - Tech Startup Success Moment")
    print("=" * 80)

    builder = CinematicPromptBuilder()

    result = builder.build_shot(
        subject="Emma, professional woman in her 30s, confident CEO",
        action="reviewing successful product metrics on laptop, moment of triumph",
        location="modern tech office with floor-to-ceiling windows, city skyline visible, golden hour light",
        style="commercial_luxury",
        shot_type="medium_closeup",
        lighting="golden_hour_exterior",
        emotion="triumph_victory"
    )

    print("\n🎬 PROFESSIONAL PROMPT:")
    print("-" * 80)
    print(result.prompt[:500] + "...\n")

    print("\n📝 DIRECTOR'S NOTES:")
    print("-" * 80)
    print(result.director_notes)

    print("\n🎥 TECHNICAL NOTES:")
    print("-" * 80)
    print(result.technical_notes)

    print("\n📊 METADATA:")
    print("-" * 80)
    for key, value in result.metadata.items():
        print(f"  {key}: {value}")


def test_scene_sequence():
    """Test building a complete scene with multiple shots"""
    print("\n\n")
    print("=" * 80)
    print("TEST 2: Complete Scene - Product Launch Celebration")
    print("=" * 80)

    builder = CinematicPromptBuilder()

    results = builder.build_scene_sequence(
        scene_description="Tech team celebrates successful product launch",
        characters=["Emma (CEO)", "David (CTO)", "Sarah (Designer)"],
        location="modern startup office with exposed brick, tech equipment, city views",
        num_shots=5,
        style="hollywood_blockbuster",
        pacing="dynamic"
    )

    for i, result in enumerate(results, 1):
        print(f"\n🎬 SHOT {i} of {len(results)}")
        print("-" * 80)
        print(f"Type: {result.metadata['shot_type']}")
        print(f"Emotion: {result.metadata['emotion']}")
        print(f"Duration: {result.metadata['duration_range'][0]}-{result.metadata['duration_range'][1]}s")
        print(f"\nPrompt Preview: {result.prompt[:200]}...")


def test_style_comparison():
    """Test different cinematic styles"""
    print("\n\n")
    print("=" * 80)
    print("TEST 3: Style Comparison - Same Shot, Different Styles")
    print("=" * 80)

    builder = CinematicPromptBuilder()

    styles = ["hollywood_blockbuster", "indie_cinema", "noir_dramatic", "social_media_native"]

    for style in styles:
        result = builder.build_shot(
            subject="entrepreneur at desk",
            action="working late at night",
            location="small office",
            style=style,
            shot_type="medium_shot",
            lighting="natural_window_light",
            emotion="determination_resolve"
        )

        print(f"\n🎨 STYLE: {style.upper()}")
        print("-" * 80)
        print(f"Mood: {result.metadata['reference_films']}")
        print(f"Preview: {result.prompt[:150]}...")


if __name__ == "__main__":
    print("\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "   PROFESSIONAL CINEMATIC PROMPT SYSTEM TEST".center(78) + "█")
    print("█" + "   World-Class Film Production Quality".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    test_single_shot()
    test_scene_sequence()
    test_style_comparison()

    print("\n\n")
    print("=" * 80)
    print("✅ ALL TESTS COMPLETE")
    print("=" * 80)
    print("\n🎬 Your prompt system is ready for Hollywood-grade content creation!")
    print("\nNext steps:")
    print("  1. Use these prompts in your film generation pipeline")
    print("  2. Connect to UI for easy access")
    print("  3. Create character consistency system")
    print("  4. Build prompt template library")
    print("\n")
