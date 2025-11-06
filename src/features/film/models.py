"""
Core data models for film generation pipeline.

Uses Pydantic for validation and serialization.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums for Provider Selection
# ============================================================================


class ImageProvider(str, Enum):
    """Available image generation providers"""

    FAL = "fal"
    REPLICATE = "replicate"


class VideoProvider(str, Enum):
    """Available video generation providers"""

    MINIMAX = "minimax"  # Cheap: ~$0.05 per 6s
    KLING = "kling"  # Premium: ~$1.84 per 10s
    RUNWAY = "runway"  # Ultra: ~$0.05 per frame


class AudioProvider(str, Enum):
    """Available audio synthesis providers"""

    OPENAI = "openai"  # Cheap: $0.015/1K chars
    ELEVENLABS = "elevenlabs"  # Premium: $0.30/1K chars


# ============================================================================
# Configuration Models
# ============================================================================


class ImageConfig(BaseModel):
    """Configuration for image generation"""

    width: int = Field(default=1024, ge=512, le=2048)
    height: int = Field(default=576, ge=512, le=2048)
    guidance_scale: float = Field(default=3.5, ge=1.0, le=20.0)
    inference_steps: int = Field(default=28, ge=1, le=100)
    num_images: int = Field(default=1, ge=1, le=4)
    enable_safety_checker: bool = False
    output_format: Literal["jpeg", "png", "webp"] = "jpeg"
    model: str = "fal-ai/flux/dev"  # Model identifier for provider

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API calls"""
        return self.model_dump()


class VideoConfig(BaseModel):
    """Configuration for video generation"""

    duration: int = Field(default=5, ge=1, le=10, description="Duration in seconds")
    fps: int = Field(default=24, ge=16, le=60)
    mode: Literal["standard", "professional"] = "standard"
    model: Optional[str] = None  # Model identifier for provider

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API calls"""
        return self.model_dump()


class AudioConfig(BaseModel):
    """Configuration for audio synthesis"""

    voice: str = "nova"  # Voice identifier
    model: str = "tts-1"  # Model for synthesis
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    output_format: Literal["mp3", "wav", "opus"] = "mp3"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API calls"""
        return self.model_dump()


# ============================================================================
# Shot Definition Models
# ============================================================================


class ShotDefinition(BaseModel):
    """
    Definition of a single shot in the film.
    Corresponds to n8n workflow shot structure.
    """

    shot_id: str = Field(..., description="Unique identifier for shot (e.g., 'shot_001')")
    shot_number: int = Field(..., ge=1)
    shot_type: Literal["wide", "medium", "close-up", "extreme-close-up"] = "medium"

    # Prompts
    enhanced_prompt: str = Field(..., min_length=10, description="Detailed cinematic prompt")
    negative_prompt: str = Field(
        default="cartoon, anime, low quality, amateur, over-saturated, digital look", description="What to avoid in generation"
    )

    # Timing
    duration: int = Field(default=5, ge=1, le=10, description="Duration in seconds")

    # Optional dialogue
    dialogue: Optional[str] = Field(default=None, description="Spoken dialogue for this shot")

    # Metadata for categorization
    characters: List[str] = Field(default_factory=list, description="Characters in this shot")
    landscapes: List[str] = Field(default_factory=list, description="Landscape/location types")
    styles: List[str] = Field(default_factory=list, description="Visual style tags")
    mood: Optional[str] = Field(default=None, description="Emotional mood")
    time_of_day: Optional[str] = Field(default=None, description="Time of day setting")

    @field_validator("shot_id")
    @classmethod
    def validate_shot_id(cls, v: str) -> str:
        """Ensure shot_id follows naming convention"""
        if not v.startswith("shot_"):
            raise ValueError("shot_id must start with 'shot_'")
        return v


class ShotConfig(BaseModel):
    """
    Complete configuration for generating a shot.
    Combines shot definition with provider selections.
    """

    shot_def: ShotDefinition

    # Provider selection (can override defaults)
    image_provider: ImageProvider = ImageProvider.FAL
    video_provider: VideoProvider = VideoProvider.MINIMAX
    audio_provider: AudioProvider = AudioProvider.OPENAI

    # Generation configs
    image_config: ImageConfig = Field(default_factory=ImageConfig)
    video_config: VideoConfig = Field(default_factory=VideoConfig)
    audio_config: AudioConfig = Field(default_factory=AudioConfig)

    @property
    def has_dialogue(self) -> bool:
        """Check if shot has dialogue"""
        return bool(self.shot_def.dialogue)


# ============================================================================
# Result Models
# ============================================================================


class GenerationResult(BaseModel):
    """Base class for generation results"""

    success: bool
    provider: str
    model: str
    cost_usd: Decimal
    generation_time_seconds: int
    request_id: Optional[str] = None
    error: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: str,
        }


class ImageResult(GenerationResult):
    """Result from image generation"""

    image_url: str
    image_path: Optional[str] = None  # Local path after download
    width: int
    height: int
    content_hash: Optional[str] = None


class VideoResult(GenerationResult):
    """Result from video animation"""

    video_url: str
    video_path: Optional[str] = None  # Local path after download
    duration: float
    fps: int
    content_hash: Optional[str] = None


class AudioResult(GenerationResult):
    """Result from audio synthesis"""

    audio_url: Optional[str] = None
    audio_path: Optional[str] = None  # Local path
    duration_seconds: float
    content_hash: Optional[str] = None


class CompletedShot(BaseModel):
    """A fully generated shot with all assets"""

    shot_config: ShotConfig
    image_result: ImageResult
    video_result: VideoResult
    audio_result: Optional[AudioResult] = None

    total_cost_usd: Decimal
    total_time_seconds: int

    class Config:
        json_encoders = {
            Decimal: str,
        }


# ============================================================================
# Asset Metadata Models
# ============================================================================


class AssetMetadata(BaseModel):
    """
    Rich metadata for generated assets.
    Enables multi-dimensional querying and discovery.
    """

    asset_id: str
    asset_type: Literal["image", "video", "audio"]
    content_hash: str = Field(..., description="Hash of generation parameters")
    file_path: str

    # Categorization (for asset discovery)
    characters: List[str] = Field(default_factory=list)
    landscapes: List[str] = Field(default_factory=list)
    styles: List[str] = Field(default_factory=list)
    mood: Optional[str] = None
    time_of_day: Optional[str] = None
    shot_type: Optional[str] = None

    # Generation parameters (for reproducibility)
    prompt: str
    negative_prompt: Optional[str] = None
    provider: str
    model: str
    config: Dict[str, Any] = Field(default_factory=dict)

    # Cost tracking
    cost_usd: Decimal
    generation_time_seconds: int

    # Usage tracking
    created_at: datetime = Field(default_factory=datetime.now)
    used_in_projects: List[str] = Field(default_factory=list, description="Project IDs that used this asset")
    reuse_count: int = Field(default=0, description="Number of times reused")

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat(),
        }

    def mark_used(self, project_id: str):
        """Mark asset as used in a project"""
        if project_id not in self.used_in_projects:
            self.used_in_projects.append(project_id)
        self.reuse_count += 1


# ============================================================================
# Project Models
# ============================================================================


class FilmProject(BaseModel):
    """
    A complete film generation project.
    Contains all shots and aggregated metadata.
    """

    project_id: str
    name: str
    description: Optional[str] = None

    # Shots
    shot_configs: List[ShotConfig]
    completed_shots: List[CompletedShot] = Field(default_factory=list)

    # Status
    status: Literal["pending", "generating", "completed", "failed"] = "pending"

    # Costs
    estimated_cost_usd: Optional[Decimal] = None
    actual_cost_usd: Decimal = Field(default=Decimal("0"))
    budget_limit_usd: Optional[Decimal] = None

    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Output
    final_film_path: Optional[str] = None

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat(),
        }

    def add_completed_shot(self, shot: CompletedShot):
        """Add a completed shot and update costs"""
        self.completed_shots.append(shot)
        self.actual_cost_usd += shot.total_cost_usd

    def check_budget(self) -> bool:
        """Check if within budget"""
        if not self.budget_limit_usd:
            return True
        return self.actual_cost_usd <= self.budget_limit_usd

    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if not self.shot_configs:
            return 0.0
        return (len(self.completed_shots) / len(self.shot_configs)) * 100


# ============================================================================
# Cost Estimation Models
# ============================================================================


class ShotCostEstimate(BaseModel):
    """Cost estimate for a single shot"""

    shot_id: str
    image_cost: Decimal
    video_cost: Decimal
    audio_cost: Decimal
    total_cost: Decimal

    class Config:
        json_encoders = {
            Decimal: str,
        }


class CostEstimate(BaseModel):
    """
    Complete cost estimate for a film project.
    Calculated before generation starts.
    """

    project_id: str
    shot_estimates: List[ShotCostEstimate]
    total_estimated_cost: Decimal
    budget_limit: Optional[Decimal] = None
    within_budget: bool = True

    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat(),
        }
