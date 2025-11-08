"""
Example: Adding Automated Subtitles to Videos

This example demonstrates how to use the SubtitleGenerator to add
viral-style captions to your videos.

Run from project root with:
    PYTHONPATH=src python examples/subtitles_example.py
"""

from features.video.subtitles import SubtitleGenerator, add_subtitles_to_video


def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)

    generator = SubtitleGenerator()

    # Add TikTok-style subtitles
    output = generator.add_subtitles(
        video_path="input.mp4",
        output_path="output_tiktok.mp4",
        style="tiktok",
        highlight_keywords=True
    )

    print(f"✅ Subtitles added: {output}")


def example_all_styles():
    """Generate videos with all available styles"""
    print("\n" + "=" * 60)
    print("Example 2: All Subtitle Styles")
    print("=" * 60)

    generator = SubtitleGenerator()

    styles = ["tiktok", "instagram", "mr_beast", "minimal", "professional"]

    for style in styles:
        print(f"\nGenerating {style} style...")

        output = generator.add_subtitles(
            video_path="input.mp4",
            output_path=f"output_{style}.mp4",
            style=style,
            highlight_keywords=True
        )

        print(f"✅ {style}: {output}")


def example_export_transcript():
    """Export transcript in multiple formats"""
    print("\n" + "=" * 60)
    print("Example 3: Export Transcripts")
    print("=" * 60)

    generator = SubtitleGenerator()

    formats = ["srt", "vtt", "json", "txt"]

    for format in formats:
        print(f"\nExporting as {format}...")

        output = generator.export_transcript(
            video_path="input.mp4",
            output_path=f"transcript.{format}",
            format=format
        )

        print(f"✅ {format}: {output}")


def example_custom_settings():
    """Custom subtitle settings"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Settings")
    print("=" * 60)

    generator = SubtitleGenerator()

    output = generator.add_subtitles(
        video_path="input.mp4",
        output_path="output_custom.mp4",
        style="instagram",
        highlight_keywords=False,  # No keyword highlighting
        max_words_per_line=3,  # Shorter lines
        language="en"  # Explicit language
    )

    print(f"✅ Custom subtitles: {output}")


def example_convenience_function():
    """Using the convenience function"""
    print("\n" + "=" * 60)
    print("Example 5: Convenience Function")
    print("=" * 60)

    # Simplest way to add subtitles
    output = add_subtitles_to_video(
        video_path="input.mp4",
        output_path="output_quick.mp4",
        style="tiktok"
    )

    print(f"✅ Quick subtitles: {output}")


def example_batch_processing():
    """Batch process multiple videos"""
    print("\n" + "=" * 60)
    print("Example 6: Batch Processing")
    print("=" * 60)

    generator = SubtitleGenerator()

    videos = [
        "video1.mp4",
        "video2.mp4",
        "video3.mp4"
    ]

    for i, video_path in enumerate(videos, 1):
        print(f"\nProcessing video {i}/{len(videos)}: {video_path}")

        try:
            output = generator.add_subtitles(
                video_path=video_path,
                output_path=video_path.replace(".mp4", "_subtitled.mp4"),
                style="tiktok"
            )
            print(f"✅ Done: {output}")
        except Exception as e:
            print(f"❌ Error: {e}")


def example_style_comparison():
    """Generate a comparison of all styles side-by-side"""
    print("\n" + "=" * 60)
    print("Example 7: Style Comparison")
    print("=" * 60)

    from features.video.subtitles import SubtitleStyleConfig

    print("\nAvailable Styles:")
    print("-" * 60)

    for style_name, config in SubtitleStyleConfig.STYLES.items():
        print(f"\n{style_name.upper()}:")
        print(f"  Font: {config['font']}")
        print(f"  Size: {config['fontsize']}px")
        print(f"  Color: {config['color']}")
        print(f"  Stroke: {config['stroke_color']} ({config['stroke_width']}px)")
        print(f"  Position: {config['position']}")


def main():
    """Run all examples"""
    print("🎬 Automated Subtitles Examples")
    print("=" * 60)

    # Run examples (comment out the ones you don't need)
    try:
        example_style_comparison()

        # Uncomment to run actual video processing:
        # example_basic_usage()
        # example_all_styles()
        # example_export_transcript()
        # example_custom_settings()
        # example_convenience_function()
        # example_batch_processing()

    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  uv add openai moviepy")

    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("\nMake sure you have an 'input.mp4' file or adjust the paths")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
