"""
Hook Optimization System - First 3 Seconds Analyzer

The first 3 seconds of a video determine if viewers keep watching or scroll away.
This module analyzes and optimizes video hooks for maximum retention.

Features:
- Visual hook analysis (motion, colors, faces, text)
- Text hook analysis (curiosity gaps, power words, questions)
- Audio hook analysis (voice energy, music presence)
- Pattern interrupt detection
- Hook scoring and recommendations
- A/B testing support
- Platform-specific optimization

Run from project root with:
    PYTHONPATH=src python -c "from features.video.hook_optimizer import HookOptimizer; ..."
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Literal
from dataclasses import dataclass, field
import numpy as np
import cv2

try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    from moviepy.video.fx.all import speedx
except ImportError:
    VideoFileClip = None


Platform = Literal["tiktok", "youtube_shorts", "instagram_reels", "youtube", "generic"]


@dataclass
class HookScore:
    """Hook analysis score and recommendations."""
    overall_score: float = 0.0  # 0-100
    visual_score: float = 0.0   # 0-100
    text_score: float = 0.0     # 0-100
    audio_score: float = 0.0    # 0-100

    # Sub-scores
    motion_score: float = 0.0
    color_impact: float = 0.0
    face_presence: float = 0.0
    text_hook_strength: float = 0.0
    curiosity_gap: float = 0.0
    voice_energy: float = 0.0

    # Analysis
    hook_type: str = "unknown"  # question, statement, action, reveal, etc.
    pattern_interrupts: List[str] = field(default_factory=list)
    power_words: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # A/B testing
    variant_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "overall_score": round(self.overall_score, 1),
            "visual_score": round(self.visual_score, 1),
            "text_score": round(self.text_score, 1),
            "audio_score": round(self.audio_score, 1),
            "motion_score": round(self.motion_score, 1),
            "color_impact": round(self.color_impact, 1),
            "face_presence": round(self.face_presence, 1),
            "text_hook_strength": round(self.text_hook_strength, 1),
            "curiosity_gap": round(self.curiosity_gap, 1),
            "voice_energy": round(self.voice_energy, 1),
            "hook_type": self.hook_type,
            "pattern_interrupts": self.pattern_interrupts,
            "power_words": self.power_words,
            "recommendations": self.recommendations,
            "warnings": self.warnings,
            "variant_id": self.variant_id,
            "grade": self._get_grade()
        }

    def _get_grade(self) -> str:
        """Get letter grade based on score."""
        if self.overall_score >= 90:
            return "A+"
        elif self.overall_score >= 85:
            return "A"
        elif self.overall_score >= 80:
            return "B+"
        elif self.overall_score >= 75:
            return "B"
        elif self.overall_score >= 70:
            return "C+"
        elif self.overall_score >= 65:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        else:
            return "F"


class HookOptimizer:
    """
    Analyze and optimize video hooks for maximum retention.

    The first 3 seconds are CRITICAL for shorts/reels:
    - 65% of viewers decide in first 2 seconds
    - 80% decision made by 3 seconds
    - Strong hooks = 2-5x higher retention

    Use Cases:
    1. Analyze existing videos to find what works
    2. Score multiple hook variations for A/B testing
    3. Get recommendations to improve hooks
    4. Optimize for specific platforms

    Example:
        >>> optimizer = HookOptimizer()
        >>> score = optimizer.analyze_hook(
        ...     video_path="video.mp4",
        ...     text="Did you know this iPhone trick?",
        ...     platform="tiktok"
        ... )
        >>> print(f"Hook Score: {score.overall_score}/100")
        >>> print(f"Grade: {score._get_grade()}")
        >>> for rec in score.recommendations:
        ...     print(f"  • {rec}")
    """

    # Power words that create curiosity/urgency
    POWER_WORDS = {
        "curiosity": ["secret", "hidden", "trick", "hack", "reveal", "discover", "leaked",
                     "insider", "nobody", "shocking", "unbelievable", "insane", "crazy"],
        "urgency": ["now", "today", "immediately", "urgent", "breaking", "just", "finally"],
        "exclusivity": ["exclusive", "only", "limited", "rare", "unique", "never"],
        "authority": ["proven", "scientific", "expert", "professional", "guaranteed"],
        "emotional": ["amazing", "incredible", "stunning", "mind-blowing", "game-changing"],
        "negative": ["mistake", "wrong", "avoid", "never", "stop", "quit", "warning"],
        "question": ["how", "why", "what", "when", "where", "which", "did you know"]
    }

    # Hook patterns that work
    HOOK_PATTERNS = {
        "question": r"^(how|why|what|when|where|which|did you|have you|can you|do you)",
        "number": r"^\d+\s+(ways|things|secrets|tips|tricks|hacks|reasons)",
        "negative": r"^(stop|never|don't|avoid|mistake|warning)",
        "curiosity": r"(secret|hidden|nobody|shocking|you won't believe)",
        "authority": r"^(expert|professional|i'm a|as a)",
        "promise": r"(will|you'll|going to|about to)",
        "compare": r"(vs|versus|better than|instead of)",
    }

    # Platform-specific recommendations
    PLATFORM_SPECS = {
        "tiktok": {
            "optimal_hook_duration": 2.0,  # seconds
            "prefer_questions": True,
            "prefer_fast_motion": True,
            "prefer_text_overlay": True,
            "prefer_music": True,
        },
        "youtube_shorts": {
            "optimal_hook_duration": 3.0,
            "prefer_questions": True,
            "prefer_fast_motion": False,
            "prefer_text_overlay": True,
            "prefer_music": False,
        },
        "instagram_reels": {
            "optimal_hook_duration": 2.5,
            "prefer_questions": True,
            "prefer_fast_motion": True,
            "prefer_text_overlay": True,
            "prefer_music": True,
        },
        "youtube": {
            "optimal_hook_duration": 5.0,
            "prefer_questions": False,
            "prefer_fast_motion": False,
            "prefer_text_overlay": False,
            "prefer_music": False,
        },
        "generic": {
            "optimal_hook_duration": 3.0,
            "prefer_questions": True,
            "prefer_fast_motion": True,
            "prefer_text_overlay": True,
            "prefer_music": True,
        }
    }

    def __init__(self):
        """Initialize hook optimizer."""
        if VideoFileClip is None:
            raise ImportError(
                "MoviePy required for hook optimization. Install: uv add moviepy opencv-python numpy"
            )

        # Load face detector for face presence analysis
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze_hook(
        self,
        video_path: str,
        text: Optional[str] = None,
        platform: Platform = "generic",
        hook_duration: float = 3.0,
        variant_id: Optional[str] = None
    ) -> HookScore:
        """
        Analyze video hook (first 3 seconds).

        Args:
            video_path: Path to video file
            text: Hook text/script (first few words spoken/shown)
            platform: Target platform for optimization
            hook_duration: Duration to analyze (default 3.0 seconds)
            variant_id: ID for A/B testing variants

        Returns:
            HookScore with detailed analysis and recommendations

        Example:
            >>> score = optimizer.analyze_hook(
            ...     video_path="video.mp4",
            ...     text="Watch what happens when I drop this iPhone",
            ...     platform="tiktok"
            ... )
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        score = HookScore(variant_id=variant_id)

        # Load video
        video = VideoFileClip(video_path)
        hook_clip = video.subclip(0, min(hook_duration, video.duration))

        # Analyze visual elements
        self._analyze_visual_hook(hook_clip, score)

        # Analyze text hook
        if text:
            self._analyze_text_hook(text, platform, score)

        # Analyze audio
        if hook_clip.audio:
            self._analyze_audio_hook(hook_clip, score)

        # Calculate overall score
        weights = {
            "visual": 0.4,
            "text": 0.4,
            "audio": 0.2
        }

        score.overall_score = (
            score.visual_score * weights["visual"] +
            score.text_score * weights["text"] +
            score.audio_score * weights["audio"]
        )

        # Generate platform-specific recommendations
        self._generate_recommendations(score, platform, text)

        # Cleanup
        hook_clip.close()
        video.close()

        return score

    def _analyze_visual_hook(self, clip: VideoFileClip, score: HookScore) -> None:
        """Analyze visual elements of hook."""
        # Sample frames
        n_samples = 5
        sample_times = np.linspace(0, clip.duration, n_samples, endpoint=False)
        frames = [clip.get_frame(t) for t in sample_times]

        # 1. Motion analysis
        motion_score = self._analyze_motion(frames)
        score.motion_score = motion_score

        # 2. Color impact analysis
        color_score = self._analyze_colors(frames)
        score.color_impact = color_score

        # 3. Face presence
        face_score = self._analyze_faces(frames)
        score.face_presence = face_score

        # Visual score is weighted average
        score.visual_score = (
            motion_score * 0.4 +
            color_score * 0.3 +
            face_score * 0.3
        )

    def _analyze_motion(self, frames: List[np.ndarray]) -> float:
        """Analyze motion/movement in frames."""
        if len(frames) < 2:
            return 0.0

        motion_scores = []
        for i in range(len(frames) - 1):
            # Convert to grayscale
            gray1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY)

            # Calculate frame difference
            diff = cv2.absdiff(gray1, gray2)
            motion = np.mean(diff)
            motion_scores.append(motion)

        avg_motion = np.mean(motion_scores)

        # Normalize to 0-100 (higher motion = better for hooks)
        # Typical motion ranges: 0-50 (static to very dynamic)
        normalized_score = min(100, (avg_motion / 30) * 100)

        return normalized_score

    def _analyze_colors(self, frames: List[np.ndarray]) -> float:
        """Analyze color vibrancy/impact."""
        color_scores = []

        for frame in frames:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

            # Analyze saturation (vibrancy)
            saturation = hsv[:, :, 1].mean()

            # Analyze value (brightness)
            value = hsv[:, :, 2].mean()

            # Color diversity (more unique colors = more interesting)
            unique_colors = len(np.unique(frame.reshape(-1, 3), axis=0))
            color_diversity = min(100, (unique_colors / 10000) * 100)

            # Combined color score
            color_score = (saturation / 255 * 40) + (value / 255 * 30) + (color_diversity * 0.3)
            color_scores.append(color_score)

        return np.mean(color_scores)

    def _analyze_faces(self, frames: List[np.ndarray]) -> float:
        """Analyze face presence (faces = higher engagement)."""
        face_scores = []

        for frame in frames:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(faces) > 0:
                # Score based on face size (bigger = more prominent)
                face_areas = [w * h for (x, y, w, h) in faces]
                largest_face = max(face_areas)
                frame_area = frame.shape[0] * frame.shape[1]
                face_ratio = largest_face / frame_area

                # Score: faces present + good size = high score
                face_score = min(100, 50 + (face_ratio * 500))
            else:
                face_score = 0

            face_scores.append(face_score)

        return np.mean(face_scores)

    def _analyze_text_hook(self, text: str, platform: Platform, score: HookScore) -> None:
        """Analyze text hook for curiosity/engagement."""
        text_lower = text.lower().strip()

        # 1. Detect hook type
        hook_type = self._detect_hook_type(text_lower)
        score.hook_type = hook_type

        # 2. Find power words
        power_words = self._find_power_words(text_lower)
        score.power_words = power_words

        # 3. Analyze curiosity gap
        curiosity_score = self._analyze_curiosity_gap(text_lower, hook_type)
        score.curiosity_gap = curiosity_score

        # 4. Length check (first 3 seconds = ~7-12 words)
        word_count = len(text.split())
        optimal_length = 7 <= word_count <= 12
        length_score = 100 if optimal_length else max(0, 100 - abs(word_count - 9) * 10)

        # 5. Pattern interrupts
        pattern_interrupts = self._detect_pattern_interrupts(text_lower)
        score.pattern_interrupts = pattern_interrupts

        # Text hook strength
        hook_strength = 0
        if hook_type in ["question", "number", "curiosity"]:
            hook_strength += 30
        if len(power_words) > 0:
            hook_strength += min(40, len(power_words) * 15)
        if curiosity_score > 70:
            hook_strength += 30

        score.text_hook_strength = min(100, hook_strength)

        # Overall text score
        score.text_score = (
            score.text_hook_strength * 0.5 +
            curiosity_score * 0.3 +
            length_score * 0.2
        )

    def _detect_hook_type(self, text: str) -> str:
        """Detect type of hook being used."""
        for hook_type, pattern in self.HOOK_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return hook_type
        return "statement"

    def _find_power_words(self, text: str) -> List[str]:
        """Find power words in text."""
        found_words = []
        for category, words in self.POWER_WORDS.items():
            for word in words:
                if word in text:
                    found_words.append(word)
        return found_words

    def _analyze_curiosity_gap(self, text: str, hook_type: str) -> float:
        """Analyze how strong the curiosity gap is."""
        score = 0

        # Questions create natural curiosity
        if "?" in text or hook_type == "question":
            score += 40

        # Incomplete information
        if any(word in text for word in ["this", "it", "watch", "see", "check out", "look at"]):
            score += 20

        # Promise of value
        if any(word in text for word in ["will", "you'll", "going to", "about to", "get", "learn"]):
            score += 20

        # Intrigue words
        if any(word in text for word in ["secret", "hidden", "nobody", "shocking", "trick"]):
            score += 20

        return min(100, score)

    def _detect_pattern_interrupts(self, text: str) -> List[str]:
        """Detect pattern interrupts in text."""
        interrupts = []

        if re.search(r"^(wait|hold on|stop|before)", text):
            interrupts.append("attention_grab")

        if "?" in text:
            interrupts.append("question")

        if re.search(r"(but|however|actually|surprisingly)", text):
            interrupts.append("contradiction")

        if re.search(r"(never|don't|stop|avoid)", text):
            interrupts.append("negative_hook")

        return interrupts

    def _analyze_audio_hook(self, clip: VideoFileClip, score: HookScore) -> None:
        """Analyze audio energy/impact."""
        if not clip.audio:
            score.audio_score = 0
            score.voice_energy = 0
            return

        # Extract audio array
        audio_array = clip.audio.to_soundarray(fps=22050)

        # Calculate RMS energy (voice/sound energy)
        if len(audio_array.shape) > 1:
            # Stereo - average channels
            audio_mono = audio_array.mean(axis=1)
        else:
            audio_mono = audio_array

        # RMS energy
        rms = np.sqrt(np.mean(audio_mono ** 2))

        # Normalize (typical RMS: 0.01-0.3 for speech)
        voice_energy = min(100, (rms / 0.15) * 100)
        score.voice_energy = voice_energy

        # Audio score = voice energy
        score.audio_score = voice_energy

    def _generate_recommendations(
        self,
        score: HookScore,
        platform: Platform,
        text: Optional[str]
    ) -> None:
        """Generate actionable recommendations."""
        recommendations = []
        warnings = []

        platform_spec = self.PLATFORM_SPECS[platform]

        # Visual recommendations
        if score.motion_score < 50:
            recommendations.append(
                "🎬 Add more motion/movement in first 3 seconds (camera movement, subject action, zooms)"
            )

        if score.color_impact < 50:
            recommendations.append(
                "🎨 Use more vibrant colors or higher contrast to grab attention"
            )

        if score.face_presence < 30 and platform in ["tiktok", "instagram_reels"]:
            recommendations.append(
                "👤 Consider showing a face in the hook (faces increase engagement by 38%)"
            )

        # Text recommendations
        if text:
            if score.hook_type == "statement" and platform_spec["prefer_questions"]:
                recommendations.append(
                    "❓ Try starting with a question instead of a statement"
                )

            if len(score.power_words) == 0:
                recommendations.append(
                    f"💎 Add power words like: {', '.join(self.POWER_WORDS['curiosity'][:5])}"
                )

            if score.curiosity_gap < 60:
                recommendations.append(
                    "🔮 Create a stronger curiosity gap (tease the outcome without revealing it)"
                )

            word_count = len(text.split())
            if word_count > 15:
                warnings.append(
                    f"⚠️ Hook text too long ({word_count} words). Keep it under 12 words for first 3 seconds"
                )

        # Audio recommendations
        if score.voice_energy < 40:
            recommendations.append(
                "🎤 Increase voice energy and enthusiasm in the first 3 seconds"
            )

        # Platform-specific
        if platform == "tiktok":
            if score.motion_score < 70:
                recommendations.append(
                    "⚡ TikTok favors fast-paced content - add quick cuts or speed up slightly"
                )

        # Overall score recommendations
        if score.overall_score < 60:
            warnings.append(
                "🚨 Hook score is low. Video likely to have poor retention. Reshoot recommended."
            )
        elif score.overall_score < 75:
            recommendations.append(
                "💡 Hook is okay but has room for improvement. Consider A/B testing variations."
            )

        score.recommendations = recommendations
        score.warnings = warnings

    def compare_hooks(
        self,
        video_paths: List[str],
        texts: List[Optional[str]] = None,
        platform: Platform = "generic"
    ) -> List[HookScore]:
        """
        Compare multiple hook variations for A/B testing.

        Args:
            video_paths: List of video file paths
            texts: List of hook texts (optional)
            platform: Target platform

        Returns:
            List of HookScores sorted by overall_score (best first)

        Example:
            >>> scores = optimizer.compare_hooks(
            ...     video_paths=["hook_a.mp4", "hook_b.mp4", "hook_c.mp4"],
            ...     texts=["How to...", "Did you know...", "Watch this..."],
            ...     platform="tiktok"
            ... )
            >>> print(f"Winner: {scores[0].variant_id} with {scores[0].overall_score:.1f}")
        """
        if texts is None:
            texts = [None] * len(video_paths)

        scores = []
        for i, (video_path, text) in enumerate(zip(video_paths, texts)):
            variant_id = f"variant_{chr(65 + i)}"  # A, B, C, etc.
            score = self.analyze_hook(
                video_path=video_path,
                text=text,
                platform=platform,
                variant_id=variant_id
            )
            scores.append(score)

        # Sort by overall score (best first)
        scores.sort(key=lambda s: s.overall_score, reverse=True)

        return scores

    def create_hook_variations(
        self,
        video_path: str,
        output_dir: str,
        variations: List[Dict] = None
    ) -> List[str]:
        """
        Create hook variations with different effects for A/B testing.

        Args:
            video_path: Source video path
            output_dir: Output directory for variations
            variations: List of variation configs (speed, zoom, color)

        Returns:
            List of output file paths

        Example:
            >>> paths = optimizer.create_hook_variations(
            ...     video_path="source.mp4",
            ...     output_dir="hooks/",
            ...     variations=[
            ...         {"speed": 1.0, "zoom": 1.0},  # Original
            ...         {"speed": 1.1, "zoom": 1.0},  # Slightly faster
            ...         {"speed": 1.0, "zoom": 1.1},  # Slight zoom
            ...     ]
            ... )
        """
        if variations is None:
            variations = [
                {"speed": 1.0, "zoom": 1.0, "name": "original"},
                {"speed": 1.1, "zoom": 1.0, "name": "faster"},
                {"speed": 1.0, "zoom": 1.05, "name": "zoom"},
                {"speed": 1.1, "zoom": 1.05, "name": "faster_zoom"},
            ]

        os.makedirs(output_dir, exist_ok=True)
        output_paths = []

        video = VideoFileClip(video_path)
        hook_clip = video.subclip(0, min(3.0, video.duration))

        for i, var in enumerate(variations):
            variant_clip = hook_clip

            # Apply speed
            if var.get("speed", 1.0) != 1.0:
                variant_clip = speedx(variant_clip, var["speed"])

            # Apply zoom (simplified - center zoom)
            if var.get("zoom", 1.0) != 1.0:
                zoom_factor = var["zoom"]
                variant_clip = variant_clip.resize(zoom_factor)
                # Crop to original size (center)
                w, h = variant_clip.size
                target_w, target_h = hook_clip.size
                x1 = (w - target_w) // 2
                y1 = (h - target_h) // 2
                variant_clip = variant_clip.crop(x1=x1, y1=y1, width=target_w, height=target_h)

            # Save
            var_name = var.get("name", f"variation_{i}")
            output_path = os.path.join(output_dir, f"hook_{var_name}.mp4")
            variant_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a",
                remove_temp=True,
                logger=None
            )
            output_paths.append(output_path)

            variant_clip.close()

        hook_clip.close()
        video.close()

        return output_paths


# Convenience functions

def analyze_hook(
    video_path: str,
    text: Optional[str] = None,
    platform: Platform = "generic"
) -> HookScore:
    """
    Convenience function to analyze a video hook.

    Example:
        >>> score = analyze_hook(
        ...     video_path="video.mp4",
        ...     text="Watch what happens next!",
        ...     platform="tiktok"
        ... )
        >>> print(f"Score: {score.overall_score}/100")
    """
    optimizer = HookOptimizer()
    return optimizer.analyze_hook(video_path, text, platform)


def compare_hooks(
    video_paths: List[str],
    texts: List[Optional[str]] = None,
    platform: Platform = "generic"
) -> List[HookScore]:
    """
    Convenience function to compare multiple hooks.

    Example:
        >>> scores = compare_hooks(
        ...     video_paths=["hook_a.mp4", "hook_b.mp4"],
        ...     texts=["Version A", "Version B"],
        ...     platform="tiktok"
        ... )
    """
    optimizer = HookOptimizer()
    return optimizer.compare_hooks(video_paths, texts, platform)


if __name__ == "__main__":
    print("Hook Optimizer - First 3 Seconds Analysis")
    print("=" * 60)
    print("\nThe first 3 seconds determine if viewers watch or scroll.")
    print("This tool analyzes and scores your video hooks.\n")
    print("Example usage:")
    print("  from features.video.hook_optimizer import analyze_hook")
    print("  score = analyze_hook('video.mp4', text='Did you know...?', platform='tiktok')")
    print("  print(f'Score: {score.overall_score}/100')")
