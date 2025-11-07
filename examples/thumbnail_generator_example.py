"""
Example: Thumbnail Generator with A/B Testing

Thumbnails determine 90% of whether someone clicks on your video!
This example shows how to create eye-catching thumbnails optimized for maximum CTR.

Key Stats:
- Thumbnails determine 90% of clicks
- Good thumbnail = 10x more views
- Faces in thumbnails = +38% CTR
- Surprised/shocked faces = +41% CTR
- A/B testing can double CTR

Run from project root with:
    PYTHONPATH=src python examples/thumbnail_generator_example.py
"""

from features.video.thumbnail_generator import ThumbnailGenerator, create_thumbnail


def example_basic_thumbnail():
    """Create a basic thumbnail"""
    print("=" * 60)
    print("Example 1: Create Basic Thumbnail")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    try:
        generator = ThumbnailGenerator()

        # Create thumbnail with auto-selected frame
        thumbnail_path = generator.create_thumbnail(
            video_path=video_path,
            output_path="thumbnail_basic.jpg",
            text="SHOCKING Result!",
            style="viral",
            platform="youtube",
            auto_select_frame=True  # Automatically find best frame
        )

        print(f"\n✅ Thumbnail created: {thumbnail_path}")
        print("   • Auto-selected best frame (face + emotion + contrast)")
        print("   • Viral style (yellow text, high contrast)")
        print("   • Optimized for YouTube (1280x720)")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("   Replace 'path/to/your/video.mp4' with your actual video")


def example_all_styles():
    """Create thumbnails with all available styles"""
    print("\n" + "=" * 60)
    print("Example 2: All Thumbnail Styles")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    styles = ["viral", "professional", "minimal", "energetic", "mystery", "educational"]

    print("\nCreating thumbnails with all styles:\n")

    try:
        generator = ThumbnailGenerator()

        for style in styles:
            output_path = f"thumbnail_{style}.jpg"

            generator.create_thumbnail(
                video_path=video_path,
                output_path=output_path,
                text=f"{style.upper()}!",
                style=style,
                platform="youtube"
            )

            print(f"✅ {style.capitalize():<15} -> {output_path}")

        print("\n💡 Compare all styles to find what works best for your content!")

    except FileNotFoundError:
        print("\n⚠️  Video file not found - showing style descriptions instead:\n")

        style_descriptions = {
            "viral": "Yellow text, high contrast - for maximum attention",
            "professional": "Clean, subtle - business-appropriate",
            "minimal": "Simple, elegant - less is more",
            "energetic": "Bright red, exciting - high energy content",
            "mystery": "Blue tones, intriguing - story-telling",
            "educational": "Blue/white, trustworthy - tutorials"
        }

        for style, desc in style_descriptions.items():
            print(f"{style.capitalize():<15} - {desc}")


def example_ab_testing():
    """Create multiple variations for A/B testing"""
    print("\n" + "=" * 60)
    print("Example 3: A/B Testing Thumbnails")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    # Different text variations to test
    text_variations = [
        "SHOCKING!",
        "You Won't Believe This",
        "This Changed Everything",
        "MUST SEE"
    ]

    try:
        generator = ThumbnailGenerator()

        print(f"\nCreating {len(text_variations)} thumbnail variations:\n")

        thumbnail_paths = generator.create_ab_test_variations(
            video_path=video_path,
            output_dir="ab_test_thumbnails/",
            text_variations=text_variations,
            style="viral",
            platform="youtube"
        )

        print("\n✅ A/B Test Thumbnails Created:")
        for i, (path, text) in enumerate(zip(thumbnail_paths, text_variations), 1):
            print(f"   {chr(64+i)}. {path}")
            print(f"      Text: \"{text}\"")

        print("\n💡 Upload these to YouTube and test which gets more clicks!")
        print("   A/B testing can double your CTR!")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("\nWhat A/B testing would create:")
        print("  • Multiple thumbnails with different text")
        print("  • Same style and frame for fair comparison")
        print("  • Test which text resonates with your audience")
        print("  • Data-driven decision making")


def example_platform_specific():
    """Create thumbnails for different platforms"""
    print("\n" + "=" * 60)
    print("Example 4: Platform-Specific Thumbnails")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    platforms = {
        "youtube": "16:9 landscape",
        "tiktok": "9:16 vertical",
        "instagram": "1:1 square",
        "facebook": "1.91:1 landscape",
        "twitter": "16:9 landscape",
        "linkedin": "1.91:1 landscape"
    }

    print("\nCreating platform-specific thumbnails:\n")

    try:
        generator = ThumbnailGenerator()

        for platform, aspect_ratio in platforms.items():
            output_path = f"thumbnail_{platform}.jpg"

            generator.create_thumbnail(
                video_path=video_path,
                output_path=output_path,
                text="WATCH THIS",
                style="viral",
                platform=platform
            )

            print(f"✅ {platform.capitalize():<12} ({aspect_ratio:<15}) -> {output_path}")

        print("\n💡 One video → 6 platform-optimized thumbnails!")

    except FileNotFoundError:
        print("\n⚠️  Video file not found - showing platform specs:\n")

        specs = {
            "YouTube": "1280x720 (16:9), Max 2MB",
            "TikTok": "1080x1920 (9:16), Max 5MB",
            "Instagram": "1080x1080 (1:1), Max 8MB",
            "Facebook": "1200x630 (1.91:1), Max 8MB",
            "Twitter": "1200x675 (16:9), Max 5MB",
            "LinkedIn": "1200x627 (1.91:1), Max 5MB"
        }

        for platform, spec in specs.items():
            print(f"{platform:<12} - {spec}")


def example_analyze_thumbnail():
    """Analyze thumbnail quality"""
    print("\n" + "=" * 60)
    print("Example 5: Analyze Thumbnail Quality")
    print("=" * 60)

    thumbnail_path = "path/to/your/thumbnail.jpg"

    try:
        generator = ThumbnailGenerator()

        score = generator.analyze_thumbnail(thumbnail_path)

        print(f"\n📊 Thumbnail Quality Analysis:\n")
        print(f"Overall Score: {score.overall_score:.1f}/100 ({score._get_grade()})")
        print(f"\nDetailed Scores:")
        print(f"  • Face Presence:  {score.face_score:.1f}/100")
        print(f"  • Contrast:       {score.contrast_score:.1f}/100")
        print(f"  • Text Quality:   {score.text_score:.1f}/100")
        print(f"  • Emotion/Exp:    {score.emotion_score:.1f}/100")
        print(f"  • Composition:    {score.composition_score:.1f}/100")

        if score.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in score.recommendations:
                print(f"   • {rec}")

        if score.warnings:
            print(f"\n⚠️  Warnings:")
            for warn in score.warnings:
                print(f"   • {warn}")

    except FileNotFoundError:
        print("\n⚠️  Thumbnail file not found")
        print("\nWhat analysis provides:")
        print("  • Overall quality score (0-100)")
        print("  • Face presence and size")
        print("  • Color contrast")
        print("  • Emotion detection")
        print("  • Actionable recommendations")


def example_specific_frame():
    """Create thumbnail from specific frame"""
    print("\n" + "=" * 60)
    print("Example 6: Use Specific Frame")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    try:
        generator = ThumbnailGenerator()

        # Use frame at 5.5 seconds
        thumbnail_path = generator.create_thumbnail(
            video_path=video_path,
            output_path="thumbnail_frame_5s.jpg",
            text="Amazing!",
            style="viral",
            platform="youtube",
            frame_time=5.5,  # Specific time in seconds
            auto_select_frame=False  # Don't auto-select
        )

        print(f"\n✅ Thumbnail created from 5.5 second mark")
        print(f"   Path: {thumbnail_path}")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("\nWhen to use specific frames:")
        print("  • You know exactly which moment looks best")
        print("  • Showing specific product/result")
        print("  • Matching thumbnail to key moment in video")


def example_best_practices():
    """Show thumbnail best practices"""
    print("\n" + "=" * 60)
    print("Example 7: Thumbnail Best Practices")
    print("=" * 60)

    print("\n📚 Thumbnail Best Practices:\n")

    print("1. TEXT:")
    print("   ✅ Keep under 4 words")
    print("   ✅ Large, readable font")
    print("   ✅ High contrast (yellow on dark)")
    print("   ❌ Full sentences")
    print("   ❌ Too much text\n")

    print("2. FACES:")
    print("   ✅ Show expressive emotions")
    print("   ✅ Face fills 40-60% of frame")
    print("   ✅ Close-up shots")
    print("   ✅ Surprised/shocked = +41% CTR")
    print("   ❌ Tiny faces")
    print("   ❌ Neutral expressions\n")

    print("3. COMPOSITION:")
    print("   ✅ Single clear focal point")
    print("   ✅ High contrast colors")
    print("   ✅ Simple, uncluttered")
    print("   ❌ Too busy")
    print("   ❌ Low contrast\n")

    print("4. TESTING:")
    print("   ✅ Create multiple variations")
    print("   ✅ A/B test with real audience")
    print("   ✅ Use data to decide")
    print("   ❌ Guess what works")
    print("   ❌ Use same thumbnail forever\n")


def example_text_guidelines():
    """Show text examples - good vs bad"""
    print("\n" + "=" * 60)
    print("Example 8: Text Guidelines")
    print("=" * 60)

    examples = [
        {
            "bad": "In this video I'm going to show you how to make money online",
            "good": "Make $1000",
            "why": "Too long → Concise"
        },
        {
            "bad": "cooking tutorial",
            "good": "SHOCKING Result!",
            "why": "Boring → Exciting"
        },
        {
            "bad": "video number 47",
            "good": "This Changed Everything",
            "why": "No value → Promise"
        },
        {
            "bad": "check this out",
            "good": "You Won't Believe This",
            "why": "Generic → Curiosity"
        }
    ]

    print("\n❌ BAD vs ✅ GOOD Thumbnail Text:\n")

    for i, ex in enumerate(examples, 1):
        print(f"{i}. ❌ BAD:  \"{ex['bad']}\"")
        print(f"   ✅ GOOD: \"{ex['good']}\"")
        print(f"   Why: {ex['why']}\n")


def example_style_comparison():
    """Compare different styles for same content"""
    print("\n" + "=" * 60)
    print("Example 9: Style Comparison")
    print("=" * 60)

    content_types = {
        "Tech Review": "professional",
        "Gaming Highlight": "energetic",
        "Mystery Story": "mystery",
        "Tutorial": "educational",
        "Viral Challenge": "viral",
        "Art/Design": "minimal"
    }

    print("\n🎨 Best Thumbnail Style by Content Type:\n")

    for content, style in content_types.items():
        print(f"{content:<20} → {style.capitalize()}")

    print("\n💡 Match style to your content for best results!")


def example_convenience_function():
    """Using convenience function"""
    print("\n" + "=" * 60)
    print("Example 10: Convenience Function")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    try:
        # Simple one-liner
        thumbnail = create_thumbnail(
            video_path=video_path,
            output_path="quick_thumbnail.jpg",
            text="WOW!",
            style="viral",
            platform="youtube"
        )

        print(f"\n✅ Quick thumbnail created: {thumbnail}")
        print("   Using convenience function - simplest way!")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("\nConvenience function:")
        print("  from features.video.thumbnail_generator import create_thumbnail")
        print("  thumbnail = create_thumbnail(video, output, text, style, platform)")
        print("  # That's it! 🎉")


def example_ctr_optimization():
    """CTR optimization tips"""
    print("\n" + "=" * 60)
    print("Example 11: CTR Optimization")
    print("=" * 60)

    print("\n📈 How to Maximize Click-Through Rate:\n")

    print("1. USE FACES (Minimum):")
    print("   • Thumbnails with faces = +38% CTR")
    print("   • Face should fill 40-60% of thumbnail")
    print("   • Use close-up shots, not wide angles\n")

    print("2. SHOW EMOTION (Big Impact):")
    print("   • Surprised/shocked faces = +41% CTR")
    print("   • Excited, amazed, or curious expressions")
    print("   • Avoid neutral, boring expressions\n")

    print("3. USE CONTRAST (Essential):")
    print("   • Yellow text on dark background works best")
    print("   • High contrast = eye-catching")
    print("   • Avoid similar colors (text blends in)\n")

    print("4. KEEP TEXT SHORT (Critical):")
    print("   • Maximum 3-4 words")
    print("   • Viewers scan quickly")
    print("   • Less is more\n")

    print("5. A/B TEST (Game Changer):")
    print("   • Create 3-5 variations")
    print("   • Test with real audience")
    print("   • Can double your CTR!")
    print("   • Use data, not guesses\n")

    print("💡 Good thumbnail = 10x more views!")


def main():
    """Run all examples"""
    print("🎨 Thumbnail Generator Examples")
    print("=" * 60)
    print("\nThumbnails determine 90% of clicks!")
    print("Use this tool to create eye-catching thumbnails.\n")

    # Run examples
    try:
        # Text-only examples (work without files)
        example_best_practices()
        example_text_guidelines()
        example_style_comparison()
        example_ctr_optimization()

        # Examples that need video files (uncomment when you have videos)
        # example_basic_thumbnail()
        # example_all_styles()
        # example_ab_testing()
        # example_platform_specific()
        # example_analyze_thumbnail()
        # example_specific_frame()
        # example_convenience_function()

        print("\n" + "=" * 60)
        print("📚 Key Takeaways:")
        print("=" * 60)
        print("\n1. Thumbnails determine 90% of clicks")
        print("2. Show expressive faces (40-60% of frame)")
        print("3. Keep text under 4 words")
        print("4. Use high contrast colors")
        print("5. A/B test multiple variations")
        print("6. Surprised/shocked faces = +41% CTR")
        print("7. Good thumbnail = 10x more views")
        print("\n💡 Create, test, optimize, repeat!")

    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  uv add moviepy pillow opencv-python")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
