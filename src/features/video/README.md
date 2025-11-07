# Video Features

Automated video processing features for social media content creation.

## Automated Subtitles

Add viral-style captions to videos automatically using OpenAI Whisper.

### Features

- ✅ Automatic transcription with word-level timing
- ✅ 5 viral caption styles (TikTok, Instagram, Mr Beast, Minimal, Professional)
- ✅ Keyword highlighting
- ✅ Export transcripts (SRT, VTT, JSON, TXT)
- ✅ Customizable styling
- ✅ Batch processing support

### Quick Start

```python
from features.video.subtitles import SubtitleGenerator

generator = SubtitleGenerator()

output = generator.add_subtitles(
    video_path="input.mp4",
    output_path="output.mp4",
    style="tiktok",
    highlight_keywords=True
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

**Add Subtitles:**
```bash
curl -X POST "http://localhost:8000/api/subtitles/add" \
  -F "video=@input.mp4" \
  -F "style=tiktok" \
  -F "highlight_keywords=true"
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

- Transcription: ~$0.006 per minute of audio (Whisper API)
- 60-second video: ~$0.006
- 10-minute video: ~$0.06

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
