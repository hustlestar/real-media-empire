# 🚀 Video Production Platform - Implementation Plan

**Timeline:** 6 weeks
**Resources:** 1-2 engineers
**Expected Value:** $400K+ in production efficiency

---

## 📋 Phase Overview

| Phase | Duration | Focus | Priority | Value |
|-------|----------|-------|----------|-------|
| Phase 1 | Week 1 | Production Essentials | CRITICAL | $50K |
| Phase 2 | Week 2 | Engagement & Virality | CRITICAL | $75K |
| Phase 3 | Week 3 | Content Workflow | HIGH | $60K |
| Phase 4 | Week 4 | Advanced Editing | HIGH | $80K |
| Phase 5 | Week 5 | Platform Optimization | MEDIUM | $70K |
| Phase 6 | Week 6 | Production Value | MEDIUM | $65K |

---

## 🎯 Phase 1: Production Essentials (Week 1)

**Goal:** Make videos broadcast-quality and platform-ready

### 1.1 Automated Subtitles/Captions System

**Priority:** 🔴 CRITICAL
**Effort:** 2-3 days
**Impact:** 40% engagement increase

**Implementation:**

```python
# File: src/features/video/subtitles.py

from openai import OpenAI
import moviepy.editor as mp
from typing import List, Literal

class SubtitleGenerator:
    """Generate and burn-in subtitles with viral styles"""

    def __init__(self, whisper_model: str = "whisper-1"):
        self.client = OpenAI()
        self.model = whisper_model

    def transcribe_video(self, video_path: str, language: str = "auto") -> List[dict]:
        """Transcribe video using Whisper"""
        audio = mp.VideoFileClip(video_path).audio
        audio_path = "temp_audio.mp3"
        audio.write_audiofile(audio_path)

        # Whisper transcription
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

        return transcript.words

    def add_subtitles(
        self,
        video_path: str,
        output_path: str,
        style: Literal["tiktok", "instagram", "mr_beast", "minimal"] = "tiktok",
        highlight_keywords: bool = True,
        max_words_per_line: int = 5
    ) -> str:
        """Add burned-in subtitles to video"""

        # Get transcript
        words = self.transcribe_video(video_path)

        # Group words into subtitle segments
        segments = self._group_words_into_segments(words, max_words_per_line)

        # Apply style
        subtitle_clips = []
        for segment in segments:
            clip = self._create_subtitle_clip(
                text=segment['text'],
                start=segment['start'],
                end=segment['end'],
                style=style,
                highlight=highlight_keywords
            )
            subtitle_clips.append(clip)

        # Composite video with subtitles
        video = mp.VideoFileClip(video_path)
        final = mp.CompositeVideoClip([video] + subtitle_clips)
        final.write_videofile(output_path)

        return output_path

    def _create_subtitle_clip(
        self,
        text: str,
        start: float,
        end: float,
        style: str,
        highlight: bool
    ) -> mp.TextClip:
        """Create styled subtitle clip"""

        styles = {
            "tiktok": {
                "fontsize": 70,
                "font": "Impact",
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 3,
                "method": "caption",
                "bg_color": None
            },
            "instagram": {
                "fontsize": 60,
                "font": "Montserrat-Bold",
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 2,
                "method": "caption",
                "bg_color": "rgba(0,0,0,0.5)"
            },
            "mr_beast": {
                "fontsize": 80,
                "font": "Impact",
                "color": "yellow",
                "stroke_color": "black",
                "stroke_width": 4,
                "method": "caption",
                "bg_color": None
            },
            "minimal": {
                "fontsize": 50,
                "font": "Helvetica",
                "color": "white",
                "stroke_color": None,
                "stroke_width": 0,
                "method": "caption",
                "bg_color": "rgba(0,0,0,0.7)"
            }
        }

        style_config = styles.get(style, styles["tiktok"])

        # Highlight keywords if enabled
        if highlight:
            text = self._highlight_keywords(text)

        txt_clip = mp.TextClip(
            text=text,
            **style_config
        ).set_position(('center', 'center')).set_duration(end - start).set_start(start)

        return txt_clip

    def _highlight_keywords(self, text: str) -> str:
        """Highlight important keywords in text"""
        keywords = ['amazing', 'incredible', 'crazy', 'shocking', 'must', 'never', 'always', 'secret']
        for keyword in keywords:
            text = text.replace(keyword, keyword.upper())
        return text

    def _group_words_into_segments(self, words: List[dict], max_words: int) -> List[dict]:
        """Group words into subtitle segments"""
        segments = []
        current_segment = []

        for word in words:
            current_segment.append(word)

            if len(current_segment) >= max_words:
                segments.append({
                    'text': ' '.join([w['word'] for w in current_segment]),
                    'start': current_segment[0]['start'],
                    'end': current_segment[-1]['end']
                })
                current_segment = []

        # Add remaining words
        if current_segment:
            segments.append({
                'text': ' '.join([w['word'] for w in current_segment]),
                'start': current_segment[0]['start'],
                'end': current_segment[-1]['end']
            })

        return segments


# API endpoint
# File: director-ui/src/api/routers/subtitles.py

from fastapi import APIRouter, UploadFile
from features.video.subtitles import SubtitleGenerator

router = APIRouter(prefix="/api/subtitles", tags=["subtitles"])

@router.post("/add")
async def add_subtitles(
    video: UploadFile,
    style: str = "tiktok",
    highlight_keywords: bool = True
):
    """Add subtitles to video"""

    generator = SubtitleGenerator()

    # Save uploaded video
    video_path = f"/tmp/{video.filename}"
    with open(video_path, "wb") as f:
        f.write(await video.read())

    # Generate subtitles
    output_path = video_path.replace(".mp4", "_subtitled.mp4")
    result_path = generator.add_subtitles(
        video_path=video_path,
        output_path=output_path,
        style=style,
        highlight_keywords=highlight_keywords
    )

    return {
        "success": True,
        "output_path": result_path
    }
```

**Dependencies:**
- `openai` - Whisper API
- `moviepy` - Video processing (already installed)
- `Pillow` - Image processing

**Testing:**
```bash
uv run python -m pytest tests/test_subtitles.py
```

---

### 1.2 Platform Video Formatter

**Priority:** 🔴 CRITICAL
**Effort:** 3-4 days
**Impact:** Platform-optimized videos

**Implementation:**

```python
# File: src/features/video/formatter.py

import moviepy.editor as mp
from typing import Dict, Literal
import cv2
import numpy as np

class PlatformVideoFormatter:
    """Format videos for different social media platforms"""

    PLATFORM_SPECS = {
        "tiktok": {
            "aspect_ratio": (9, 16),
            "resolution": (1080, 1920),
            "max_duration": 600,  # 10 minutes
            "fps": 30
        },
        "instagram_reels": {
            "aspect_ratio": (9, 16),
            "resolution": (1080, 1920),
            "max_duration": 90,
            "fps": 30
        },
        "instagram_feed": {
            "aspect_ratio": (4, 5),
            "resolution": (1080, 1350),
            "max_duration": 60,
            "fps": 30
        },
        "youtube": {
            "aspect_ratio": (16, 9),
            "resolution": (1920, 1080),
            "max_duration": 43200,  # 12 hours
            "fps": 30
        },
        "youtube_shorts": {
            "aspect_ratio": (9, 16),
            "resolution": (1080, 1920),
            "max_duration": 60,
            "fps": 30
        },
        "linkedin": {
            "aspect_ratio": (1, 1),
            "resolution": (1200, 1200),
            "max_duration": 600,
            "fps": 30
        }
    }

    def create_all_versions(
        self,
        source_video: str,
        platforms: List[str],
        smart_crop: bool = True,
        add_safe_zones: bool = True
    ) -> Dict[str, str]:
        """Create platform-specific versions of video"""

        results = {}

        for platform in platforms:
            output_path = source_video.replace(".mp4", f"_{platform}.mp4")

            results[platform] = self.format_for_platform(
                source_video=source_video,
                platform=platform,
                output_path=output_path,
                smart_crop=smart_crop,
                add_safe_zones=add_safe_zones
            )

        return results

    def format_for_platform(
        self,
        source_video: str,
        platform: str,
        output_path: str,
        smart_crop: bool = True,
        add_safe_zones: bool = True
    ) -> str:
        """Format video for specific platform"""

        specs = self.PLATFORM_SPECS[platform]

        video = mp.VideoFileClip(source_video)

        # Trim if too long
        if video.duration > specs["max_duration"]:
            video = video.subclip(0, specs["max_duration"])

        # Resize with smart crop
        if smart_crop:
            video = self._smart_crop(video, specs["resolution"])
        else:
            video = self._simple_resize(video, specs["resolution"])

        # Add safe zones
        if add_safe_zones:
            video = self._add_safe_zones(video, platform)

        # Set FPS
        video = video.set_fps(specs["fps"])

        # Export
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=specs["fps"]
        )

        return output_path

    def _smart_crop(self, video: mp.VideoFileClip, target_resolution: tuple) -> mp.VideoFileClip:
        """Intelligently crop video to target resolution"""

        target_width, target_height = target_resolution
        target_ratio = target_width / target_height

        source_width, source_height = video.size
        source_ratio = source_width / source_height

        if abs(target_ratio - source_ratio) < 0.1:
            # Similar aspect ratio, just resize
            return video.resize(target_resolution)

        # Detect subject using face/object detection
        subject_center = self._detect_subject_center(video)

        # Crop around subject
        if target_ratio < source_ratio:
            # Need to crop width
            new_width = int(source_height * target_ratio)
            x_center = int(subject_center[0] * source_width)
            x1 = max(0, x_center - new_width // 2)
            x2 = min(source_width, x1 + new_width)

            video = video.crop(x1=x1, x2=x2)
        else:
            # Need to crop height
            new_height = int(source_width / target_ratio)
            y_center = int(subject_center[1] * source_height)
            y1 = max(0, y_center - new_height // 2)
            y2 = min(source_height, y1 + new_height)

            video = video.crop(y1=y1, y2=y2)

        return video.resize(target_resolution)

    def _detect_subject_center(self, video: mp.VideoFileClip) -> tuple:
        """Detect main subject in video using face/object detection"""

        # Sample first frame
        frame = video.get_frame(1)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Use Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            # Use first detected face as subject
            x, y, w, h = faces[0]
            center_x = (x + w / 2) / frame.shape[1]
            center_y = (y + h / 2) / frame.shape[0]
            return (center_x, center_y)

        # Default to center if no face detected
        return (0.5, 0.5)

    def _simple_resize(self, video: mp.VideoFileClip, target_resolution: tuple) -> mp.VideoFileClip:
        """Simple resize with letterboxing"""
        return video.resize(target_resolution)

    def _add_safe_zones(self, video: mp.VideoFileClip, platform: str) -> mp.VideoFileClip:
        """Add safe zones to keep important content visible"""
        # Platform-specific safe zones (areas to avoid for text/faces)
        # TikTok: avoid bottom 20% (UI elements)
        # Instagram: avoid top 15% and bottom 20%
        # This is mainly for guidance, actual implementation would overlay guides
        return video


# API endpoint
# File: director-ui/src/api/routers/formatter.py

from fastapi import APIRouter, UploadFile
from features.video.formatter import PlatformVideoFormatter

router = APIRouter(prefix="/api/format", tags=["format"])

@router.post("/platforms")
async def format_for_platforms(
    video: UploadFile,
    platforms: List[str],
    smart_crop: bool = True
):
    """Format video for multiple platforms"""

    formatter = PlatformVideoFormatter()

    # Save uploaded video
    video_path = f"/tmp/{video.filename}"
    with open(video_path, "wb") as f:
        f.write(await video.read())

    # Create platform versions
    results = formatter.create_all_versions(
        source_video=video_path,
        platforms=platforms,
        smart_crop=smart_crop,
        add_safe_zones=True
    )

    return {
        "success": True,
        "versions": results
    }
```

---

### 1.3 Voice Cloning Integration

**Priority:** 🔴 CRITICAL
**Effort:** 1 day
**Impact:** Brand consistency

**Implementation:**

```python
# File: src/features/audio/voice_cloning.py

from elevenlabs import Voice, VoiceSettings, clone
from elevenlabs.client import ElevenLabs
import os

class VoiceCloner:
    """Clone and manage brand voices"""

    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))

    def clone_voice(
        self,
        sample_audio_paths: List[str],
        voice_name: str,
        description: str = ""
    ) -> Voice:
        """Clone a voice from audio samples"""

        voice = clone(
            name=voice_name,
            description=description,
            files=sample_audio_paths
        )

        return voice

    def generate_speech(
        self,
        text: str,
        voice_id: str,
        emotion: Literal["neutral", "enthusiastic", "calm", "serious"] = "neutral",
        speed: float = 1.0,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> bytes:
        """Generate speech using cloned voice"""

        # Emotion-based settings
        emotion_settings = {
            "neutral": {"stability": 0.5, "similarity_boost": 0.75},
            "enthusiastic": {"stability": 0.3, "similarity_boost": 0.85},
            "calm": {"stability": 0.7, "similarity_boost": 0.65},
            "serious": {"stability": 0.8, "similarity_boost": 0.70}
        }

        settings = emotion_settings.get(emotion, emotion_settings["neutral"])

        audio = self.client.generate(
            text=text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    stability=settings["stability"],
                    similarity_boost=settings["similarity_boost"],
                    style=0.0,
                    use_speaker_boost=True
                )
            ),
            model="eleven_multilingual_v2"
        )

        return audio

    def list_cloned_voices(self) -> List[Voice]:
        """List all cloned voices"""
        voices = self.client.voices.get_all()
        return [v for v in voices.voices if v.category == "cloned"]
```

---

## 🔥 Phase 2: Engagement & Virality (Week 2)

**Goal:** Maximize watch time and engagement

### 2.1 Hook Optimization System

**Priority:** 🔴 CRITICAL
**Effort:** 2 days
**Impact:** 3x retention improvement

**Implementation:**

```python
# File: src/features/video/hooks.py

from typing import List, Literal
import moviepy.editor as mp
from openai import OpenAI

class HookOptimizer:
    """Optimize video hooks for maximum retention"""

    HOOK_TEMPLATES = {
        "curiosity_gap": [
            "Wait until you see what happens next...",
            "You won't believe what I found...",
            "This is crazy..."
        ],
        "pattern_interrupt": [
            "STOP scrolling.",
            "Watch this.",
            "POV: You're about to learn..."
        ],
        "value_promise": [
            "I'm about to show you...",
            "Here's exactly how to...",
            "In the next 30 seconds..."
        ],
        "controversy": [
            "Nobody talks about this...",
            "They don't want you to know...",
            "This is actually illegal in some countries..."
        ],
        "story": [
            "So I was walking down the street when...",
            "3 years ago I had no idea...",
            "Let me tell you a story..."
        ]
    }

    def __init__(self):
        self.client = OpenAI()

    def generate_hook(
        self,
        video_topic: str,
        style: Literal["curiosity_gap", "pattern_interrupt", "value_promise", "controversy", "story"] = "curiosity_gap",
        platform: Literal["tiktok", "instagram", "youtube_shorts"] = "tiktok"
    ) -> str:
        """Generate optimized hook for video"""

        prompt = f"""
        Create a viral hook for a {platform} video about: {video_topic}

        Style: {style}

        Requirements:
        - Must grab attention in first 1 second
        - Must be 5-8 words max
        - Must create curiosity or pattern interrupt
        - Must match platform style

        Examples of {style} hooks:
        {chr(10).join(self.HOOK_TEMPLATES[style])}

        Generate 1 hook:
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9
        )

        return response.choices[0].message.content.strip()

    def add_hook_to_video(
        self,
        video_path: str,
        hook_text: str,
        output_path: str,
        style: Literal["tiktok", "instagram", "youtube"] = "tiktok"
    ) -> str:
        """Add hook overlay to video"""

        video = mp.VideoFileClip(video_path)

        # Create hook text clip
        hook_clip = mp.TextClip(
            txt=hook_text,
            fontsize=80,
            font="Impact",
            color="yellow",
            stroke_color="black",
            stroke_width=3,
            method="caption",
            size=(video.w * 0.8, None)
        ).set_position('center').set_duration(3).set_start(0)

        # Add zoom effect for emphasis
        hook_clip = hook_clip.resize(lambda t: 1 + 0.05 * t)  # Zoom in

        # Composite
        final = mp.CompositeVideoClip([video, hook_clip])
        final.write_videofile(output_path)

        return output_path

    def test_hooks(
        self,
        video_path: str,
        hook_options: List[str],
        platform: str = "tiktok"
    ) -> List[dict]:
        """Create multiple versions with different hooks for A/B testing"""

        versions = []

        for i, hook in enumerate(hook_options):
            output_path = video_path.replace(".mp4", f"_hook_{i}.mp4")

            result_path = self.add_hook_to_video(
                video_path=video_path,
                hook_text=hook,
                output_path=output_path,
                style=platform
            )

            versions.append({
                "hook": hook,
                "path": result_path,
                "variant_id": f"hook_{i}"
            })

        return versions
```

---

### 2.2 Engagement Triggers System

**Priority:** 🔴 CRITICAL
**Effort:** 2 days
**Impact:** 2x engagement rate

**Implementation:**

```python
# File: src/features/video/engagement.py

import moviepy.editor as mp
from typing import List, Literal
import random

class EngagementTriggers:
    """Add engagement-boosting elements to videos"""

    CTA_TEMPLATES = {
        "comment": [
            "Comment YES if you agree",
            "Drop a 🔥 in the comments",
            "Let me know your thoughts below"
        ],
        "share": [
            "Tag someone who needs to see this",
            "Send this to your friend",
            "Share this with someone"
        ],
        "follow": [
            "Follow for more",
            "Follow if you want part 2",
            "Hit that follow button"
        ],
        "like": [
            "Double tap if you love this",
            "Like for more content like this",
            "Smash that like button"
        ]
    }

    PATTERN_INTERRUPTS = {
        "zoom": {"scale": 1.2, "duration": 0.3},
        "shake": {"amplitude": 10, "frequency": 50},
        "flash": {"opacity": 0.3, "duration": 0.1},
        "bounce": {"distance": 20, "duration": 0.5}
    }

    def add_pattern_interrupts(
        self,
        video_path: str,
        output_path: str,
        interrupt_interval: float = 7.0,  # Every 7 seconds
        interrupt_type: Literal["zoom", "shake", "flash", "bounce"] = "zoom"
    ) -> str:
        """Add pattern interrupts to maintain attention"""

        video = mp.VideoFileClip(video_path)

        # Calculate interrupt positions
        interrupt_times = []
        current_time = interrupt_interval
        while current_time < video.duration:
            interrupt_times.append(current_time)
            current_time += interrupt_interval

        clips = []
        last_time = 0

        for interrupt_time in interrupt_times:
            # Regular segment
            segment = video.subclip(last_time, interrupt_time)
            clips.append(segment)

            # Interrupt segment
            interrupt_segment = video.subclip(interrupt_time, min(interrupt_time + 0.5, video.duration))

            if interrupt_type == "zoom":
                interrupt_segment = interrupt_segment.resize(1.2)
            elif interrupt_type == "shake":
                # Add shake effect
                interrupt_segment = self._add_shake_effect(interrupt_segment)

            clips.append(interrupt_segment)
            last_time = interrupt_time + 0.5

        # Add remaining video
        if last_time < video.duration:
            clips.append(video.subclip(last_time, video.duration))

        final = mp.concatenate_videoclips(clips)
        final.write_videofile(output_path)

        return output_path

    def add_cta_overlay(
        self,
        video_path: str,
        output_path: str,
        cta_type: Literal["comment", "share", "follow", "like"] = "follow",
        position: float = 0.9  # 90% through video
    ) -> str:
        """Add call-to-action overlay"""

        video = mp.VideoFileClip(video_path)

        # Select random CTA
        cta_text = random.choice(self.CTA_TEMPLATES[cta_type])

        # Create CTA clip
        cta_clip = mp.TextClip(
            txt=cta_text,
            fontsize=50,
            font="Arial-Bold",
            color="white",
            bg_color="rgba(0,0,0,0.7)",
            method="caption",
            size=(video.w * 0.8, None)
        ).set_position(('center', 'bottom')).set_duration(3).set_start(video.duration * position)

        # Add bounce animation
        cta_clip = cta_clip.set_position(lambda t: ('center', video.h - 200 + 20 * abs(np.sin(t * 10))))

        final = mp.CompositeVideoClip([video, cta_clip])
        final.write_videofile(output_path)

        return output_path

    def _add_shake_effect(self, clip: mp.VideoClip) -> mp.VideoClip:
        """Add shake effect to clip"""
        def shake_position(t):
            x_offset = random.randint(-10, 10)
            y_offset = random.randint(-10, 10)
            return (x_offset, y_offset)

        return clip.set_position(shake_position)
```

---

## 📦 Phase 3: Content Workflow (Week 3)

### 3.1 Content Repurposing Pipeline

**Priority:** 🟠 HIGH
**Effort:** 1 week
**Impact:** 10x content output

**Implementation:**

```python
# File: src/features/content/repurposer.py

from typing import List, Dict
import moviepy.editor as mp
from openai import OpenAI

class ContentRepurposer:
    """Repurpose long-form content into multiple platform-optimized clips"""

    def __init__(self):
        self.client = OpenAI()

    def analyze_video_for_clips(
        self,
        video_path: str,
        transcript: str,
        target_platforms: List[str]
    ) -> List[dict]:
        """Analyze video and identify best clip opportunities"""

        prompt = f"""
        Analyze this video transcript and identify the best 30-90 second clips for social media.

        Transcript:
        {transcript}

        Target platforms: {', '.join(target_platforms)}

        For each clip, provide:
        1. Start time (MM:SS)
        2. End time (MM:SS)
        3. Hook/title
        4. Why it's engaging
        5. Best platform(s)

        Identify 8-12 clip opportunities that:
        - Have a complete thought/story
        - Start with a strong hook
        - Have a clear payoff
        - Are 30-90 seconds long

        Format as JSON array.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def create_platform_clip(
        self,
        source_video: str,
        start_time: float,
        end_time: float,
        platform: str,
        hook_text: str,
        add_subtitles: bool = True
    ) -> str:
        """Create platform-optimized clip"""

        video = mp.VideoFileClip(source_video).subclip(start_time, end_time)

        # Format for platform
        from features.video.formatter import PlatformVideoFormatter
        formatter = PlatformVideoFormatter()

        temp_path = f"/tmp/clip_{platform}_{start_time}.mp4"
        video.write_videofile(temp_path)

        formatted_path = formatter.format_for_platform(
            source_video=temp_path,
            platform=platform,
            output_path=temp_path.replace(".mp4", "_formatted.mp4"),
            smart_crop=True
        )

        # Add hook
        from features.video.hooks import HookOptimizer
        hook_optimizer = HookOptimizer()

        with_hook = hook_optimizer.add_hook_to_video(
            video_path=formatted_path,
            hook_text=hook_text,
            output_path=formatted_path.replace(".mp4", "_hooked.mp4"),
            style=platform
        )

        # Add subtitles
        if add_subtitles:
            from features.video.subtitles import SubtitleGenerator
            subtitle_gen = SubtitleGenerator()

            final_path = subtitle_gen.add_subtitles(
                video_path=with_hook,
                output_path=with_hook.replace(".mp4", "_final.mp4"),
                style=platform
            )

            return final_path

        return with_hook

    def repurpose_content(
        self,
        source_video: str,
        source_script: str,
        target_formats: Dict[str, dict]
    ) -> Dict[str, List[str]]:
        """Repurpose content into multiple platform-specific clips"""

        # Analyze video for clip opportunities
        clips_data = self.analyze_video_for_clips(
            video_path=source_video,
            transcript=source_script,
            target_platforms=list(target_formats.keys())
        )

        results = {platform: [] for platform in target_formats.keys()}

        for clip in clips_data['clips']:
            platforms = clip.get('best_platforms', target_formats.keys())

            for platform in platforms:
                if platform in target_formats:
                    output = self.create_platform_clip(
                        source_video=source_video,
                        start_time=self._parse_time(clip['start_time']),
                        end_time=self._parse_time(clip['end_time']),
                        platform=platform,
                        hook_text=clip['hook'],
                        add_subtitles=True
                    )

                    results[platform].append(output)

        return results

    def _parse_time(self, time_str: str) -> float:
        """Parse MM:SS to seconds"""
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
```

---

### 3.2 Template Library System

**Priority:** 🟠 HIGH
**Effort:** 3-4 days
**Impact:** 5x production speed

See full template system implementation in next phase...

---

## 🎨 Phase 4-6 Details

*[Continue with remaining phases...]*

---

## 📊 Success Metrics

Track these metrics after each phase:

### Phase 1 Metrics
- ✅ % of videos with subtitles (Target: 100%)
- ✅ Average time to format for platforms (Target: <5 min)
- ✅ Brand voice consistency score (Target: 95%+)

### Phase 2 Metrics
- ✅ Average watch time (Target: +40%)
- ✅ Engagement rate (Target: +100%)
- ✅ Hook retention rate (Target: 70%+ at 3s)

### Phase 3 Metrics
- ✅ Clips generated per source video (Target: 10+)
- ✅ Time to create full video (Target: <20 min)
- ✅ Template usage rate (Target: 80%)

### Overall Success Criteria
- 🎯 10x content output volume
- 🎯 87% time reduction per video
- 🎯 2-3x engagement improvement
- 🎯 50% cost reduction per view

---

## 🚀 Getting Started

**Week 1 Priority:**
1. Start with subtitles system (highest impact)
2. Then platform formatter
3. Then voice cloning

**Command:**
```bash
cd src
uv add openai moviepy opencv-python elevenlabs
uv run python -m features.video.subtitles
```

---

**Next:** Begin Phase 1 implementation or adjust priorities based on your needs.
