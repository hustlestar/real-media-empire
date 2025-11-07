"""
Platform video formatter for social media optimization.

Automatically converts videos to the correct aspect ratios and specifications
for different social media platforms (TikTok, Instagram, YouTube, LinkedIn, etc.).
"""

from typing import Dict, List, Literal, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
    import moviepy.video.fx.all as vfx
except ImportError:
    VideoFileClip = CompositeVideoClip = ColorClip = None
    vfx = None

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

logger = logging.getLogger(__name__)

Platform = Literal[
    "tiktok",
    "instagram_reels",
    "instagram_feed",
    "instagram_story",
    "youtube",
    "youtube_shorts",
    "linkedin",
    "facebook",
    "twitter"
]


@dataclass
class PlatformSpec:
    """Platform video specifications"""
    name: str
    aspect_ratio: Tuple[int, int]  # (width, height) ratio
    resolution: Tuple[int, int]  # (width, height) in pixels
    max_duration: int  # seconds
    fps: int
    max_file_size_mb: int


class PlatformSpecs:
    """Specifications for all supported platforms"""

    SPECS = {
        "tiktok": PlatformSpec(
            name="TikTok",
            aspect_ratio=(9, 16),
            resolution=(1080, 1920),
            max_duration=600,  # 10 minutes
            fps=30,
            max_file_size_mb=287
        ),
        "instagram_reels": PlatformSpec(
            name="Instagram Reels",
            aspect_ratio=(9, 16),
            resolution=(1080, 1920),
            max_duration=90,
            fps=30,
            max_file_size_mb=100
        ),
        "instagram_story": PlatformSpec(
            name="Instagram Story",
            aspect_ratio=(9, 16),
            resolution=(1080, 1920),
            max_duration=60,
            fps=30,
            max_file_size_mb=100
        ),
        "instagram_feed": PlatformSpec(
            name="Instagram Feed",
            aspect_ratio=(4, 5),
            resolution=(1080, 1350),
            max_duration=60,
            fps=30,
            max_file_size_mb=100
        ),
        "youtube": PlatformSpec(
            name="YouTube",
            aspect_ratio=(16, 9),
            resolution=(1920, 1080),
            max_duration=43200,  # 12 hours
            fps=30,
            max_file_size_mb=256000  # 256GB
        ),
        "youtube_shorts": PlatformSpec(
            name="YouTube Shorts",
            aspect_ratio=(9, 16),
            resolution=(1080, 1920),
            max_duration=60,
            fps=30,
            max_file_size_mb=100
        ),
        "linkedin": PlatformSpec(
            name="LinkedIn",
            aspect_ratio=(1, 1),
            resolution=(1200, 1200),
            max_duration=600,  # 10 minutes
            fps=30,
            max_file_size_mb=5000  # 5GB
        ),
        "facebook": PlatformSpec(
            name="Facebook",
            aspect_ratio=(16, 9),
            resolution=(1920, 1080),
            max_duration=7200,  # 2 hours
            fps=30,
            max_file_size_mb=4000  # 4GB
        ),
        "twitter": PlatformSpec(
            name="Twitter/X",
            aspect_ratio=(16, 9),
            resolution=(1280, 720),
            max_duration=140,
            fps=30,
            max_file_size_mb=512
        )
    }

    @classmethod
    def get_spec(cls, platform: Platform) -> PlatformSpec:
        """Get platform specification"""
        return cls.SPECS.get(platform)

    @classmethod
    def list_platforms(cls) -> List[str]:
        """List all supported platforms"""
        return list(cls.SPECS.keys())


class PlatformVideoFormatter:
    """
    Format videos for different social media platforms.

    Features:
    - Automatic aspect ratio conversion
    - Smart cropping (detects and follows faces/subjects)
    - Letterboxing/pillarboxing options
    - Platform-specific optimizations
    - Batch processing for multiple platforms

    Example:
        >>> formatter = PlatformVideoFormatter()
        >>> versions = formatter.create_all_versions(
        ...     source_video="input.mp4",
        ...     platforms=["tiktok", "youtube", "linkedin"]
        ... )
    """

    def __init__(self):
        """Initialize platform video formatter"""
        if VideoFileClip is None:
            raise ImportError("moviepy required. Install: uv add moviepy")

        # Load face detector if OpenCV available
        self.face_cascade = None
        if cv2 is not None:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def create_all_versions(
        self,
        source_video: str,
        platforms: List[Platform],
        smart_crop: bool = True,
        add_padding: bool = False,
        padding_color: str = "black"
    ) -> Dict[str, str]:
        """
        Create platform-specific versions of a video.

        Args:
            source_video: Path to source video
            platforms: List of platforms to generate for
            smart_crop: Use smart cropping (detect faces/subjects)
            add_padding: Add padding instead of cropping
            padding_color: Color for padding (black, white, blur)

        Returns:
            Dictionary mapping platform names to output paths

        Example:
            >>> formatter = PlatformVideoFormatter()
            >>> versions = formatter.create_all_versions(
            ...     source_video="video.mp4",
            ...     platforms=["tiktok", "youtube", "linkedin"],
            ...     smart_crop=True
            ... )
            >>> print(versions)
            {
                'tiktok': 'video_tiktok.mp4',
                'youtube': 'video_youtube.mp4',
                'linkedin': 'video_linkedin.mp4'
            }
        """
        results = {}

        for platform in platforms:
            try:
                output_path = self._generate_output_path(source_video, platform)

                result_path = self.format_for_platform(
                    source_video=source_video,
                    platform=platform,
                    output_path=output_path,
                    smart_crop=smart_crop,
                    add_padding=add_padding,
                    padding_color=padding_color
                )

                results[platform] = result_path
                logger.info(f"Created {platform} version: {result_path}")

            except Exception as e:
                logger.error(f"Error creating {platform} version: {e}")
                results[platform] = None

        return results

    def format_for_platform(
        self,
        source_video: str,
        platform: Platform,
        output_path: str,
        smart_crop: bool = True,
        add_padding: bool = False,
        padding_color: str = "black"
    ) -> str:
        """
        Format video for specific platform.

        Args:
            source_video: Input video path
            platform: Target platform
            output_path: Output video path
            smart_crop: Use smart cropping
            add_padding: Add padding instead of cropping
            padding_color: Padding color

        Returns:
            Path to formatted video
        """
        spec = PlatformSpecs.get_spec(platform)
        if not spec:
            raise ValueError(f"Unsupported platform: {platform}")

        logger.info(f"Formatting video for {spec.name}")
        logger.info(f"Target: {spec.resolution[0]}x{spec.resolution[1]} ({spec.aspect_ratio[0]}:{spec.aspect_ratio[1]})")

        # Load video
        video = VideoFileClip(source_video)

        # Trim if too long
        if video.duration > spec.max_duration:
            logger.warning(f"Video duration ({video.duration}s) exceeds max ({spec.max_duration}s), trimming")
            video = video.subclip(0, spec.max_duration)

        # Resize/crop to target aspect ratio
        if add_padding:
            video = self._add_padding(video, spec, padding_color)
        elif smart_crop and self.face_cascade is not None:
            video = self._smart_crop(video, spec)
        else:
            video = self._simple_resize(video, spec)

        # Set FPS
        video = video.set_fps(spec.fps)

        # Write output
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=spec.fps,
            bitrate="5000k",
            logger=None
        )

        video.close()
        return output_path

    def _smart_crop(self, video: VideoFileClip, spec: PlatformSpec) -> VideoFileClip:
        """
        Intelligently crop video to target aspect ratio.

        Detects faces/subjects and crops around them.
        """
        target_width, target_height = spec.resolution
        target_ratio = target_width / target_height

        source_width, source_height = video.size
        source_ratio = source_width / source_height

        # If aspect ratios are similar, just resize
        if abs(target_ratio - source_ratio) < 0.1:
            return video.resize(spec.resolution)

        # Detect subject center
        subject_center = self._detect_subject_center(video)

        logger.info(f"Smart crop: subject at ({subject_center[0]:.2f}, {subject_center[1]:.2f})")

        # Crop around subject
        if target_ratio < source_ratio:
            # Need to crop width (making it taller/narrower)
            new_width = int(source_height * target_ratio)
            x_center = int(subject_center[0] * source_width)
            x1 = max(0, x_center - new_width // 2)
            x2 = min(source_width, x1 + new_width)

            # Adjust if we hit the edge
            if x2 - x1 < new_width:
                x1 = max(0, x2 - new_width)

            video = video.crop(x1=x1, x2=x2, y1=0, y2=source_height)

        else:
            # Need to crop height (making it wider/shorter)
            new_height = int(source_width / target_ratio)
            y_center = int(subject_center[1] * source_height)
            y1 = max(0, y_center - new_height // 2)
            y2 = min(source_height, y1 + new_height)

            # Adjust if we hit the edge
            if y2 - y1 < new_height:
                y1 = max(0, y2 - new_height)

            video = video.crop(x1=0, x2=source_width, y1=y1, y2=y2)

        # Resize to exact target resolution
        return video.resize(spec.resolution)

    def _simple_resize(self, video: VideoFileClip, spec: PlatformSpec) -> VideoFileClip:
        """Simple resize with aspect ratio preservation"""
        target_width, target_height = spec.resolution
        target_ratio = target_width / target_height

        source_width, source_height = video.size
        source_ratio = source_width / source_height

        # If aspect ratios match, just resize
        if abs(target_ratio - source_ratio) < 0.01:
            return video.resize(spec.resolution)

        # Calculate new dimensions
        if source_ratio > target_ratio:
            # Source is wider, crop width
            new_height = source_height
            new_width = int(source_height * target_ratio)
            x_center = source_width // 2
            x1 = max(0, x_center - new_width // 2)
            x2 = min(source_width, x1 + new_width)
            video = video.crop(x1=x1, x2=x2, y1=0, y2=source_height)
        else:
            # Source is taller, crop height
            new_width = source_width
            new_height = int(source_width / target_ratio)
            y_center = source_height // 2
            y1 = max(0, y_center - new_height // 2)
            y2 = min(source_height, y1 + new_height)
            video = video.crop(x1=0, x2=source_width, y1=y1, y2=y2)

        return video.resize(spec.resolution)

    def _add_padding(
        self,
        video: VideoFileClip,
        spec: PlatformSpec,
        padding_color: str = "black"
    ) -> VideoFileClip:
        """Add padding (letterbox/pillarbox) to video"""
        target_width, target_height = spec.resolution

        # Scale video to fit within target dimensions
        video = video.resize(height=target_height if video.w/video.h > target_width/target_height else None,
                            width=target_width if video.w/video.h <= target_width/target_height else None)

        # Create background
        if padding_color == "blur":
            # Blurred background
            bg = video.resize((target_width, target_height))
            bg = bg.fx(vfx.blur, 15)
        else:
            # Solid color background
            color_map = {"black": (0, 0, 0), "white": (255, 255, 255)}
            color = color_map.get(padding_color, (0, 0, 0))
            bg = ColorClip(size=spec.resolution, color=color, duration=video.duration)

        # Composite video on background
        video = video.set_position("center")
        final = CompositeVideoClip([bg, video])

        return final

    def _detect_subject_center(self, video: VideoFileClip) -> Tuple[float, float]:
        """
        Detect main subject in video using face detection.

        Returns:
            (x, y) normalized coordinates (0.0 to 1.0) of subject center
        """
        # Sample frame from middle of video
        sample_time = video.duration / 2
        frame = video.get_frame(sample_time)

        if cv2 is None or self.face_cascade is None:
            # Default to center if OpenCV not available
            return (0.5, 0.5)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            # Use first detected face as subject
            x, y, w, h = faces[0]
            center_x = (x + w / 2) / frame.shape[1]
            center_y = (y + h / 2) / frame.shape[0]
            logger.info(f"Detected face at ({center_x:.2f}, {center_y:.2f})")
            return (center_x, center_y)

        # If no face detected, look for areas of high contrast/detail
        # (likely to be the subject)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        abs_laplacian = np.absolute(laplacian)

        # Divide image into grid and find most detailed section
        h, w = abs_laplacian.shape
        grid_size = 5
        cell_h = h // grid_size
        cell_w = w // grid_size

        max_detail = 0
        best_cell = (grid_size // 2, grid_size // 2)  # Default to center

        for i in range(grid_size):
            for j in range(grid_size):
                y1, y2 = i * cell_h, (i + 1) * cell_h
                x1, x2 = j * cell_w, (j + 1) * cell_w
                cell_detail = abs_laplacian[y1:y2, x1:x2].sum()

                if cell_detail > max_detail:
                    max_detail = cell_detail
                    best_cell = (j, i)

        # Convert grid position to normalized coordinates
        center_x = (best_cell[0] + 0.5) / grid_size
        center_y = (best_cell[1] + 0.5) / grid_size

        logger.info(f"Subject detected at ({center_x:.2f}, {center_y:.2f}) via detail analysis")
        return (center_x, center_y)

    def _generate_output_path(self, source_video: str, platform: Platform) -> str:
        """Generate output path for platform version"""
        source_path = Path(source_video)
        stem = source_path.stem
        ext = source_path.suffix

        return str(source_path.parent / f"{stem}_{platform}{ext}")

    def validate_video(self, video_path: str, platform: Platform) -> Dict[str, any]:
        """
        Validate if video meets platform requirements.

        Args:
            video_path: Path to video file
            platform: Target platform

        Returns:
            Dictionary with validation results
        """
        spec = PlatformSpecs.get_spec(platform)
        if not spec:
            raise ValueError(f"Unsupported platform: {platform}")

        video = VideoFileClip(video_path)

        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "specs": {
                "duration": video.duration,
                "resolution": video.size,
                "fps": video.fps,
                "aspect_ratio": f"{video.w}:{video.h}"
            }
        }

        # Check duration
        if video.duration > spec.max_duration:
            results["errors"].append(
                f"Duration ({video.duration:.1f}s) exceeds maximum ({spec.max_duration}s)"
            )
            results["valid"] = False

        # Check aspect ratio
        video_ratio = video.w / video.h
        target_ratio = spec.aspect_ratio[0] / spec.aspect_ratio[1]

        if abs(video_ratio - target_ratio) > 0.1:
            results["warnings"].append(
                f"Aspect ratio ({video_ratio:.2f}) differs from optimal ({target_ratio:.2f})"
            )

        # Check file size
        file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
        if file_size_mb > spec.max_file_size_mb:
            results["errors"].append(
                f"File size ({file_size_mb:.1f}MB) exceeds maximum ({spec.max_file_size_mb}MB)"
            )
            results["valid"] = False

        video.close()
        return results


# Convenience function
def format_video_for_platforms(
    source_video: str,
    platforms: List[Platform],
    smart_crop: bool = True
) -> Dict[str, str]:
    """
    Convenience function to format video for multiple platforms.

    Args:
        source_video: Input video path
        platforms: List of target platforms
        smart_crop: Use smart cropping

    Returns:
        Dictionary mapping platforms to output paths

    Example:
        >>> from features.video.formatter import format_video_for_platforms
        >>> versions = format_video_for_platforms(
        ...     source_video="video.mp4",
        ...     platforms=["tiktok", "youtube", "linkedin"]
        ... )
    """
    formatter = PlatformVideoFormatter()
    return formatter.create_all_versions(
        source_video=source_video,
        platforms=platforms,
        smart_crop=smart_crop
    )
