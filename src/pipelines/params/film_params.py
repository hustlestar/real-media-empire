"""
Parameters for film generation pipeline.

Uses Pydantic BaseModel instead of deprecated ZenML BaseParameters.
"""

import logging
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field

from util.time import get_now

logger = logging.getLogger(__name__)


class FilmPipelineParams(BaseModel):
    """
    Parameters for film generation pipeline.

    Note: Uses Pydantic BaseModel instead of ZenML's deprecated BaseParameters.
    """

    # ========================================================================
    # Project Identification
    # ========================================================================

    film_id: str = Field(..., description="Unique identifier for this film project")

    execution_date: str = Field(default_factory=get_now, description="Execution timestamp")

    # ========================================================================
    # Input
    # ========================================================================

    shots_json_path: str = Field(..., description="Path to JSON file containing shot definitions")

    # ========================================================================
    # Provider Selection (Defaults)
    # ========================================================================

    default_image_provider: Literal["fal", "replicate"] = Field(default="fal", description="Default image generation provider")

    default_video_provider: Literal["minimax", "kling", "runway"] = Field(
        default="minimax", description="Default video generation provider (minimax=cheap, kling=premium)"
    )

    default_audio_provider: Literal["openai", "elevenlabs"] = Field(
        default="openai", description="Default audio synthesis provider (openai=cheap, elevenlabs=premium)"
    )

    # ========================================================================
    # Cost Controls
    # ========================================================================

    budget_limit_usd: Optional[Decimal] = Field(default=None, description="Maximum budget for this generation run (None=unlimited)")

    use_cache: bool = Field(default=True, description="Enable asset caching to save costs")

    # ========================================================================
    # Quality Settings
    # ========================================================================

    image_width: int = Field(default=1024, ge=512, le=2048, description="Default image width")

    image_height: int = Field(default=576, ge=512, le=2048, description="Default image height (576 for 16:9)")

    inference_steps: int = Field(default=28, ge=1, le=100, description="Number of inference steps for image generation")

    guidance_scale: float = Field(default=3.5, ge=1.0, le=20.0, description="Guidance scale for image generation")

    # ========================================================================
    # Output
    # ========================================================================

    output_dir: Optional[str] = Field(default=None, description="Output directory (defaults to FILM_GALLERY_DIR/projects/{film_id})")

    save_intermediate: bool = Field(default=True, description="Save intermediate assets (images, videos) per shot")

    # ========================================================================
    # API Keys (loaded from env)
    # ========================================================================

    fal_api_key: Optional[str] = Field(default=None, description="FAL API key (from env FAL_API_KEY)")

    replicate_api_key: Optional[str] = Field(default=None, description="Replicate API key (from env REPLICATE_API_KEY)")

    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key (from env OPENAI_API_KEY)")

    elevenlabs_api_key: Optional[str] = Field(default=None, description="ElevenLabs API key (from env ELEVENLABS_API_KEY)")

    class Config:
        json_encoders = {
            Decimal: str,
        }

    def get_api_keys_dict(self) -> dict:
        """Get API keys as dictionary for provider initialization"""
        return {
            "fal": self.fal_api_key,
            "replicate": self.replicate_api_key,
            "openai": self.openai_api_key,
            "elevenlabs": self.elevenlabs_api_key,
        }


def create_film_params_from_cli(film_id: str, shots_json_path: str, budget_limit: Optional[float] = None, **kwargs) -> FilmPipelineParams:
    """
    Create FilmPipelineParams from CLI arguments.

    Helper function for CLI integration.
    """
    # Load API keys from environment
    from config import CONFIG

    params = FilmPipelineParams(
        film_id=film_id,
        shots_json_path=shots_json_path,
        budget_limit_usd=Decimal(str(budget_limit)) if budget_limit else None,
        fal_api_key=CONFIG.get("FAL_API_KEY"),
        replicate_api_key=CONFIG.get("REPLICATE_API_KEY"),
        openai_api_key=CONFIG.get("OPEN_AI_API_KEY"),
        elevenlabs_api_key=CONFIG.get("ELEVENLABS_API_KEY"),
        **kwargs,
    )

    logger.info(f"Created film pipeline params for: {film_id}")
    return params
