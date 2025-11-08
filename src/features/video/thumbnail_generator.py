"""
Thumbnail Generator with A/B Testing

Thumbnails determine 90% of whether someone clicks on your video.
This module generates eye-catching thumbnails optimized for different platforms
and supports A/B testing to find winners.

Features:
- Auto-generate thumbnails from video frames
- Face detection for optimal framing
- Text overlay with viral styles
- Emotion detection (surprised face = +41% CTR)
- Color optimization and contrast boost
- A/B testing support
- Platform-specific templates (YouTube, TikTok, Instagram)
- Thumbnail scoring and recommendations

Run from project root with:
    PYTHONPATH=src python -c "from features.video.thumbnail_generator import ThumbnailGenerator; ..."
"""

import os
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Literal
from dataclasses import dataclass, field
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    VideoFileClip = None


Platform = Literal["youtube", "tiktok", "instagram", "facebook", "twitter", "linkedin"]
ThumbnailStyle = Literal["viral", "professional", "minimal", "energetic", "mystery", "educational"]


@dataclass
class ThumbnailScore:
    """Thumbnail analysis score."""
    overall_score: float = 0.0  # 0-100
    face_score: float = 0.0     # Face presence and size
    contrast_score: float = 0.0  # Color contrast
    text_score: float = 0.0     # Text readability
    emotion_score: float = 0.0  # Facial expression impact
    composition_score: float = 0.0  # Rule of thirds, balance

    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    variant_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "overall_score": round(self.overall_score, 1),
            "face_score": round(self.face_score, 1),
            "contrast_score": round(self.contrast_score, 1),
            "text_score": round(self.text_score, 1),
            "emotion_score": round(self.emotion_score, 1),
            "composition_score": round(self.composition_score, 1),
            "recommendations": self.recommendations,
            "warnings": self.warnings,
            "variant_id": self.variant_id,
            "grade": self._get_grade()
        }

    def _get_grade(self) -> str:
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
        else:
            return "C"


@dataclass
class ThumbnailTemplate:
    """Thumbnail template configuration."""
    name: str
    text_position: Tuple[str, str]  # ("center", "top"), ("left", "bottom"), etc.
    text_size_ratio: float  # Relative to image height
    text_color: Tuple[int, int, int]
    outline_color: Optional[Tuple[int, int, int]]
    outline_width: int
    background_overlay: bool
    overlay_opacity: float  # 0.0-1.0
    effects: List[str]  # ["contrast_boost", "saturation", "sharp", "vignette"]


class ThumbnailGenerator:
    """
    Generate and optimize thumbnails for maximum click-through rate.

    Thumbnail Best Practices:
    - Show expressive faces (surprised/shocked = +41% CTR)
    - Use high contrast colors (yellow/red text on dark backgrounds)
    - Keep text under 4 words
    - Show action or result, not setup
    - Use close-up shots (faces fill 40-60% of thumbnail)
    - Test multiple variations (A/B testing can double CTR)

    Example:
        >>> gen = ThumbnailGenerator()
        >>> thumbnail = gen.create_thumbnail(
        ...     video_path="video.mp4",
        ...     text="SHOCKING Result!",
        ...     style="viral",
        ...     platform="youtube"
        ... )
    """

    # Platform specifications
    PLATFORM_SPECS = {
        "youtube": {
            "width": 1280,
            "height": 720,
            "aspect_ratio": (16, 9),
            "max_file_size_mb": 2,
            "recommended_formats": ["jpg", "png"]
        },
        "tiktok": {
            "width": 1080,
            "height": 1920,
            "aspect_ratio": (9, 16),
            "max_file_size_mb": 5,
            "recommended_formats": ["jpg", "png"]
        },
        "instagram": {
            "width": 1080,
            "height": 1080,
            "aspect_ratio": (1, 1),
            "max_file_size_mb": 8,
            "recommended_formats": ["jpg", "png"]
        },
        "facebook": {
            "width": 1200,
            "height": 630,
            "aspect_ratio": (1.91, 1),
            "max_file_size_mb": 8,
            "recommended_formats": ["jpg", "png"]
        },
        "twitter": {
            "width": 1200,
            "height": 675,
            "aspect_ratio": (16, 9),
            "max_file_size_mb": 5,
            "recommended_formats": ["jpg", "png"]
        },
        "linkedin": {
            "width": 1200,
            "height": 627,
            "aspect_ratio": (1.91, 1),
            "max_file_size_mb": 5,
            "recommended_formats": ["jpg", "png"]
        }
    }

    # Thumbnail style templates
    STYLE_TEMPLATES = {
        "viral": ThumbnailTemplate(
            name="Viral",
            text_position=("center", "top"),
            text_size_ratio=0.15,
            text_color=(255, 255, 0),  # Yellow
            outline_color=(0, 0, 0),
            outline_width=8,
            background_overlay=True,
            overlay_opacity=0.3,
            effects=["contrast_boost", "saturation", "sharp"]
        ),
        "professional": ThumbnailTemplate(
            name="Professional",
            text_position=("center", "bottom"),
            text_size_ratio=0.10,
            text_color=(255, 255, 255),
            outline_color=(0, 0, 0),
            outline_width=4,
            background_overlay=False,
            overlay_opacity=0.0,
            effects=["sharp"]
        ),
        "minimal": ThumbnailTemplate(
            name="Minimal",
            text_position=("left", "bottom"),
            text_size_ratio=0.08,
            text_color=(255, 255, 255),
            outline_color=None,
            outline_width=0,
            background_overlay=False,
            overlay_opacity=0.0,
            effects=[]
        ),
        "energetic": ThumbnailTemplate(
            name="Energetic",
            text_position=("center", "center"),
            text_size_ratio=0.18,
            text_color=(255, 50, 50),  # Bright red
            outline_color=(255, 255, 255),
            outline_width=10,
            background_overlay=True,
            overlay_opacity=0.2,
            effects=["contrast_boost", "saturation", "sharp", "vignette"]
        ),
        "mystery": ThumbnailTemplate(
            name="Mystery",
            text_position=("center", "bottom"),
            text_size_ratio=0.12,
            text_color=(200, 200, 255),  # Light blue
            outline_color=(0, 0, 100),
            outline_width=6,
            background_overlay=True,
            overlay_opacity=0.4,
            effects=["contrast_boost", "vignette"]
        ),
        "educational": ThumbnailTemplate(
            name="Educational",
            text_position=("left", "top"),
            text_size_ratio=0.09,
            text_color=(50, 150, 255),  # Blue
            outline_color=(255, 255, 255),
            outline_width=3,
            background_overlay=False,
            overlay_opacity=0.0,
            effects=["sharp"]
        )
    }

    def __init__(self):
        """Initialize thumbnail generator."""
        # Load face detector
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Try to load emotion cascade (if available)
        try:
            smile_cascade_path = cv2.data.haarcascades + "haarcascade_smile.xml"
            self.smile_cascade = cv2.CascadeClassifier(smile_cascade_path)
        except:
            self.smile_cascade = None

    def create_thumbnail(
        self,
        video_path: str,
        output_path: str,
        text: Optional[str] = None,
        style: ThumbnailStyle = "viral",
        platform: Platform = "youtube",
        frame_time: Optional[float] = None,
        auto_select_frame: bool = True
    ) -> str:
        """
        Create thumbnail from video.

        Args:
            video_path: Path to video file
            output_path: Output thumbnail path
            text: Text overlay (keep under 4 words!)
            style: Thumbnail style template
            platform: Target platform
            frame_time: Specific time to extract frame (seconds)
            auto_select_frame: Auto-select best frame (face, emotion, contrast)

        Returns:
            Path to generated thumbnail

        Example:
            >>> gen.create_thumbnail(
            ...     video_path="video.mp4",
            ...     output_path="thumb.jpg",
            ...     text="UNBELIEVABLE",
            ...     style="viral",
            ...     platform="youtube"
            ... )
        """
        if VideoFileClip is None:
            raise ImportError("MoviePy required. Install: uv add moviepy pillow opencv-python")

        # Load video
        video = VideoFileClip(video_path)

        # Select frame
        if auto_select_frame and frame_time is None:
            frame_time = self._select_best_frame_time(video)
        elif frame_time is None:
            frame_time = video.duration / 2  # Middle frame

        # Extract frame
        frame = video.get_frame(frame_time)
        video.close()

        # Convert to PIL Image
        img = Image.fromarray(frame)

        # Resize to platform specs
        platform_spec = self.PLATFORM_SPECS[platform]
        target_size = (platform_spec["width"], platform_spec["height"])
        img = self._resize_and_crop(img, target_size)

        # Apply style
        template = self.STYLE_TEMPLATES[style]
        img = self._apply_effects(img, template.effects)

        # Add text overlay
        if text:
            img = self._add_text_overlay(img, text, template)

        # Save
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Optimize file size
        quality = 95
        img.save(output_path, quality=quality, optimize=True)

        # Check file size and reduce quality if needed
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        max_size = platform_spec["max_file_size_mb"]

        while file_size_mb > max_size and quality > 60:
            quality -= 5
            img.save(output_path, quality=quality, optimize=True)
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)

        print(f"✅ Thumbnail created: {output_path} ({file_size_mb:.2f}MB)")
        return output_path

    def _select_best_frame_time(self, video: VideoFileClip, num_candidates: int = 20) -> float:
        """Select best frame based on face presence, emotion, and contrast."""
        duration = video.duration
        sample_times = np.linspace(0.1 * duration, 0.9 * duration, num_candidates)

        best_score = 0
        best_time = duration / 2

        for t in sample_times:
            frame = video.get_frame(t)
            score = self._score_frame(frame)

            if score > best_score:
                best_score = score
                best_time = t

        return best_time

    def _score_frame(self, frame: np.ndarray) -> float:
        """Score a frame for thumbnail suitability."""
        score = 0

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            # Face presence bonus
            score += 50

            # Larger face = better
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face
            face_ratio = (w * h) / (frame.shape[0] * frame.shape[1])
            score += min(30, face_ratio * 500)  # Optimal: 40-60% of frame

            # Check for smile/expression (if available)
            if self.smile_cascade:
                roi_gray = gray[y:y+h, x:x+w]
                smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
                if len(smiles) > 0:
                    score += 20  # Expression/emotion bonus

        # Contrast score
        contrast = frame.std()
        score += min(20, (contrast / 50) * 20)

        return score

    def _resize_and_crop(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize and crop image to target size."""
        target_ratio = target_size[0] / target_size[1]
        img_ratio = img.width / img.height

        if img_ratio > target_ratio:
            # Image is wider - crop width
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            # Image is taller - crop height
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))

        # Resize
        img = img.resize(target_size, Image.LANCZOS)
        return img

    def _apply_effects(self, img: Image.Image, effects: List[str]) -> Image.Image:
        """Apply visual effects to image."""
        for effect in effects:
            if effect == "contrast_boost":
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.3)
            elif effect == "saturation":
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(1.2)
            elif effect == "sharp":
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.5)
            elif effect == "vignette":
                img = self._add_vignette(img)

        return img

    def _add_vignette(self, img: Image.Image, strength: float = 0.5) -> Image.Image:
        """Add vignette effect (darkened edges)."""
        # Create radial gradient mask
        width, height = img.size
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)

        # Draw ellipse gradient
        for i in range(50):
            alpha = int(255 * (1 - i / 50) * strength)
            bbox = [
                i * width // 100,
                i * height // 100,
                width - i * width // 100,
                height - i * height // 100
            ]
            draw.ellipse(bbox, fill=alpha)

        # Apply mask
        black = Image.new('RGB', (width, height), (0, 0, 0))
        img = Image.composite(img, black, mask)
        return img

    def _add_text_overlay(
        self,
        img: Image.Image,
        text: str,
        template: ThumbnailTemplate
    ) -> Image.Image:
        """Add text overlay to thumbnail."""
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Calculate font size
        font_size = int(height * template.text_size_ratio)

        # Try to load a bold font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position
        h_align, v_align = template.text_position

        if h_align == "left":
            x = width * 0.05
        elif h_align == "right":
            x = width * 0.95 - text_width
        else:  # center
            x = (width - text_width) / 2

        if v_align == "top":
            y = height * 0.1
        elif v_align == "bottom":
            y = height * 0.85 - text_height
        else:  # center
            y = (height - text_height) / 2

        # Add background overlay
        if template.background_overlay:
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)

            padding = 20
            overlay_draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=(0, 0, 0, int(255 * template.overlay_opacity))
            )
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(img)

        # Draw text with outline
        if template.outline_color:
            # Draw outline
            for offset_x in range(-template.outline_width, template.outline_width + 1):
                for offset_y in range(-template.outline_width, template.outline_width + 1):
                    if offset_x != 0 or offset_y != 0:
                        draw.text(
                            (x + offset_x, y + offset_y),
                            text,
                            font=font,
                            fill=template.outline_color
                        )

        # Draw main text
        draw.text((x, y), text, font=font, fill=template.text_color)

        return img

    def create_ab_test_variations(
        self,
        video_path: str,
        output_dir: str,
        text_variations: List[str],
        style: ThumbnailStyle = "viral",
        platform: Platform = "youtube"
    ) -> List[str]:
        """
        Create multiple thumbnail variations for A/B testing.

        Args:
            video_path: Source video
            output_dir: Output directory
            text_variations: List of text options to test
            style: Thumbnail style
            platform: Target platform

        Returns:
            List of thumbnail paths

        Example:
            >>> gen.create_ab_test_variations(
            ...     video_path="video.mp4",
            ...     output_dir="thumbnails/",
            ...     text_variations=[
            ...         "SHOCKING Result!",
            ...         "You Won't Believe This",
            ...         "This Changed Everything"
            ...     ]
            ... )
        """
        os.makedirs(output_dir, exist_ok=True)
        thumbnail_paths = []

        for i, text in enumerate(text_variations, 1):
            output_path = os.path.join(output_dir, f"thumb_variant_{chr(64+i)}.jpg")
            path = self.create_thumbnail(
                video_path=video_path,
                output_path=output_path,
                text=text,
                style=style,
                platform=platform
            )
            thumbnail_paths.append(path)

        return thumbnail_paths

    def analyze_thumbnail(self, thumbnail_path: str, variant_id: Optional[str] = None) -> ThumbnailScore:
        """
        Analyze thumbnail quality and provide recommendations.

        Args:
            thumbnail_path: Path to thumbnail image
            variant_id: Optional variant identifier

        Returns:
            ThumbnailScore with analysis and recommendations
        """
        img = cv2.imread(thumbnail_path)
        if img is None:
            raise FileNotFoundError(f"Thumbnail not found: {thumbnail_path}")

        score = ThumbnailScore(variant_id=variant_id)

        # Face analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face
            face_ratio = (w * h) / (img.shape[0] * img.shape[1])

            if 0.2 <= face_ratio <= 0.6:
                score.face_score = 100
            elif face_ratio < 0.2:
                score.face_score = 50
                score.recommendations.append("Face is too small - zoom in for better impact")
            else:
                score.face_score = 70
                score.recommendations.append("Face is very large - consider showing more context")

            # Emotion detection
            if self.smile_cascade:
                roi_gray = gray[y:y+h, x:x+w]
                smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
                if len(smiles) > 0:
                    score.emotion_score = 100
                else:
                    score.emotion_score = 60
                    score.recommendations.append("Try thumbnail with more expressive emotion (surprised/shocked faces = +41% CTR)")
        else:
            score.face_score = 30
            score.recommendations.append("No face detected - thumbnails with faces get 38% more clicks")
            score.emotion_score = 0

        # Contrast analysis
        contrast = img.std()
        score.contrast_score = min(100, (contrast / 50) * 100)
        if score.contrast_score < 60:
            score.recommendations.append("Boost contrast for more eye-catching thumbnail")

        # Overall composition (simplified - check rule of thirds)
        score.composition_score = 75  # Placeholder

        # Overall score
        score.overall_score = (
            score.face_score * 0.35 +
            score.contrast_score * 0.25 +
            score.emotion_score * 0.25 +
            score.composition_score * 0.15
        )

        if score.overall_score < 70:
            score.warnings.append("Low thumbnail score - consider creating new variations")

        return score


# Convenience functions

def create_thumbnail(
    video_path: str,
    output_path: str,
    text: Optional[str] = None,
    style: ThumbnailStyle = "viral",
    platform: Platform = "youtube"
) -> str:
    """Convenience function to create thumbnail."""
    gen = ThumbnailGenerator()
    return gen.create_thumbnail(video_path, output_path, text, style, platform)


if __name__ == "__main__":
    print("Thumbnail Generator - Optimize for Clicks")
    print("=" * 60)
    print("\nThumbnails determine 90% of clicks!")
    print("Use this tool to create eye-catching thumbnails.\n")
