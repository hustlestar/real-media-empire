# Video Features

Automated video processing features for social media content creation.

---

## 🎣 Hook Optimizer (NEW!)

Analyze and optimize the first 3 seconds of your videos for maximum retention. **65% of viewers decide in the first 2 seconds** - make them count!

### Features

- ✅ Visual hook analysis (motion, colors, faces)
- ✅ Text hook analysis (power words, curiosity gaps)
- ✅ Audio hook analysis (voice energy, sound presence)
- ✅ Platform-specific optimization (TikTok, YouTube, Instagram)
- ✅ Hook scoring (0-100 with letter grades)
- ✅ A/B testing support
- ✅ Actionable recommendations
- ✅ Pattern interrupt detection
- ✅ Hook variation generation

### Quick Start

```python
from features.video.hook_optimizer import analyze_hook

# Analyze your hook
score = analyze_hook(
    video_path="video.mp4",
    text="Did you know this iPhone trick?",
    platform="tiktok"
)

print(f"Hook Score: {score.overall_score}/100 ({score._get_grade()})")
print(f"Recommendations: {score.recommendations}")
```

### Hook Scoring

| Grade | Score | Retention | Action |
|-------|-------|-----------|--------|
| A+ | 90-100 | Excellent | Ship it! |
| A/B+ | 80-89 | Good | Minor tweaks |
| B/C+ | 70-79 | Decent | Room for improvement |
| C/D | 60-69 | Weak | Needs work |
| F | <60 | Poor | Reshoot recommended |

### Key Stats

- **65%** of viewers decide in first 2 seconds
- **80%** decision made by 3 seconds
- Strong hooks = **2-5x higher retention**
- Hook optimization can boost watch time by **200%+**

### A/B Testing

```python
from features.video.hook_optimizer import compare_hooks

# Test multiple variations
scores = compare_hooks(
    video_paths=["hook_a.mp4", "hook_b.mp4", "hook_c.mp4"],
    texts=["Did you know...", "Watch this...", "Secret trick..."],
    platform="tiktok"
)

print(f"Winner: {scores[0].variant_id} with {scores[0].overall_score:.1f}")
```

### Power Words

Hook optimizer detects power words in 7 categories:
- **Curiosity**: secret, hidden, trick, hack, reveal
- **Urgency**: now, today, immediately, breaking
- **Exclusivity**: exclusive, only, limited, rare
- **Authority**: proven, expert, professional
- **Emotional**: amazing, incredible, stunning
- **Negative**: mistake, wrong, avoid, stop
- **Question**: how, why, what, did you know

### Platform Optimization

Different platforms have different hook requirements:

| Platform | Duration | Style |
|----------|----------|-------|
| TikTok | 2-3 sec | Fast, question-based, energetic |
| YouTube Shorts | 3 sec | Clear value, curiosity gap |
| Instagram Reels | 2-2.5 sec | Visual hook, FOMO |
| YouTube | 5-8 sec | Tease outcome, promise value |

---

## 🎨 Thumbnail Generator (NEW!)

Create eye-catching thumbnails optimized for maximum click-through rate. **Thumbnails determine 90% of clicks** - make them count!

### Features

- ✅ Auto-generate thumbnails from video frames
- ✅ Smart frame selection (face detection + emotion + contrast)
- ✅ 6 viral styles (viral, professional, minimal, energetic, mystery, educational)
- ✅ Platform-specific sizing (YouTube, TikTok, Instagram, etc.)
- ✅ Text overlay with customizable styling
- ✅ Visual effects (contrast boost, saturation, sharpening, vignette)
- ✅ Thumbnail quality analysis and scoring
- ✅ A/B testing variation generation

### Quick Start

```python
from features.video.thumbnail_generator import create_thumbnail

# Create thumbnail with auto-selected best frame
thumbnail = create_thumbnail(
    video_path="video.mp4",
    output_path="thumb.jpg",
    text="SHOCKING!",
    style="viral",
    platform="youtube"
)
```

### Key Stats

| Metric | Impact |
|--------|--------|
| **Click decision** | 90% determined by thumbnail |
| **View multiplier** | Good thumbnail = 10x more views |
| **Face impact** | Faces in thumbnails = +38% CTR |
| **Emotion impact** | Surprised/shocked faces = +41% CTR |
| **A/B testing** | Can double your CTR |

### Thumbnail Styles

| Style | Description | Best For |
|-------|-------------|----------|
| **Viral** | Yellow text, high contrast, bold | TikTok, YouTube Shorts, trending content |
| **Professional** | Clean, subtle, business-appropriate | LinkedIn, corporate, business content |
| **Minimal** | Simple, elegant, less is more | Artistic, photography, design |
| **Energetic** | Bright red text, exciting | Gaming, sports, high-energy |
| **Mystery** | Blue tones, intriguing | Story-telling, mystery, drama |
| **Educational** | Blue/white, trustworthy | Tutorials, how-to, explanations |

### Platform Specifications

| Platform | Size | Aspect Ratio | Max Size |
|----------|------|--------------|----------|
| YouTube | 1280x720 | 16:9 | 2 MB |
| TikTok | 1080x1920 | 9:16 | 5 MB |
| Instagram | 1080x1080 | 1:1 | 8 MB |
| Facebook | 1200x630 | 1.91:1 | 8 MB |
| Twitter | 1200x675 | 16:9 | 5 MB |
| LinkedIn | 1200x627 | 1.91:1 | 5 MB |

### A/B Testing

```python
from features.video.thumbnail_generator import ThumbnailGenerator

gen = ThumbnailGenerator()

# Create multiple variations to test
thumbnails = gen.create_ab_test_variations(
    video_path="video.mp4",
    output_dir="test_thumbs/",
    text_variations=[
        "SHOCKING!",
        "You Won't Believe This",
        "This Changed Everything"
    ],
    style="viral",
    platform="youtube"
)

# Analyze each variation
for thumb in thumbnails:
    score = gen.analyze_thumbnail(thumb)
    print(f"Score: {score.overall_score}/100")
```

### Best Practices

**Text Guidelines:**
- ✅ Keep under 4 words
- ✅ Large, readable font
- ✅ High contrast (yellow on dark)
- ❌ Full sentences or paragraphs
- ❌ Too much text

**Face Guidelines:**
- ✅ Show expressive emotions (surprised, shocked, excited)
- ✅ Face fills 40-60% of thumbnail
- ✅ Close-up shots
- ❌ Tiny faces or distant shots
- ❌ Neutral expressions

**Composition:**
- ✅ Single clear focal point
- ✅ High contrast colors
- ✅ Simple, uncluttered
- ❌ Too busy or complex
- ❌ Low contrast

### API Usage

**Create Thumbnail:**
```bash
curl -X POST "http://localhost:8000/api/thumbnail/create" \
  -F "video=@myvideo.mp4" \
  -F "text=SHOCKING!" \
  -F "style=viral" \
  -F "platform=youtube"
```

**A/B Test Thumbnails:**
```bash
curl -X POST "http://localhost:8000/api/thumbnail/ab-test" \
  -F "video=@myvideo.mp4" \
  -F "text_variations=SHOCKING,UNBELIEVABLE,MUST SEE" \
  -F "style=viral" \
  -F "analyze=true"
```

**Analyze Thumbnail:**
```bash
curl -X POST "http://localhost:8000/api/thumbnail/analyze" \
  -F "thumbnail=@mythumb.jpg"
```

**Get Best Practices:**
```bash
curl "http://localhost:8000/api/thumbnail/best-practices?platform=youtube"
```

### Installation

```bash
uv add moviepy pillow opencv-python
```

### Impact

- **90% of clicks** determined by thumbnail
- **10x more views** with optimized thumbnails
- **+38% CTR** with faces in thumbnails
- **+41% CTR** with surprised/shocked expressions
- **2x CTR improvement** possible with A/B testing

---

## 📱 Platform Video Formatter

Automatically format videos for different social media platforms with correct aspect ratios and specifications.

### Features

- ✅ Support for 9 major platforms (TikTok, Instagram, YouTube, LinkedIn, etc.)
- ✅ Smart cropping with face/subject detection
- ✅ Automatic aspect ratio conversion
- ✅ Platform-specific optimization
- ✅ Batch processing for multiple platforms
- ✅ Validation against platform requirements
- ✅ Padding options (letterbox/pillarbox with blur)

### Supported Platforms

| Platform | Resolution | Aspect Ratio | Max Duration |
|----------|------------|--------------|--------------|
| TikTok | 1080x1920 | 9:16 | 10 min |
| Instagram Reels | 1080x1920 | 9:16 | 90 sec |
| Instagram Feed | 1080x1350 | 4:5 | 60 sec |
| Instagram Story | 1080x1920 | 9:16 | 60 sec |
| YouTube | 1920x1080 | 16:9 | 12 hours |
| YouTube Shorts | 1080x1920 | 9:16 | 60 sec |
| LinkedIn | 1200x1200 | 1:1 | 10 min |
| Facebook | 1920x1080 | 16:9 | 2 hours |
| Twitter | 1280x720 | 16:9 | 140 sec |

### Quick Start

```python
from features.video.formatter import format_video_for_platforms

# One video → All platform versions
versions = format_video_for_platforms(
    source_video="input.mp4",
    platforms=["tiktok", "youtube", "linkedin"],
    smart_crop=True  # Detects faces/subjects automatically
)

# Returns:
# {
#   'tiktok': 'input_tiktok.mp4',
#   'youtube': 'input_youtube.mp4',
#   'linkedin': 'input_linkedin.mp4'
# }
```

### API Usage

**Format for Multiple Platforms:**
```bash
curl -X POST "http://localhost:8000/api/format/platforms" \
  -F "video=@input.mp4" \
  -F "platforms=tiktok,youtube,linkedin" \
  -F "smart_crop=true"
```

**Validate Video:**
```bash
curl -X POST "http://localhost:8000/api/format/validate" \
  -F "video=@input.mp4" \
  -F "platforms=tiktok,instagram_reels,youtube"
```

**List Platforms:**
```bash
curl "http://localhost:8000/api/format/platforms"
```

### Installation

```bash
uv add moviepy opencv-python
```

### Impact

- ✅ Publish-ready videos for all platforms
- ✅ Algorithm-friendly aspect ratios
- ✅ No manual resizing needed
- ✅ Smart cropping keeps subjects in frame

---

## 🎬 Automated Subtitles

Add viral-style captions to videos automatically using OpenAI Whisper.

### Features

- ✅ Automatic transcription with word-level timing
- ✅ 5 viral caption styles (TikTok, Instagram, Mr Beast, Minimal, Professional)
- ✅ Keyword highlighting
- ✅ Export transcripts (SRT, VTT, JSON, TXT)
- ✅ Customizable styling
- ✅ Batch processing support

### Quick Start

**For AI-Generated Videos (FREE - Recommended):**

```python
from features.video.subtitles import add_subtitles_from_text

# You already have the script from your AI video generation!
output = add_subtitles_from_text(
    video_path="generated_video.mp4",
    text="Welcome to my channel! This is amazing content.",
    output_path="output.mp4",
    style="tiktok"
)
```

**For External Videos (Costs $0.006/min):**

```python
from features.video.subtitles import SubtitleGenerator

generator = SubtitleGenerator(api_key="your-openai-key")

output = generator.add_subtitles(
    video_path="external_video.mp4",
    output_path="output.mp4",
    style="tiktok"
)
```

### Installation

```bash
uv add openai moviepy
```

### Available Styles

1. **TikTok** - Bold white text with black stroke, centered
2. **Instagram** - Clean white text with semi-transparent background
3. **Mr Beast** - Large yellow text, center screen, maximum impact
4. **Minimal** - Small white text on dark background, bottom
5. **Professional** - Clean corporate style, bottom

### API Usage

**Add Subtitles from Text (FREE - Recommended):**
```bash
curl -X POST "http://localhost:8000/api/subtitles/add-from-text" \
  -F "video=@generated_video.mp4" \
  -F "text=Welcome to my channel! This is amazing content." \
  -F "style=tiktok"
```

**Add Subtitles with Whisper (Costs Money):**
```bash
curl -X POST "http://localhost:8000/api/subtitles/add" \
  -F "video=@external_video.mp4" \
  -F "style=tiktok"
```

**Export Transcript:**
```bash
curl -X POST "http://localhost:8000/api/subtitles/export-transcript" \
  -F "video=@input.mp4" \
  -F "format=srt"
```

**List Styles:**
```bash
curl "http://localhost:8000/api/subtitles/styles"
```

### Examples

See `examples/subtitles_example.py` for comprehensive examples including:
- Basic usage
- All subtitle styles
- Transcript export
- Custom settings
- Batch processing

### Configuration

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Cost Estimation

**Text-Based Method (Recommended):**
- Cost: **FREE** (no API calls!)
- 60-second video: $0.00
- 10-minute video: $0.00
- Performance: Same as Whisper method

**Whisper Transcription Method (Fallback):**
- Transcription: ~$0.006 per minute of audio
- 60-second video: ~$0.006
- 10-minute video: ~$0.06

💡 **Tip:** For AI-generated videos, always use the text-based method to save costs!

### Performance

- **Transcription**: ~1-2 minutes per 10 minutes of video
- **Subtitle rendering**: ~2-3 minutes per 10 minutes of video
- **Total**: ~3-5 minutes for 10-minute video

### Impact

Adding subtitles increases:
- **Engagement**: +40%
- **Watch time**: +60%
- **Accessibility**: 100%
- **Algorithm performance**: Significant boost on all platforms

### Why Subtitles Matter

- 80%+ of social media videos watched with sound OFF
- TikTok/Instagram algorithm heavily favors captioned videos
- Accessibility is now table stakes
- Higher completion rates = better algorithm performance

### Troubleshooting

**Missing dependencies:**
```bash
uv add openai moviepy
```

**Font not found:**
Install system fonts:
```bash
# Ubuntu/Debian
sudo apt-get install fonts-liberation

# macOS - fonts usually pre-installed
```

**Slow processing:**
- Use shorter videos for testing
- Consider cloud GPU for faster rendering
- Batch processing recommended for multiple videos

### Next Steps

See `IMPLEMENTATION_PLAN.md` for the complete Phase 1 roadmap.

Next features:
- Platform video formatter (9:16, 16:9, 1:1)
- Voice cloning integration
- Hook optimization
