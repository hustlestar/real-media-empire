"""
Core data models for PowerPoint presentation generation.

Uses Pydantic for validation and serialization.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================


class SlideLayout(str, Enum):
    """Available slide layout types"""

    TITLE = "title"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    IMAGE_TEXT = "image_text"
    BLANK = "blank"
    SECTION_HEADER = "section_header"


class ToneType(str, Enum):
    """Presentation tone options"""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    MOTIVATIONAL = "motivational"
    EDUCATIONAL = "educational"
    SALES = "sales"
    TECHNICAL = "technical"


class AspectRatio(str, Enum):
    """Presentation aspect ratios"""

    RATIO_4_3 = "4:3"
    RATIO_16_9 = "16:9"


class ListType(str, Enum):
    """List formatting types"""

    BULLET = "bullet"
    NUMBERED = "numbered"


# ============================================================================
# Request Models
# ============================================================================


class PresentationRequest(BaseModel):
    """Input request for generating a presentation"""

    presentation_id: str = Field(..., description="Unique identifier for this presentation")
    topic: str = Field(..., min_length=3, description="Main topic or title")
    brief: Optional[str] = Field(None, description="Detailed description or brief")
    target_audience: Optional[str] = Field(None, description="Target audience (e.g., 'executives', 'students')")
    num_slides: int = Field(default=10, ge=3, le=50, description="Target number of slides")
    tone: ToneType = Field(default=ToneType.PROFESSIONAL, description="Presentation tone")
    key_points: Optional[List[str]] = Field(default=None, description="Specific points to cover")
    additional_instructions: Optional[str] = Field(None, description="Additional instructions for AI content generation")
    reference_content: Optional[str] = Field(None, description="Reference text/content to base the presentation on")
    include_title_slide: bool = Field(default=True, description="Include title slide")
    include_conclusion: bool = Field(default=True, description="Include conclusion slide")


class PresentationConfig(BaseModel):
    """Configuration for presentation generation"""

    aspect_ratio: AspectRatio = Field(default=AspectRatio.RATIO_16_9)
    template_path: Optional[str] = Field(default=None, description="Path to custom PPTX template")

    # Style settings (used when creating template from scratch)
    theme_name: str = Field(default="professional", description="Theme name for generated template")
    font_family: str = Field(default="Calibri", description="Primary font family")
    title_font_size: int = Field(default=44, ge=20, le=80)
    body_font_size: int = Field(default=24, ge=10, le=40)

    # Color scheme (hex colors)
    primary_color: str = Field(default="#1F4E78", pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary_color: str = Field(default="#2E75B6", pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: str = Field(default="#FFC000", pattern=r"^#[0-9A-Fa-f]{6}$")
    text_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    background_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")

    # Content settings
    max_bullets_per_slide: int = Field(default=5, ge=3, le=10)
    max_chars_per_bullet: int = Field(default=100, ge=50, le=300)
    enable_speaker_notes: bool = Field(default=True)

    # Layout dimensions (in inches)
    header_height: float = Field(default=1.0, ge=0.5, le=2.0, description="Header section height")
    footer_height: float = Field(default=0.5, ge=0.3, le=1.0, description="Footer section height")
    margin: float = Field(default=0.5, ge=0.1, le=1.0, description="Slide margins")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return self.model_dump()


# ============================================================================
# Content Models
# ============================================================================


class BulletPoint(BaseModel):
    """A single bullet point with optional indentation"""

    text: str = Field(..., min_length=1, max_length=500)
    level: int = Field(default=0, ge=0, le=2, description="Indentation level (0=main, 1=sub, 2=sub-sub)")
    list_type: ListType = Field(default=ListType.BULLET, description="Bullet or numbered list")


class SlideContent(BaseModel):
    """Content for a single slide"""

    title: str = Field(..., min_length=1, max_length=200)
    bullets: List[BulletPoint] = Field(default_factory=list)
    text_content: Optional[str] = Field(None, description="For non-bullet content")
    speaker_notes: Optional[str] = Field(None, description="Speaker notes for this slide")
    image_placeholder: Optional[str] = Field(None, description="Description of image to include")


class SlideDefinition(BaseModel):
    """
    Complete definition of a single slide.
    Generated by AI content provider.
    """

    slide_number: int = Field(..., ge=1)
    layout_type: SlideLayout = Field(default=SlideLayout.CONTENT)
    content: SlideContent

    # Metadata for caching and reuse
    tags: List[str] = Field(default_factory=list, description="Categorization tags")


class PresentationOutline(BaseModel):
    """
    High-level structure of the presentation.
    Generated first by AI before detailed content.
    """

    title: str
    subtitle: Optional[str] = None
    slide_titles: List[str] = Field(..., description="Title for each slide in order")
    estimated_duration_minutes: Optional[int] = Field(None, ge=1, le=180)

    def get_num_slides(self) -> int:
        """Get total number of slides"""
        return len(self.slide_titles)


# ============================================================================
# Result Models
# ============================================================================


class PresentationResult(BaseModel):
    """Result of presentation generation"""

    presentation_id: str
    file_path: str = Field(..., description="Path to generated PPTX file")
    slide_count: int = Field(..., ge=1)

    # Cost tracking
    cost_usd: Decimal = Field(default=Decimal("0.00"))
    tokens_used: int = Field(default=0)
    provider: str = Field(default="openai")
    model_used: str = Field(default="gpt-4")

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    cache_hit: bool = Field(default=False, description="Whether cached content was reused")

    # Content summary
    outline: PresentationOutline
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentGenerationResult(BaseModel):
    """Result from AI content generation step"""

    slides: List[SlideDefinition]
    outline: PresentationOutline
    tokens_used: int = Field(default=0)
    cost_usd: Decimal = Field(default=Decimal("0.00"))
    model_used: str
