"""
Example: Platform Video Formatter

This example demonstrates how to automatically format videos for different
social media platforms with correct aspect ratios and specifications.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from features.video.formatter import (
    PlatformVideoFormatter,
    PlatformSpecs,
    format_video_for_platforms
)


def example_format_all_platforms():
    """Format video for all major platforms"""
    print("=" * 60)
    print("Example 1: Format for All Major Platforms")
    print("=" * 60)

    formatter = PlatformVideoFormatter()

    platforms = ["tiktok", "instagram_reels", "youtube", "linkedin"]

    versions = formatter.create_all_versions(
        source_video="input.mp4",
        platforms=platforms,
        smart_crop=True  # Detect and follow faces/subjects
    )

    print(f"\n✅ Created {len(versions)} platform versions:")
    for platform, path in versions.items():
        if path:
            print(f"  • {platform}: {path}")


def example_single_platform():
    """Format for a single platform"""
    print("\n" + "=" * 60)
    print("Example 2: Format for Single Platform (TikTok)")
    print("=" * 60)

    formatter = PlatformVideoFormatter()

    output = formatter.format_for_platform(
        source_video="input.mp4",
        platform="tiktok",
        output_path="output_tiktok.mp4",
        smart_crop=True
    )

    print(f"\n✅ TikTok version created: {output}")


def example_with_padding():
    """Format with padding instead of cropping"""
    print("\n" + "=" * 60)
    print("Example 3: Format with Padding (No Cropping)")
    print("=" * 60)

    formatter = PlatformVideoFormatter()

    versions = formatter.create_all_versions(
        source_video="input.mp4",
        platforms=["tiktok", "youtube"],
        smart_crop=False,
        add_padding=True,
        padding_color="blur"  # Options: black, white, blur
    )

    print(f"\n✅ Created versions with padding:")
    for platform, path in versions.items():
        print(f"  • {platform}: {path}")


def example_validate_video():
    """Validate video against platform requirements"""
    print("\n" + "=" * 60)
    print("Example 4: Validate Video for Platforms")
    print("=" * 60)

    formatter = PlatformVideoFormatter()

    platforms = ["tiktok", "youtube", "instagram_reels"]

    for platform in platforms:
        print(f"\n{platform.upper()}:")

        validation = formatter.validate_video("input.mp4", platform)

        if validation["valid"]:
            print("  ✅ Valid for platform")
        else:
            print("  ❌ Invalid for platform")
            for error in validation["errors"]:
                print(f"     • {error}")

        if validation["warnings"]:
            print("  ⚠️  Warnings:")
            for warning in validation["warnings"]:
                print(f"     • {warning}")

        print(f"  Specs: {validation['specs']}")


def example_list_platforms():
    """List all supported platforms"""
    print("\n" + "=" * 60)
    print("Example 5: List All Supported Platforms")
    print("=" * 60)

    platforms = PlatformSpecs.list_platforms()

    print(f"\n{len(platforms)} Supported Platforms:\n")

    for platform in platforms:
        spec = PlatformSpecs.get_spec(platform)
        print(f"  {spec.name:20} {spec.resolution[0]}x{spec.resolution[1]:5} "
              f"({spec.aspect_ratio[0]}:{spec.aspect_ratio[1]}) "
              f"max {spec.max_duration}s")


def example_convenience_function():
    """Using the convenience function"""
    print("\n" + "=" * 60)
    print("Example 6: Convenience Function")
    print("=" * 60)

    # Simplest way to format for multiple platforms
    versions = format_video_for_platforms(
        source_video="input.mp4",
        platforms=["tiktok", "youtube", "linkedin"],
        smart_crop=True
    )

    print(f"\n✅ Created {len(versions)} versions:")
    for platform, path in versions.items():
        print(f"  • {platform}: {path}")


def example_batch_processing():
    """Batch process multiple videos"""
    print("\n" + "=" * 60)
    print("Example 7: Batch Processing Multiple Videos")
    print("=" * 60)

    formatter = PlatformVideoFormatter()

    videos = [
        "video1.mp4",
        "video2.mp4",
        "video3.mp4"
    ]

    platforms = ["tiktok", "youtube"]

    for i, video in enumerate(videos, 1):
        print(f"\nProcessing video {i}/{len(videos)}: {video}")

        try:
            versions = formatter.create_all_versions(
                source_video=video,
                platforms=platforms,
                smart_crop=True
            )

            print(f"✅ Created {len(versions)} versions")

        except Exception as e:
            print(f"❌ Error: {e}")


def example_smart_crop_comparison():
    """Compare smart crop vs simple resize"""
    print("\n" + "=" * 60)
    print("Example 8: Smart Crop vs Simple Resize")
    print("=" * 60)

    formatter = PlatformVideoFormatter()

    print("\nCreating TikTok version WITH smart crop (detects faces)...")
    smart_version = formatter.format_for_platform(
        source_video="input.mp4",
        platform="tiktok",
        output_path="output_smart.mp4",
        smart_crop=True
    )
    print(f"✅ Smart crop: {smart_version}")

    print("\nCreating TikTok version WITHOUT smart crop (center crop)...")
    simple_version = formatter.format_for_platform(
        source_video="input.mp4",
        platform="tiktok",
        output_path="output_simple.mp4",
        smart_crop=False
    )
    print(f"✅ Simple resize: {simple_version}")

    print("\n💡 Compare the two videos to see the difference!")


def main():
    """Run all examples"""
    print("🎬 Platform Video Formatter Examples")
    print("=" * 60)

    # Run examples (comment out the ones you don't need)
    try:
        example_list_platforms()

        # Uncomment to run actual video processing:
        # example_format_all_platforms()
        # example_single_platform()
        # example_with_padding()
        # example_validate_video()
        # example_convenience_function()
        # example_batch_processing()
        # example_smart_crop_comparison()

    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  uv add moviepy opencv-python")

    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("\nMake sure you have an 'input.mp4' file or adjust the paths")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
