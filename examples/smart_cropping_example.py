"""
Example: Smart Cropping with Subject Tracking

Intelligent video cropping that keeps main subjects in frame.
Uses face detection + YOLO object detection + subject tracking.

Key Benefits:
- No manual selection needed
- Tracks subjects across frames
- Smooth camera motion
- Works with any aspect ratio

Run from project root with:
    PYTHONPATH=src python examples/smart_cropping_example.py
"""

from features.video.smart_cropping import SmartCropper, smart_crop_video


def example_basic_smart_crop():
    """Basic smart cropping to TikTok format"""
    print("=" * 60)
    print("Example 1: Basic Smart Crop (TikTok 9:16)")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    try:
        # Crop to TikTok format with subject tracking
        output = smart_crop_video(
            video_path=video_path,
            output_path="output_tiktok.mp4",
            target_size=(1080, 1920),  # TikTok: 9:16
            detection_mode="balanced"
        )

        print(f"\n✅ Smart crop complete: {output}")
        print("   • Detected and tracked main subjects")
        print("   • Kept subjects in frame throughout video")
        print("   • Smooth camera motion")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("   Replace 'path/to/your/video.mp4' with your actual video")


def example_detection_modes():
    """Compare different detection modes"""
    print("\n" + "=" * 60)
    print("Example 2: Detection Modes Comparison")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    modes = {
        "fast": "Every 10 frames - fastest but less smooth",
        "balanced": "Every 5 frames - good speed/quality trade-off",
        "accurate": "Every frame - slowest but smoothest"
    }

    print("\nAvailable detection modes:\n")

    for mode, description in modes.items():
        print(f"{mode.upper()}:")
        print(f"  {description}")

        try:
            cropper = SmartCropper(detection_mode=mode)
            output = f"output_{mode}.mp4"

            cropper.apply_smart_crop(
                video_path=video_path,
                output_path=output,
                target_size=(1080, 1920),
                track=True
            )

            print(f"  ✅ Output: {output}\n")

        except FileNotFoundError:
            print(f"  ⚠️  Skipping (video not found)\n")


def example_subject_tracking():
    """Track subject through video"""
    print("\n" + "=" * 60)
    print("Example 3: Subject Tracking Analysis")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    try:
        cropper = SmartCropper(detection_mode="balanced")

        print(f"\nTracking subjects in: {video_path}")

        # Get tracking data
        crop_centers = cropper.track_subject(
            video_path=video_path,
            target_aspect_ratio=(9, 16)
        )

        print(f"\n📊 Tracking Results:")
        print(f"   Total frames: {len(crop_centers)}")

        # Analyze movement
        if len(crop_centers) > 1:
            movements = []
            for i in range(len(crop_centers) - 1):
                dx = crop_centers[i+1][0] - crop_centers[i][0]
                dy = crop_centers[i+1][1] - crop_centers[i][1]
                dist = (dx**2 + dy**2) ** 0.5
                movements.append(dist)

            avg_movement = sum(movements) / len(movements)
            max_movement = max(movements)

            print(f"   Average movement: {avg_movement:.4f}")
            print(f"   Max movement: {max_movement:.4f}")

            if avg_movement < 0.02:
                print(f"   Subject activity: Stable (mostly stationary)")
            elif avg_movement < 0.05:
                print(f"   Subject activity: Moderate (normal movement)")
            else:
                print(f"   Subject activity: High (very dynamic)")

        # Sample positions
        print(f"\n📍 Sample crop centers:")
        sample_indices = [0, len(crop_centers)//4, len(crop_centers)//2,
                         3*len(crop_centers)//4, len(crop_centers)-1]

        for idx in sample_indices:
            if idx < len(crop_centers):
                x, y = crop_centers[idx]
                print(f"   Frame {idx:4d}: ({x:.2f}, {y:.2f})")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")


def example_multi_platform():
    """Crop for multiple platforms"""
    print("\n" + "=" * 60)
    print("Example 4: Multi-Platform Smart Crop")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    platforms = {
        "tiktok": (1080, 1920),       # 9:16
        "youtube": (1920, 1080),       # 16:9
        "instagram": (1080, 1080),     # 1:1
        "instagram_feed": (1080, 1350) # 4:5
    }

    print("\nCropping for multiple platforms:\n")

    try:
        cropper = SmartCropper(detection_mode="balanced")

        for platform, size in platforms.items():
            output = f"output_{platform}.mp4"

            print(f"{platform.capitalize():15} ({size[0]}x{size[1]})", end=" ... ")

            cropper.apply_smart_crop(
                video_path=video_path,
                output_path=output,
                target_size=size,
                track=True
            )

            print(f"✅ {output}")

        print(f"\n💡 One video → {len(platforms)} platform-optimized versions!")

    except FileNotFoundError:
        print("\n⚠️  Video file not found - showing what would be created:\n")

        for platform, size in platforms.items():
            aspect = f"{size[0]}:{size[1]}"
            print(f"  {platform:15} - {size[0]}x{size[1]} ({aspect})")


def example_with_without_tracking():
    """Compare with and without subject tracking"""
    print("\n" + "=" * 60)
    print("Example 5: Tracking vs Static Crop")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    try:
        cropper = SmartCropper()

        # With tracking
        print("\n1. WITH subject tracking:")
        print("   • Analyzes all frames")
        print("   • Tracks subject movement")
        print("   • Smooth camera motion")

        cropper.apply_smart_crop(
            video_path=video_path,
            output_path="output_with_tracking.mp4",
            target_size=(1080, 1920),
            track=True  # Enable tracking
        )

        print("   ✅ output_with_tracking.mp4")

        # Without tracking (static)
        print("\n2. WITHOUT subject tracking:")
        print("   • Single detection at middle frame")
        print("   • Static crop position")
        print("   • Faster processing")

        cropper.apply_smart_crop(
            video_path=video_path,
            output_path="output_static.mp4",
            target_size=(1080, 1920),
            track=False  # Disable tracking
        )

        print("   ✅ output_static.mp4")

        print("\n💡 Compare the two videos to see the difference!")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("\nDifferences:")
        print("  WITH tracking: Follows subject, smooth motion")
        print("  WITHOUT tracking: Static crop, faster processing")


def example_detection_priority():
    """Show detection priority system"""
    print("\n" + "=" * 60)
    print("Example 6: Detection Priority System")
    print("=" * 60)

    print("\n🎯 Subject Detection Priority (Highest to Lowest):\n")

    priorities = [
        (1, "Faces", "OpenCV Haar Cascade detection"),
        (2, "People/Persons", "YOLO detection (if available)"),
        (3, "Animals", "Dogs, cats, horses (YOLO)"),
        (4, "Important Objects", "Phones, laptops (YOLO)"),
        (5, "Other Objects", "Mouse, keyboard, remote (YOLO)"),
        (6, "Salient Regions", "Fallback: edge detection")
    ]

    for priority, subject, method in priorities:
        print(f"  Priority {priority}: {subject}")
        print(f"               {method}")
        print()

    print("💡 The system always picks the highest priority subject detected!")
    print("   Faces > People > Animals > Objects > Salient Regions")


def example_smoothing_factor():
    """Show smoothing effect"""
    print("\n" + "=" * 60)
    print("Example 7: Smoothing Factor")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    smoothing_levels = {
        0.3: "Low smoothing - more responsive, may be jerky",
        0.7: "Default smoothing - balanced",
        0.9: "High smoothing - very smooth, less responsive"
    }

    print("\nSmoothing factor controls camera motion smoothness:\n")

    try:
        cropper = SmartCropper()

        for smoothing, description in smoothing_levels.items():
            print(f"Smoothing {smoothing}: {description}")

            # Get tracking with different smoothing
            centers = cropper.track_subject(
                video_path=video_path,
                target_aspect_ratio=(9, 16),
                smoothing=smoothing
            )

            print(f"  ✅ Tracked {len(centers)} frames\n")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("\nSmoothing effect:")
        print("  • Low (0.3): Follows subject closely, may be jerky")
        print("  • Medium (0.7): Good balance (recommended)")
        print("  • High (0.9): Very smooth, slower to respond")


def example_yolo_availability():
    """Check YOLO availability"""
    print("\n" + "=" * 60)
    print("Example 8: Check Detection Capabilities")
    print("=" * 60)

    cropper = SmartCropper()

    print(f"\n🔍 Detection Capabilities:\n")
    print(f"  OpenCV Face Detection: ✅ Always available")
    print(f"  YOLO Object Detection: {'✅ Available' if cropper.yolo_available else '❌ Not available'}")

    if not cropper.yolo_available:
        print(f"\n💡 To enable YOLO detection:")
        print(f"  1. Download YOLOv3 weights from: https://pjreddie.com/darknet/yolo/")
        print(f"  2. Place yolov3.weights and yolov3.cfg in project root")
        print(f"  3. Restart the application")
        print(f"\n  With YOLO: Detects 80+ object classes")
        print(f"  Without YOLO: Face detection + saliency detection")


def example_convenience_function():
    """Using convenience function"""
    print("\n" + "=" * 60)
    print("Example 9: Convenience Function")
    print("=" * 60)

    video_path = "path/to/your/video.mp4"

    try:
        # Simple one-liner
        output = smart_crop_video(
            video_path=video_path,
            output_path="quick_crop.mp4",
            target_size=(1080, 1920),
            detection_mode="balanced"
        )

        print(f"\n✅ Quick crop: {output}")
        print("   Using convenience function - simplest way!")

    except FileNotFoundError:
        print("\n⚠️  Video file not found")
        print("\nConvenience function:")
        print("  from features.video.smart_cropping import smart_crop_video")
        print("  output = smart_crop_video(video, output, size, mode)")
        print("  # That's it! 🎉")


def example_best_practices():
    """Best practices for smart cropping"""
    print("\n" + "=" * 60)
    print("Example 10: Best Practices")
    print("=" * 60)

    print("\n📚 Smart Cropping Best Practices:\n")

    print("1. DETECTION MODE:")
    print("   ✅ Use 'balanced' for most cases")
    print("   ✅ Use 'fast' for quick previews")
    print("   ✅ Use 'accurate' for final production")
    print()

    print("2. SUBJECT TRACKING:")
    print("   ✅ Enable for videos with moving subjects")
    print("   ✅ Disable for static shots (faster)")
    print("   ✅ Adjust smoothing based on content")
    print()

    print("3. ASPECT RATIOS:")
    print("   ✅ Match target platform requirements")
    print("   ✅ Test multiple ratios from one source")
    print("   ✅ Vertical (9:16) for shorts/reels")
    print("   ✅ Square (1:1) for Instagram feed")
    print()

    print("4. PERFORMANCE:")
    print("   ✅ Process longest videos with 'fast' mode first")
    print("   ✅ Use 'accurate' for short clips (<1 min)")
    print("   ✅ Batch process multiple videos overnight")
    print()


def main():
    """Run all examples"""
    print("🎯 Smart Cropping Examples")
    print("=" * 60)
    print("\nIntelligent video cropping with subject tracking!")
    print("Keeps main subjects in frame when changing aspect ratios.\n")

    # Run examples
    try:
        # Info examples (work without files)
        example_detection_priority()
        example_yolo_availability()
        example_best_practices()

        # Examples that need video files (uncomment when you have videos)
        # example_basic_smart_crop()
        # example_detection_modes()
        # example_subject_tracking()
        # example_multi_platform()
        # example_with_without_tracking()
        # example_smoothing_factor()
        # example_convenience_function()

        print("\n" + "=" * 60)
        print("📚 Key Takeaways:")
        print("=" * 60)
        print("\n1. Smart cropping keeps subjects in frame")
        print("2. Detects faces, people, animals, objects")
        print("3. Subject tracking for smooth motion")
        print("4. Works with any aspect ratio")
        print("5. One video → Multiple platform versions")
        print("\n💡 No more manual cropping or cut-off subjects!")

    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  uv add moviepy opencv-python")
        print("\nOptional (for YOLO):")
        print("  Download YOLOv3 weights from: https://pjreddie.com/darknet/yolo/")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
