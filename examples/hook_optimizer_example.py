"""
Example: Hook Optimization - First 3 Seconds Analysis

The first 3 seconds determine if viewers watch or scroll.
This example shows how to analyze and optimize video hooks for maximum retention.

Key Stats:
- 65% of viewers decide in first 2 seconds
- 80% decision made by 3 seconds
- Strong hooks = 2-5x higher retention
- Hook optimization can boost watch time by 200%+

Run from project root with:
    PYTHONPATH=src python examples/hook_optimizer_example.py
"""

from features.video.hook_optimizer import HookOptimizer, analyze_hook, compare_hooks


def example_basic_analysis():
    """Basic hook analysis"""
    print("=" * 60)
    print("Example 1: Basic Hook Analysis")
    print("=" * 60)

    optimizer = HookOptimizer()

    # Analyze a hook
    # NOTE: Replace with your actual video file!
    video_path = "path/to/your/video.mp4"

    try:
        score = optimizer.analyze_hook(
            video_path=video_path,
            text="Did you know this iPhone trick will change your life?",
            platform="tiktok"
        )

        print(f"\n📊 Hook Analysis Results:")
        print(f"   Overall Score: {score.overall_score:.1f}/100 ({score._get_grade()})")
        print(f"   Visual Score:  {score.visual_score:.1f}/100")
        print(f"   Text Score:    {score.text_score:.1f}/100")
        print(f"   Audio Score:   {score.audio_score:.1f}/100")

        print(f"\n🎬 Visual Analysis:")
        print(f"   Motion:  {score.motion_score:.1f}/100")
        print(f"   Colors:  {score.color_impact:.1f}/100")
        print(f"   Faces:   {score.face_presence:.1f}/100")

        print(f"\n📝 Text Hook:")
        print(f"   Type: {score.hook_type}")
        print(f"   Strength: {score.text_hook_strength:.1f}/100")
        print(f"   Curiosity Gap: {score.curiosity_gap:.1f}/100")
        print(f"   Power Words: {', '.join(score.power_words) if score.power_words else 'None'}")

        print(f"\n🎤 Audio:")
        print(f"   Voice Energy: {score.voice_energy:.1f}/100")

        if score.pattern_interrupts:
            print(f"\n⚡ Pattern Interrupts:")
            for interrupt in score.pattern_interrupts:
                print(f"   • {interrupt}")

        if score.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in score.recommendations:
                print(f"   {rec}")

        if score.warnings:
            print(f"\n⚠️  Warnings:")
            for warn in score.warnings:
                print(f"   {warn}")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("   Replace 'path/to/your/video.mp4' with your actual video file")


def example_platform_comparison():
    """Compare hook performance across platforms"""
    print("\n" + "=" * 60)
    print("Example 2: Platform-Specific Analysis")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"
    text = "Watch what happens when I drop this iPhone in water!"

    platforms = ["tiktok", "youtube_shorts", "instagram_reels", "youtube"]

    try:
        optimizer = HookOptimizer()

        print(f"\nAnalyzing hook for different platforms:")
        print(f"Text: \"{text}\"\n")

        results = []
        for platform in platforms:
            score = optimizer.analyze_hook(
                video_path=video_path,
                text=text,
                platform=platform
            )
            results.append((platform, score.overall_score))

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)

        print(f"{'Platform':<20} {'Score':<10} {'Grade':<10}")
        print("-" * 40)
        for platform, score_val in results:
            grade = HookOptimizer().analyze_hook(video_path, text, platform)._get_grade()
            print(f"{platform:<20} {score_val:>6.1f}/100  {grade:<10}")

    except FileNotFoundError:
        print("\n⚠️  Video file not found - using demo mode")


def example_ab_testing():
    """A/B test multiple hook variations"""
    print("\n" + "=" * 60)
    print("Example 3: A/B Testing Hook Variations")
    print("=" * 60)

    # Multiple hook variations to test
    hooks = [
        {
            "video": "path/to/hook_a.mp4",
            "text": "How to make $1000 in 24 hours"
        },
        {
            "video": "path/to/hook_b.mp4",
            "text": "This money trick changed my life"
        },
        {
            "video": "path/to/hook_c.mp4",
            "text": "Watch me make money while I sleep"
        }
    ]

    try:
        video_paths = [h["video"] for h in hooks]
        texts = [h["text"] for h in hooks]

        scores = compare_hooks(
            video_paths=video_paths,
            texts=texts,
            platform="tiktok"
        )

        print(f"\n🏆 A/B Test Results (Best to Worst):\n")

        for i, score in enumerate(scores, 1):
            print(f"{i}. {score.variant_id} - {score.overall_score:.1f}/100 ({score._get_grade()})")
            print(f"   Text: \"{texts[i-1]}\"")
            print(f"   Visual: {score.visual_score:.1f} | Text: {score.text_score:.1f} | Audio: {score.audio_score:.1f}")

            if i == 1:
                print(f"   ✅ WINNER - Use this hook!")
                if score.recommendations:
                    print(f"   💡 Top tip: {score.recommendations[0]}")
            print()

        # Show score difference
        score_diff = scores[0].overall_score - scores[-1].overall_score
        print(f"Score range: {score_diff:.1f} points")
        print(f"Winner is {score_diff:.1f}% better than lowest")

    except FileNotFoundError:
        print("\n⚠️  Video files not found")
        print("   Replace paths with your actual test videos")


def example_text_hook_analysis():
    """Analyze text hooks only (without video)"""
    print("\n" + "=" * 60)
    print("Example 4: Text Hook Analysis")
    print("=" * 60)

    hooks = [
        "Did you know this iPhone trick?",
        "3 secrets Apple doesn't want you to know",
        "I tested every iPhone hack on TikTok",
        "Stop doing this to your iPhone",
        "This will change how you use your phone forever",
        "Watch what happens when I...",
        "You've been using your iPhone wrong",
        "How I got 1M views with this simple trick"
    ]

    print("\nAnalyzing text hooks:\n")
    print(f"{'Hook Text':<50} {'Type':<15} {'Power Words'}")
    print("-" * 90)

    optimizer = HookOptimizer()

    for hook_text in hooks:
        # Create dummy score for text analysis
        from features.video.hook_optimizer import HookScore
        score = HookScore()

        # Use internal method
        optimizer._analyze_text_hook(hook_text, "tiktok", score)

        power_words_str = ", ".join(score.power_words[:3]) if score.power_words else "-"
        print(f"{hook_text:<50} {score.hook_type:<15} {power_words_str}")


def example_hook_scoring_breakdown():
    """Detailed breakdown of how hooks are scored"""
    print("\n" + "=" * 60)
    print("Example 5: Hook Scoring Breakdown")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"
    text = "This secret iPhone hack will blow your mind!"

    try:
        optimizer = HookOptimizer()
        score = optimizer.analyze_hook(video_path, text, platform="tiktok")

        print(f"\n📊 Detailed Score Breakdown:\n")

        print("OVERALL SCORE: {:.1f}/100 ({})".format(score.overall_score, score._get_grade()))
        print("=" * 40)

        print("\n1. VISUAL COMPONENTS (40% of total):")
        print(f"   Total Visual Score: {score.visual_score:.1f}/100")
        print(f"   ├─ Motion (40%):      {score.motion_score:.1f}/100")
        print(f"   ├─ Colors (30%):      {score.color_impact:.1f}/100")
        print(f"   └─ Faces (30%):       {score.face_presence:.1f}/100")

        print("\n2. TEXT COMPONENTS (40% of total):")
        print(f"   Total Text Score: {score.text_score:.1f}/100")
        print(f"   ├─ Hook Type:         {score.hook_type}")
        print(f"   ├─ Hook Strength:     {score.text_hook_strength:.1f}/100")
        print(f"   ├─ Curiosity Gap:     {score.curiosity_gap:.1f}/100")
        print(f"   └─ Power Words:       {len(score.power_words)} found")

        print("\n3. AUDIO COMPONENTS (20% of total):")
        print(f"   Total Audio Score: {score.audio_score:.1f}/100")
        print(f"   └─ Voice Energy:      {score.voice_energy:.1f}/100")

        print("\n" + "=" * 40)
        print(f"WEIGHTED TOTAL: {score.overall_score:.1f}/100")

    except FileNotFoundError:
        print("\n⚠️  Using demo calculations")

        print("\nHook Scoring Formula:")
        print("Overall = (Visual × 0.4) + (Text × 0.4) + (Audio × 0.2)")
        print("\nVisual = (Motion × 0.4) + (Colors × 0.3) + (Faces × 0.3)")
        print("Text = (Strength × 0.5) + (Curiosity × 0.3) + (Length × 0.2)")


def example_hook_improvement():
    """Show before/after hook improvements"""
    print("\n" + "=" * 60)
    print("Example 6: Hook Improvement Examples")
    print("=" * 60)

    improvements = [
        {
            "before": "Hey guys, welcome back to my channel. Today I'm going to show you...",
            "after": "This iPhone trick saved me 2 hours every day",
            "improvement": "Removed intro, added specific value + curiosity"
        },
        {
            "before": "In this video, I'll teach you about productivity",
            "after": "I tested 50 productivity apps. Only 3 survived.",
            "improvement": "Added specificity + intrigue + authority"
        },
        {
            "before": "Let me tell you about my morning routine",
            "after": "My 3AM morning routine is weird but it works",
            "improvement": "Added pattern interrupt + curiosity gap"
        },
        {
            "before": "Here's how to cook pasta",
            "after": "Stop boiling pasta wrong - chef reveals secret",
            "improvement": "Added negative hook + authority + secret"
        }
    ]

    print("\n🔧 Hook Improvement Examples:\n")

    for i, example in enumerate(improvements, 1):
        print(f"{i}. BEFORE (❌):")
        print(f"   \"{example['before']}\"")
        print(f"\n   AFTER (✅):")
        print(f"   \"{example['after']}\"")
        print(f"\n   Why it's better: {example['improvement']}")
        print()


def example_platform_best_practices():
    """Platform-specific hook best practices"""
    print("\n" + "=" * 60)
    print("Example 7: Platform-Specific Best Practices")
    print("=" * 60)

    platforms = {
        "TikTok": {
            "duration": "2-3 seconds",
            "style": "Fast-paced, energetic, question-based",
            "good": "This secret TikTok hack...",
            "bad": "Hey TikTok, welcome to my page..."
        },
        "YouTube Shorts": {
            "duration": "3 seconds",
            "style": "Clear value prop, curiosity gap",
            "good": "I spent $10K testing this so you don't have to",
            "bad": "Today I'm going to show you about..."
        },
        "Instagram Reels": {
            "duration": "2-2.5 seconds",
            "style": "Visual hook, trending audio, FOMO",
            "good": "POV: You just discovered the makeup hack",
            "bad": "Hi friends, in today's reel..."
        },
        "YouTube": {
            "duration": "5-8 seconds",
            "style": "Tease outcome, promise value, build intrigue",
            "good": "This mistake cost me $50K. Here's how to avoid it.",
            "bad": "What's up guys, it's [name] here and today..."
        }
    }

    for platform, details in platforms.items():
        print(f"\n{platform}:")
        print(f"  Duration: {details['duration']}")
        print(f"  Style: {details['style']}")
        print(f"  ✅ Good: \"{details['good']}\"")
        print(f"  ❌ Bad:  \"{details['bad']}\"")


def example_power_words():
    """Show power words by category"""
    print("\n" + "=" * 60)
    print("Example 8: Power Words for Hooks")
    print("=" * 60)

    from features.video.hook_optimizer import HookOptimizer

    power_words = HookOptimizer.POWER_WORDS

    print("\n💎 Power Words by Category:\n")

    for category, words in power_words.items():
        print(f"{category.upper()}:")
        print(f"  {', '.join(words[:10])}")
        print(f"  Example: \"The {words[0]} to...\"\n")


def example_create_variations():
    """Create hook variations for testing"""
    print("\n" + "=" * 60)
    print("Example 9: Create Hook Variations")
    print("=" * 60)

    video_path = "path/to/source.mp4"
    output_dir = "hooks_test/"

    try:
        optimizer = HookOptimizer()

        print(f"\nCreating hook variations from: {video_path}")
        print(f"Output directory: {output_dir}\n")

        variations = [
            {"speed": 1.0, "zoom": 1.0, "name": "original"},
            {"speed": 1.1, "zoom": 1.0, "name": "10_percent_faster"},
            {"speed": 1.0, "zoom": 1.05, "name": "slight_zoom"},
            {"speed": 1.1, "zoom": 1.05, "name": "fast_and_zoom"},
        ]

        output_paths = optimizer.create_hook_variations(
            video_path=video_path,
            output_dir=output_dir,
            variations=variations
        )

        print("✅ Variations created:")
        for i, path in enumerate(output_paths, 1):
            print(f"   {i}. {path}")

        print(f"\n💡 Next: Test these variations with real audience to find winner!")

    except FileNotFoundError:
        print("\n⚠️  Source video not found")
        print("\nVariations that can be created:")
        print("  • Original speed & zoom")
        print("  • 10% faster (more engaging)")
        print("  • Slight zoom (1.05x - draws attention)")
        print("  • Fast + zoom (maximum energy)")


def main():
    """Run all examples"""
    print("🎬 Hook Optimizer Examples")
    print("=" * 60)
    print("\nThe first 3 seconds determine everything!")
    print("Use this tool to analyze and optimize your video hooks.\n")

    # Run examples
    try:
        # Text-only examples (work without video files)
        example_text_hook_analysis()
        example_hook_improvement()
        example_platform_best_practices()
        example_power_words()

        # Examples that need video files (uncomment when you have videos)
        # example_basic_analysis()
        # example_platform_comparison()
        # example_ab_testing()
        # example_hook_scoring_breakdown()
        # example_create_variations()

        print("\n" + "=" * 60)
        print("📚 Key Takeaways:")
        print("=" * 60)
        print("\n1. Hook in first 3 seconds (2 for TikTok/Reels)")
        print("2. Start with value, not introduction")
        print("3. Use questions or curiosity gaps")
        print("4. Add 1-2 power words")
        print("5. Show motion/action immediately")
        print("6. A/B test multiple variations")
        print("7. Match hook style to platform")
        print("\n💡 Strong hooks = 2-5x higher retention!")

    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  uv add moviepy opencv-python numpy")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
