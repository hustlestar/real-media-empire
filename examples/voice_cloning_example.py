"""
Example: Voice Cloning and Management with ElevenLabs Voice Lab

This example demonstrates how to use the VoiceCloner to create
brand-consistent voices across all your video content.

Run from project root with:
    PYTHONPATH=src python examples/voice_cloning_example.py
"""

from features.audio.voice_cloning import VoiceCloner, VoiceSettings, clone_voice, generate_speech


def example_list_voices():
    """List all available voices"""
    print("=" * 60)
    print("Example 1: List Available Voices")
    print("=" * 60)

    cloner = VoiceCloner()
    voices = cloner.list_voices()

    print(f"\nFound {len(voices)} voices:\n")
    for voice in voices[:10]:  # Show first 10
        print(f"  • {voice.name:30} ({voice.voice_id})")
        print(f"    Category: {voice.category}, Samples: {len(voice.samples)}")
        if voice.description:
            print(f"    Description: {voice.description}")
        print()


def example_clone_voice():
    """Clone a voice from audio samples"""
    print("\n" + "=" * 60)
    print("Example 2: Clone a Voice")
    print("=" * 60)

    cloner = VoiceCloner()

    # Clone voice from audio samples
    # NOTE: Replace with your actual audio files!
    audio_files = [
        "path/to/sample1.mp3",
        "path/to/sample2.mp3",
        "path/to/sample3.mp3"
    ]

    try:
        voice = cloner.clone_voice(
            name="CEO Voice - Brand",
            audio_files=audio_files,
            description="Our CEO's voice for product announcements and company updates",
            labels={
                "use_case": "corporate",
                "department": "marketing",
                "approved_by": "legal"
            }
        )

        print(f"\n✅ Voice cloned successfully!")
        print(f"   Voice ID: {voice.voice_id}")
        print(f"   Name: {voice.name}")

    except FileNotFoundError:
        print("\n⚠️  Skipping - audio files not found")
        print("   Replace 'path/to/sample*.mp3' with your actual audio files")


def example_generate_speech_basic():
    """Generate speech with default settings"""
    print("\n" + "=" * 60)
    print("Example 3: Generate Speech (Basic)")
    print("=" * 60)

    cloner = VoiceCloner()

    # Get first available voice
    voices = cloner.list_voices()
    if not voices:
        print("❌ No voices available")
        return

    voice = voices[0]
    print(f"Using voice: {voice.name} ({voice.voice_id})")

    # Generate speech
    output = cloner.generate_speech(
        text="Welcome to our channel! Today we're going to show you something amazing.",
        voice_id=voice.voice_id,
        output_path="output_basic.mp3"
    )

    print(f"\n✅ Speech generated: {output}")


def example_generate_speech_with_presets():
    """Generate speech with different content type presets"""
    print("\n" + "=" * 60)
    print("Example 4: Generate Speech with Content Presets")
    print("=" * 60)

    cloner = VoiceCloner()
    voices = cloner.list_voices()
    if not voices:
        print("❌ No voices available")
        return

    voice = voices[0]
    print(f"Using voice: {voice.name}\n")

    text = "This product will change your life! Don't miss out on this amazing opportunity!"

    content_types = ["short", "reel", "ad", "tutorial", "storytelling", "energetic"]

    for content_type in content_types:
        print(f"\nGenerating {content_type} version...")

        output = cloner.generate_speech(
            text=text,
            voice_id=voice.voice_id,
            output_path=f"output_{content_type}.mp3",
            content_type=content_type
        )

        print(f"✅ {content_type}: {output}")


def example_custom_voice_settings():
    """Generate speech with custom voice settings"""
    print("\n" + "=" * 60)
    print("Example 5: Custom Voice Settings")
    print("=" * 60)

    cloner = VoiceCloner()
    voices = cloner.list_voices()
    if not voices:
        print("❌ No voices available")
        return

    voice = voices[0]

    # Create custom settings
    custom_settings = VoiceSettings(
        stability=0.3,          # More expressive
        similarity_boost=0.9,   # Very similar to original
        style=0.6,              # High style exaggeration
        use_speaker_boost=True
    )

    output = cloner.generate_speech(
        text="Check out this incredible new feature!",
        voice_id=voice.voice_id,
        output_path="output_custom.mp3",
        settings=custom_settings
    )

    print(f"\n✅ Custom speech generated: {output}")
    print(f"   Settings: stability={custom_settings.stability}, "
          f"similarity={custom_settings.similarity_boost}, "
          f"style={custom_settings.style}")


def example_batch_generation():
    """Generate speech for multiple scripts"""
    print("\n" + "=" * 60)
    print("Example 6: Batch Speech Generation")
    print("=" * 60)

    cloner = VoiceCloner()
    voices = cloner.list_voices()
    if not voices:
        print("❌ No voices available")
        return

    voice = voices[0]
    print(f"Using voice: {voice.name}\n")

    scripts = [
        "Welcome to episode 1!",
        "Welcome to episode 2!",
        "Welcome to episode 3!",
        "Thanks for watching!",
    ]

    for i, script in enumerate(scripts, 1):
        print(f"Generating script {i}/{len(scripts)}...")

        try:
            output = cloner.generate_speech(
                text=script,
                voice_id=voice.voice_id,
                output_path=f"batch_output_{i}.mp3",
                content_type="short"
            )
            print(f"✅ Done: {output}")

        except Exception as e:
            print(f"❌ Error: {e}")


def example_voice_management():
    """Manage voices (get details, update settings, delete)"""
    print("\n" + "=" * 60)
    print("Example 7: Voice Management")
    print("=" * 60)

    cloner = VoiceCloner()

    # Find a voice by name
    print("\nSearching for voice by name...")
    voice = cloner.find_voice_by_name("adam")  # Common premade voice
    if voice:
        print(f"✅ Found: {voice.name} ({voice.voice_id})")

        # Get full details
        print("\nGetting full voice details...")
        detailed_voice = cloner.get_voice(voice.voice_id)
        print(f"  Category: {detailed_voice.category}")
        print(f"  Samples: {len(detailed_voice.samples)}")
        if detailed_voice.settings:
            print(f"  Settings: stability={detailed_voice.settings.stability}, "
                  f"similarity={detailed_voice.settings.similarity_boost}")
    else:
        print("⚠️  Voice not found")


def example_usage_stats():
    """Check API usage statistics"""
    print("\n" + "=" * 60)
    print("Example 8: API Usage Statistics")
    print("=" * 60)

    cloner = VoiceCloner()

    stats = cloner.get_usage_stats()

    print(f"\nAPI Usage:")
    print(f"  Tier: {stats['tier']}")
    print(f"  Characters used: {stats['character_count']:,}")
    print(f"  Character limit: {stats['character_limit']:,}")
    print(f"  Remaining: {stats['remaining_characters']:,}")
    print(f"  Usage: {(stats['character_count'] / max(stats['character_limit'], 1) * 100):.1f}%")
    print(f"\nFeatures:")
    print(f"  Instant voice cloning: {'✅' if stats['can_use_instant_voice_cloning'] else '❌'}")
    print(f"  Professional voice cloning: {'✅' if stats['can_use_professional_voice_cloning'] else '❌'}")


def example_convenience_functions():
    """Using convenience functions"""
    print("\n" + "=" * 60)
    print("Example 9: Convenience Functions")
    print("=" * 60)

    # Get a voice ID first
    cloner = VoiceCloner()
    voices = cloner.list_voices()
    if not voices:
        print("❌ No voices available")
        return

    voice_id = voices[0].voice_id

    # Simple speech generation
    print(f"\nGenerating speech with convenience function...")
    output = generate_speech(
        text="This is the easiest way to generate speech!",
        voice_id=voice_id,
        output_path="convenience_output.mp3",
        content_type="short"
    )

    print(f"✅ Done: {output}")


def example_multi_model_comparison():
    """Compare different models"""
    print("\n" + "=" * 60)
    print("Example 10: Model Comparison")
    print("=" * 60)

    cloner = VoiceCloner()
    voices = cloner.list_voices()
    if not voices:
        print("❌ No voices available")
        return

    voice = voices[0]
    text = "This is a test of different models."

    models = [
        "eleven_multilingual_v2",  # Best quality
        "eleven_monolingual_v1",   # English only
        "eleven_turbo_v2"          # Fastest
    ]

    for model in models:
        print(f"\nGenerating with {model}...")
        try:
            output = cloner.generate_speech(
                text=text,
                voice_id=voice.voice_id,
                output_path=f"model_{model}.mp3",
                model=model
            )
            print(f"✅ {model}: {output}")
        except Exception as e:
            print(f"❌ Error with {model}: {e}")


def example_content_preset_comparison():
    """Show all content presets and their settings"""
    print("\n" + "=" * 60)
    print("Example 11: Content Type Presets")
    print("=" * 60)

    from features.audio.voice_cloning import VoiceCloner

    print("\nAvailable Content Presets:\n")

    presets = {
        "short": "Optimized for TikTok/Reels - expressive, high energy",
        "reel": "Similar to short - Instagram Reels",
        "ad": "Professional, clear, confident - advertisements",
        "tutorial": "Clear, stable - easy to understand",
        "storytelling": "Expressive with emotion - narratives",
        "energetic": "High energy, enthusiastic - grabs attention"
    }

    for preset_name, description in presets.items():
        settings = VoiceCloner.CONTENT_PRESETS[preset_name]
        print(f"{preset_name.upper()}:")
        print(f"  Description: {description}")
        print(f"  Stability: {settings.stability}")
        print(f"  Similarity Boost: {settings.similarity_boost}")
        print(f"  Style: {settings.style}")
        print(f"  Speaker Boost: {settings.use_speaker_boost}")
        print()


def main():
    """Run all examples"""
    print("🎙️  Voice Cloning Examples - ElevenLabs Voice Lab")
    print("=" * 60)

    # Run examples (comment out the ones you don't need)
    try:
        example_usage_stats()
        example_list_voices()
        example_content_preset_comparison()

        # Uncomment to run actual voice operations:
        # example_clone_voice()
        # example_generate_speech_basic()
        # example_generate_speech_with_presets()
        # example_custom_voice_settings()
        # example_batch_generation()
        # example_voice_management()
        # example_convenience_functions()
        # example_multi_model_comparison()

    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  uv add requests")

    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nMake sure you have:")
        print("  1. ElevenLabs API key in .env file: ELEVEN_LABS_API_KEY=your-key")
        print("  2. Or set environment variable: export ELEVEN_LABS_API_KEY=your-key")
        print("\nGet your API key at: https://elevenlabs.io/")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
