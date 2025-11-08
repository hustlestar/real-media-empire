# Audio Features - Voice Cloning & Management

Professional voice cloning and brand voice consistency using ElevenLabs Voice Lab.

## 🎙️ Features

### Voice Cloning
- **Clone voices from audio samples** - Upload 1-3 samples of clean speech
- **Voice Design** - Create synthetic voices without samples (Pro/Enterprise)
- **Brand voice library** - Manage multiple voices for different content types
- **Voice settings optimization** - Fine-tune stability, similarity, style

### Content-Optimized Presets
Pre-configured voice settings for different content types:
- **Shorts/Reels** - Expressive, high energy, engaging
- **Ads** - Professional, clear, confident
- **Tutorials** - Stable, clear, easy to understand
- **Storytelling** - Expressive with emotion
- **Energetic** - High energy, enthusiastic

### Voice Management
- List all available voices (premade + cloned)
- Get detailed voice information
- Update voice settings
- Delete custom voices
- Track API usage and quota

## 🚀 Quick Start

### Clone a Voice

```python
from features.audio.voice_cloning import VoiceCloner

cloner = VoiceCloner()

# Clone from audio samples
voice = cloner.clone_voice(
    name="CEO Voice",
    audio_files=["sample1.mp3", "sample2.mp3", "sample3.mp3"],
    description="Our CEO's voice for announcements"
)

print(f"Voice ID: {voice.voice_id}")
```

### Generate Speech

```python
# Generate speech with content preset
cloner.generate_speech(
    text="Welcome to our channel!",
    voice_id=voice.voice_id,
    output_path="welcome.mp3",
    content_type="short"  # Optimized for TikTok/Reels
)
```

### Using Convenience Functions

```python
from features.audio.voice_cloning import clone_voice, generate_speech

# Clone voice
voice = clone_voice(
    name="Brand Voice",
    audio_files=["sample.mp3"]
)

# Generate speech
generate_speech(
    text="Check this out!",
    voice_id=voice.voice_id,
    output_path="output.mp3",
    content_type="reel"
)
```

## 📋 Voice Cloning Requirements

For best results when cloning voices:

1. **Audio Quality**
   - Clean speech (no background noise/music)
   - Single speaker only
   - Clear pronunciation
   - Natural speaking pace

2. **Duration**
   - Each sample: 30 seconds to 5 minutes
   - Total recommended: 2-3 minutes across samples
   - More samples = better quality

3. **Format**
   - MP3 or WAV
   - 44.1kHz or 48kHz sample rate
   - Mono or stereo

4. **Content**
   - Varied sentences (different emotions/tones)
   - Natural conversation works best
   - Avoid monotone reading

## 🎛️ Voice Settings

Fine-tune voice synthesis with custom settings:

```python
from features.audio.voice_cloning import VoiceSettings

settings = VoiceSettings(
    stability=0.5,          # 0.0-1.0 (lower = expressive, higher = stable)
    similarity_boost=0.75,  # 0.0-1.0 (how much to match original)
    style=0.0,              # 0.0-1.0 (style exaggeration, v2 models only)
    use_speaker_boost=True  # Boost similarity to speaker
)

cloner.generate_speech(
    text="Custom settings test",
    voice_id=voice_id,
    output_path="custom.mp3",
    settings=settings
)
```

### Content Type Presets

| Content Type | Stability | Similarity | Style | Use Case |
|-------------|-----------|------------|-------|----------|
| **short** | 0.4 | 0.8 | 0.3 | TikTok, YouTube Shorts |
| **reel** | 0.3 | 0.85 | 0.4 | Instagram Reels |
| **ad** | 0.6 | 0.75 | 0.2 | Advertisements |
| **tutorial** | 0.7 | 0.7 | 0.0 | Educational content |
| **storytelling** | 0.5 | 0.8 | 0.5 | Narratives, stories |
| **energetic** | 0.2 | 0.9 | 0.6 | High-energy content |

## 🔧 API Endpoints

### Clone Voice
```bash
curl -X POST "http://localhost:8000/api/voice/clone" \
  -F "name=CEO Voice" \
  -F "description=Our CEO's voice" \
  -F "files=@sample1.mp3" \
  -F "files=@sample2.mp3"
```

### List Voices
```bash
curl "http://localhost:8000/api/voice/list"
```

### Generate Speech
```bash
curl -X POST "http://localhost:8000/api/voice/generate-speech" \
  -F "text=Hello world!" \
  -F "voice_id=abc123" \
  -F "content_type=short"
```

### Get Usage Stats
```bash
curl "http://localhost:8000/api/voice/usage"
```

## 💡 Use Cases

### 1. Brand Voice Consistency
Clone your founder/CEO voice for consistent brand messaging:
```python
# Clone founder voice
founder_voice = cloner.clone_voice(
    name="Founder - Sarah",
    audio_files=["interview1.mp3", "podcast_appearance.mp3"],
    labels={"role": "founder", "approved": "legal"}
)

# Use across all videos
for script in product_announcements:
    generate_speech(
        text=script,
        voice_id=founder_voice.voice_id,
        output_path=f"announcement_{i}.mp3",
        content_type="ad"
    )
```

### 2. Content Variety
Create character voices for storytelling:
```python
# Clone multiple characters
narrator = clone_voice(name="Narrator", audio_files=["narrator.mp3"])
character1 = clone_voice(name="Character 1", audio_files=["char1.mp3"])
character2 = clone_voice(name="Character 2", audio_files=["char2.mp3"])

# Generate dialogue
generate_speech("Once upon a time...", narrator.voice_id, "narration.mp3")
generate_speech("Hello friend!", character1.voice_id, "char1_line.mp3")
generate_speech("Hey there!", character2.voice_id, "char2_line.mp3")
```

### 3. Platform Optimization
Use different settings for different platforms:
```python
voice_id = "your-voice-id"

# TikTok - High energy
generate_speech(
    text="Check this out!",
    voice_id=voice_id,
    output_path="tiktok.mp3",
    content_type="short"
)

# LinkedIn - Professional
generate_speech(
    text="Industry insights for you",
    voice_id=voice_id,
    output_path="linkedin.mp3",
    content_type="tutorial"
)
```

### 4. Batch Content Generation
Generate voiceovers for 100+ videos:
```python
cloner = VoiceCloner()
voice_id = "brand-voice-id"

for i, script in enumerate(scripts):
    output_path = f"voiceover_{i:03d}.mp3"
    generate_speech(
        text=script,
        voice_id=voice_id,
        output_path=output_path,
        content_type="short"
    )
    print(f"Generated {i+1}/{len(scripts)}")
```

## 💰 Cost & Quota

### Pricing Tiers
- **Free**: 10,000 characters/month
- **Starter**: 30,000 characters/month ($5)
- **Creator**: 100,000 characters/month ($22)
- **Pro**: 500,000 characters/month ($99)
- **Enterprise**: Custom

### Cost Estimation
```python
# Check usage
stats = cloner.get_usage_stats()
print(f"Used: {stats['character_count']:,} / {stats['character_limit']:,}")
print(f"Remaining: {stats['remaining_characters']:,}")

# Estimate cost before generation
text = "Your script here..."
chars = len(text)
print(f"This will use {chars} characters")
```

### Voice Cloning Quota
- **Instant Voice Cloning**: Free on most tiers (check your plan)
- **Professional Voice Cloning**: Higher tiers only
- Each voice clone counts toward your voice library limit

## 🎯 Best Practices

### 1. Voice Cloning
```python
# ✅ GOOD - Multiple varied samples
voice = clone_voice(
    name="Brand Voice",
    audio_files=[
        "casual_conversation.mp3",    # Natural, conversational
        "presentation.mp3",            # Professional tone
        "energetic_pitch.mp3"          # High energy
    ]
)

# ❌ BAD - Single monotone sample
voice = clone_voice(
    name="Voice",
    audio_files=["robot_reading.mp3"]  # Monotone reading
)
```

### 2. Content Presets
```python
# ✅ GOOD - Use appropriate preset
generate_speech(
    text="Learn how to code in 60 seconds!",
    voice_id=voice_id,
    content_type="short"  # Perfect for shorts
)

# ❌ BAD - Wrong preset for content
generate_speech(
    text="Detailed tax law explanation...",
    voice_id=voice_id,
    content_type="energetic"  # Too hyper for complex topic
)
```

### 3. Voice Management
```python
# ✅ GOOD - Organized voice library
voices = {
    "brand_ceo": clone_voice(name="CEO - Product Announcements", ...),
    "brand_tutorial": clone_voice(name="Tutorial - How-to Videos", ...),
    "character_hero": clone_voice(name="Story - Hero Character", ...)
}

# ❌ BAD - Confusing names
voice1 = clone_voice(name="voice1", ...)
voice2 = clone_voice(name="test", ...)
```

## 📊 Impact

### Brand Consistency
- **100% voice consistency** across all content
- Professional quality without expensive talent
- Scale from 10 to 1000+ videos with same voice

### Cost Savings
- **No voice actors needed** - $500-2000/video saved
- **No studio time** - $200-500/session saved
- **Instant revisions** - No re-recording costs

### Production Speed
- **5 seconds** to generate voiceover (vs hours for recording)
- **Instant iterations** - No scheduling delays
- **24/7 availability** - Generate anytime

### Quality
- **Professional studio quality** from ElevenLabs
- **29 languages** supported (multilingual models)
- **Emotion and tone control** via settings

## 🔗 Integration with Other Features

### With Subtitle System
```python
from features.video.subtitles import SubtitleGenerator
from features.audio.voice_cloning import generate_speech

# Generate voiceover
audio_path = generate_speech(
    text=script,
    voice_id=voice_id,
    output_path="voiceover.mp3",
    content_type="short"
)

# Add matching subtitles (text-based, FREE!)
subtitle_gen = SubtitleGenerator()
final_video = subtitle_gen.add_subtitles_from_text(
    video_path="visual.mp4",
    text=script,  # Same script!
    output_path="final.mp4",
    style="tiktok"
)
```

### With Video Formatter
```python
from features.video.formatter import PlatformVideoFormatter

# Create voiceover
audio = generate_speech(text=script, voice_id=voice_id, ...)

# Format for platforms
formatter = PlatformVideoFormatter()
versions = formatter.create_all_versions(
    source_video="video_with_voiceover.mp4",
    platforms=["tiktok", "youtube", "linkedin"]
)
```

## 📚 Models

### Available Models

| Model | Quality | Speed | Languages | Use Case |
|-------|---------|-------|-----------|----------|
| **eleven_multilingual_v2** | ⭐⭐⭐⭐⭐ | Medium | 29 | Best quality, production |
| **eleven_monolingual_v1** | ⭐⭐⭐⭐ | Fast | English | English content |
| **eleven_turbo_v2** | ⭐⭐⭐ | Very Fast | Multiple | Quick iterations |

```python
# Use different models
cloner.generate_speech(
    text="Test",
    voice_id=voice_id,
    output_path="output.mp3",
    model="eleven_multilingual_v2"  # Best quality
)
```

## 🛠️ Installation

```bash
# Add dependencies
uv add requests

# Set API key
echo "ELEVEN_LABS_API_KEY=your-key-here" >> .env
```

Get your API key at: https://elevenlabs.io/

## 📖 Examples

See `examples/voice_cloning_example.py` for complete examples:
```bash
PYTHONPATH=src python examples/voice_cloning_example.py
```

## 🔒 Security & Compliance

### Voice Ownership
- Only clone voices you have permission to use
- Get written consent for voice cloning
- Label voices clearly (personal, brand, licensed)

### Data Privacy
- Audio samples stored on ElevenLabs servers
- Review ElevenLabs privacy policy
- Consider data residency requirements

### Usage Guidelines
```python
# ✅ GOOD - Clear ownership and consent
voice = clone_voice(
    name="CEO Voice - Approved by Legal",
    audio_files=["ceo_consent_recording.mp3"],
    labels={
        "consent_date": "2025-01-15",
        "approved_by": "legal@company.com",
        "purpose": "marketing_only"
    }
)

# ❌ BAD - Unclear ownership
voice = clone_voice(
    name="Random Person",
    audio_files=["downloaded_audio.mp3"]
)
```

## 🎬 Next Steps

1. **Get API key** from https://elevenlabs.io/
2. **Clone your first voice** from audio samples
3. **Generate test voiceovers** with different presets
4. **Integrate with video pipeline** for automated production
5. **Scale to 100+ videos** with consistent brand voice

---

**Pro Tip**: Start with the FREE tier to test voice cloning, then upgrade based on your character usage. Most shorts use 50-200 characters of speech, so even the free tier supports 50+ videos/month!
