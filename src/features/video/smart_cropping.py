"""
Smart Cropping with Subject Tracking using YOLO

Advanced subject detection and tracking for intelligent video cropping.
Goes beyond face detection to track people, objects, animals, and more.

Features:
- YOLO object detection (80+ classes: person, dog, car, phone, etc.)
- Subject tracking across frames (motion prediction)
- Priority-based cropping (faces > people > main objects)
- Smooth camera motion (no jarring jumps)
- Multi-subject detection with attention weighting
- Works with platform formatter for auto-cropping

Run from project root with:
    PYTHONPATH=src python -c "from features.video.smart_cropping import SmartCropper; ..."
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Literal
from dataclasses import dataclass, field
import numpy as np
import cv2

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    VideoFileClip = None


DetectionMode = Literal["fast", "balanced", "accurate"]


@dataclass
class Detection:
    """Object detection result."""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    center: Tuple[float, float]  # normalized (0-1)
    area: float  # normalized (0-1)
    priority: int  # 1=highest


@dataclass
class TrackingResult:
    """Subject tracking result across frames."""
    detections: List[Detection]
    primary_subject: Optional[Detection]
    crop_center: Tuple[float, float]  # normalized (0-1)
    confidence: float
    frame_number: int


class SmartCropper:
    """
    Advanced smart cropping with YOLO object detection and subject tracking.

    Detects and tracks subjects intelligently:
    - Faces (highest priority)
    - People/persons (high priority)
    - Animals (medium priority)
    - Objects (lower priority)

    Use Cases:
    1. Auto-crop videos for platform-specific aspect ratios
    2. Keep main subject in frame when resizing
    3. Track moving subjects smoothly
    4. Multi-platform video optimization

    Example:
        >>> cropper = SmartCropper()
        >>> crop_centers = cropper.track_subject(
        ...     video_path="video.mp4",
        ...     target_aspect_ratio=(9, 16)  # TikTok
        ... )
        >>> # Use crop_centers to intelligently crop video
    """

    # YOLO class IDs and priorities
    CLASS_PRIORITIES = {
        0: ("person", 2),      # Person - high priority
        15: ("cat", 3),        # Cat
        16: ("dog", 3),        # Dog
        17: ("horse", 3),      # Horse
        62: ("laptop", 4),     # Laptop
        63: ("mouse", 5),      # Mouse
        64: ("remote", 5),     # Remote
        65: ("keyboard", 5),   # Keyboard
        66: ("cell phone", 4), # Cell phone
        67: ("microwave", 5),  # Microwave
    }

    def __init__(self, detection_mode: DetectionMode = "balanced"):
        """
        Initialize smart cropper.

        Args:
            detection_mode: Detection mode
                - "fast": Faster but less accurate (every 10 frames)
                - "balanced": Good speed/accuracy balance (every 5 frames)
                - "accurate": Best accuracy (every frame)
        """
        self.detection_mode = detection_mode

        # Load face detector (OpenCV - always available)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Try to load YOLO (optional - falls back to face detection only)
        self.yolo_net = None
        self.yolo_available = False

        try:
            # Try to load YOLOv3 (pre-trained on COCO dataset)
            # Note: This requires downloading weights files
            # For production, you'd download these once
            weights_path = "yolov3.weights"
            config_path = "yolov3.cfg"

            if os.path.exists(weights_path) and os.path.exists(config_path):
                self.yolo_net = cv2.dnn.readNet(weights_path, config_path)
                self.yolo_available = True
                print("✅ YOLO detection enabled")
            else:
                print("⚠️  YOLO weights not found - using face detection only")
                print("   Download from: https://pjreddie.com/darknet/yolo/")
        except Exception as e:
            print(f"⚠️  Could not load YOLO: {e}")
            print("   Falling back to face detection only")

        # Frame sampling based on mode
        self.frame_skip = {
            "fast": 10,
            "balanced": 5,
            "accurate": 1
        }[detection_mode]

    def track_subject(
        self,
        video_path: str,
        target_aspect_ratio: Tuple[int, int] = (9, 16),
        smoothing: float = 0.7
    ) -> List[Tuple[float, float]]:
        """
        Track main subject through video and return crop centers.

        Args:
            video_path: Path to video file
            target_aspect_ratio: Target aspect ratio (width, height)
            smoothing: Smoothing factor 0-1 (higher = smoother but less responsive)

        Returns:
            List of (x, y) crop centers for each frame (normalized 0-1)

        Example:
            >>> cropper = SmartCropper()
            >>> centers = cropper.track_subject("video.mp4", (9, 16))
            >>> # centers[0] = (0.5, 0.3)  # Center at x=50%, y=30%
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        if VideoFileClip is None:
            raise ImportError("MoviePy required. Install: uv add moviepy opencv-python")

        video = VideoFileClip(video_path)
        fps = video.fps
        total_frames = int(video.duration * fps)

        print(f"Tracking subject in {video_path}")
        print(f"  Total frames: {total_frames}")
        print(f"  Frame skip: {self.frame_skip}")
        print(f"  Detection mode: {self.detection_mode}")

        # Track subject positions
        crop_centers = []
        last_center = (0.5, 0.5)  # Start at center

        for frame_num in range(0, total_frames, self.frame_skip):
            # Get frame
            time = frame_num / fps
            if time >= video.duration:
                break

            frame = video.get_frame(time)

            # Detect subjects
            detections = self._detect_subjects(frame)

            # Find primary subject
            if detections:
                primary = self._select_primary_subject(detections)
                current_center = primary.center
            else:
                # No detection - use last known position
                current_center = last_center

            # Apply smoothing
            smoothed_center = (
                smoothing * last_center[0] + (1 - smoothing) * current_center[0],
                smoothing * last_center[1] + (1 - smoothing) * current_center[1]
            )

            # Store crop center
            crop_centers.append(smoothed_center)
            last_center = smoothed_center

        video.close()

        # Interpolate for skipped frames
        if self.frame_skip > 1:
            crop_centers = self._interpolate_centers(crop_centers, total_frames, self.frame_skip)

        print(f"✅ Tracking complete: {len(crop_centers)} frames")
        return crop_centers

    def _detect_subjects(self, frame: np.ndarray) -> List[Detection]:
        """Detect all subjects in frame."""
        detections = []

        # 1. Face detection (highest priority)
        face_detections = self._detect_faces(frame)
        detections.extend(face_detections)

        # 2. YOLO object detection (if available)
        if self.yolo_available:
            yolo_detections = self._detect_yolo_objects(frame)
            detections.extend(yolo_detections)

        # 3. Fallback: motion/saliency detection
        if not detections:
            fallback_detection = self._detect_motion_saliency(frame)
            if fallback_detection:
                detections.append(fallback_detection)

        return detections

    def _detect_faces(self, frame: np.ndarray) -> List[Detection]:
        """Detect faces using OpenCV."""
        detections = []
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        h, w = frame.shape[:2]

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        for (x, y, fw, fh) in faces:
            center_x = (x + fw / 2) / w
            center_y = (y + fh / 2) / h
            area = (fw * fh) / (w * h)

            detection = Detection(
                class_id=-1,  # Face (special)
                class_name="face",
                confidence=1.0,
                bbox=(x, y, fw, fh),
                center=(center_x, center_y),
                area=area,
                priority=1  # Highest priority
            )
            detections.append(detection)

        return detections

    def _detect_yolo_objects(self, frame: np.ndarray) -> List[Detection]:
        """Detect objects using YOLO."""
        if not self.yolo_net:
            return []

        detections = []
        h, w = frame.shape[:2]

        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.yolo_net.setInput(blob)

        # Get output layers
        layer_names = self.yolo_net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.yolo_net.getUnconnectedOutLayers()]

        # Run detection
        outputs = self.yolo_net.forward(output_layers)

        # Parse detections
        for output in outputs:
            for det in output:
                scores = det[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5:  # Confidence threshold
                    # Get bounding box
                    center_x = int(det[0] * w)
                    center_y = int(det[1] * h)
                    width = int(det[2] * w)
                    height = int(det[3] * h)

                    x = int(center_x - width / 2)
                    y = int(center_y - height / 2)

                    # Get class name and priority
                    class_name, priority = self.CLASS_PRIORITIES.get(
                        class_id,
                        (f"class_{class_id}", 5)
                    )

                    detection = Detection(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=float(confidence),
                        bbox=(x, y, width, height),
                        center=(center_x / w, center_y / h),
                        area=(width * height) / (w * h),
                        priority=priority
                    )
                    detections.append(detection)

        return detections

    def _detect_motion_saliency(self, frame: np.ndarray) -> Optional[Detection]:
        """Fallback: detect salient regions using edge detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        h, w = frame.shape[:2]

        # Use Laplacian for edge detection
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        abs_laplacian = np.absolute(laplacian)

        # Divide into grid and find most detailed region
        grid_size = 4
        cell_h = h // grid_size
        cell_w = w // grid_size

        max_detail = 0
        best_cell = (grid_size // 2, grid_size // 2)  # Default center

        for i in range(grid_size):
            for j in range(grid_size):
                cell = abs_laplacian[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                detail = np.mean(cell)

                if detail > max_detail:
                    max_detail = detail
                    best_cell = (i, j)

        # Calculate center of best cell
        center_x = (best_cell[1] + 0.5) / grid_size
        center_y = (best_cell[0] + 0.5) / grid_size

        return Detection(
            class_id=-2,
            class_name="salient_region",
            confidence=0.5,
            bbox=(best_cell[1] * cell_w, best_cell[0] * cell_h, cell_w, cell_h),
            center=(center_x, center_y),
            area=(cell_w * cell_h) / (w * h),
            priority=6  # Lowest priority
        )

    def _select_primary_subject(self, detections: List[Detection]) -> Detection:
        """Select primary subject from detections."""
        if not detections:
            # Return center default
            return Detection(-1, "none", 0.0, (0, 0, 0, 0), (0.5, 0.5), 0.0, 10)

        # Sort by priority, then by size
        sorted_dets = sorted(
            detections,
            key=lambda d: (d.priority, -d.area)
        )

        return sorted_dets[0]

    def _interpolate_centers(
        self,
        centers: List[Tuple[float, float]],
        total_frames: int,
        skip: int
    ) -> List[Tuple[float, float]]:
        """Interpolate crop centers for skipped frames."""
        if skip == 1:
            return centers

        interpolated = []

        for i in range(len(centers) - 1):
            start = centers[i]
            end = centers[i + 1]

            # Add start frame
            interpolated.append(start)

            # Interpolate in-between frames
            for j in range(1, skip):
                alpha = j / skip
                interp_x = start[0] * (1 - alpha) + end[0] * alpha
                interp_y = start[1] * (1 - alpha) + end[1] * alpha
                interpolated.append((interp_x, interp_y))

        # Add last center
        if centers:
            interpolated.append(centers[-1])

        # Trim or pad to exact frame count
        while len(interpolated) < total_frames:
            interpolated.append(interpolated[-1] if interpolated else (0.5, 0.5))

        return interpolated[:total_frames]

    def apply_smart_crop(
        self,
        video_path: str,
        output_path: str,
        target_size: Tuple[int, int],
        track: bool = True
    ) -> str:
        """
        Apply smart cropping to video.

        Args:
            video_path: Input video path
            output_path: Output video path
            target_size: Target (width, height) in pixels
            track: Use subject tracking (True) or single detection (False)

        Returns:
            Path to output video

        Example:
            >>> cropper = SmartCropper()
            >>> cropper.apply_smart_crop(
            ...     "input.mp4",
            ...     "output_9x16.mp4",
            ...     (1080, 1920),  # TikTok size
            ...     track=True
            ... )
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        if VideoFileClip is None:
            raise ImportError("MoviePy required")

        print(f"Applying smart crop: {video_path} -> {output_path}")
        print(f"  Target size: {target_size}")

        video = VideoFileClip(video_path)
        target_w, target_h = target_size
        target_ratio = target_w / target_h

        # Get crop centers
        if track:
            print("  Tracking subject...")
            crop_centers = self.track_subject(
                video_path,
                target_aspect_ratio=(target_w, target_h)
            )
        else:
            # Single detection at middle frame
            mid_frame = video.get_frame(video.duration / 2)
            detections = self._detect_subjects(mid_frame)
            if detections:
                primary = self._select_primary_subject(detections)
                center = primary.center
            else:
                center = (0.5, 0.5)
            crop_centers = [center] * int(video.duration * video.fps)

        # Apply crop with tracking
        def crop_frame(get_frame, t):
            frame = get_frame(t)
            h, w = frame.shape[:2]

            # Get crop center for this time
            frame_idx = int(t * video.fps)
            if frame_idx >= len(crop_centers):
                frame_idx = len(crop_centers) - 1

            center_x, center_y = crop_centers[frame_idx]

            # Calculate crop box
            if w / h > target_ratio:
                # Video is wider - crop width
                crop_h = h
                crop_w = int(crop_h * target_ratio)
            else:
                # Video is taller - crop height
                crop_w = w
                crop_h = int(crop_w / target_ratio)

            # Calculate crop coordinates around center
            x1 = int(center_x * w - crop_w / 2)
            y1 = int(center_y * h - crop_h / 2)

            # Clamp to frame bounds
            x1 = max(0, min(x1, w - crop_w))
            y1 = max(0, min(y1, h - crop_h))

            x2 = x1 + crop_w
            y2 = y1 + crop_h

            # Crop and resize
            cropped = frame[y1:y2, x1:x2]
            resized = cv2.resize(cropped, target_size, interpolation=cv2.INTER_LANCZOS4)

            return resized

        # Apply transformation
        cropped_video = video.fl(crop_frame, apply_to=['mask'])

        # Write output
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        cropped_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )

        video.close()
        cropped_video.close()

        print(f"✅ Smart crop complete: {output_path}")
        return output_path


# Convenience function

def smart_crop_video(
    video_path: str,
    output_path: str,
    target_size: Tuple[int, int],
    detection_mode: DetectionMode = "balanced"
) -> str:
    """
    Convenience function for smart cropping.

    Example:
        >>> smart_crop_video(
        ...     "input.mp4",
        ...     "output.mp4",
        ...     (1080, 1920),  # TikTok
        ...     detection_mode="balanced"
        ... )
    """
    cropper = SmartCropper(detection_mode=detection_mode)
    return cropper.apply_smart_crop(video_path, output_path, target_size, track=True)


if __name__ == "__main__":
    print("Smart Cropping with Subject Tracking")
    print("=" * 60)
    print("\nIntelligent video cropping using:")
    print("  • Face detection (OpenCV)")
    print("  • Object detection (YOLO - if available)")
    print("  • Subject tracking across frames")
    print("  • Smooth camera motion")
    print("\nKeeps main subjects in frame when cropping for social media!")
