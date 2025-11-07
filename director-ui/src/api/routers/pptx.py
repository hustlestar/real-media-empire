"""
PPTX Generation API routes - PowerPoint generation with content integration.
Integrates with YouTube transcriber, web scraper, and AI generation.
"""

import logging
from typing import Optional
from pathlib import Path
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Import PPTX generation system
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from pptx_gen.generator import PresentationGenerator
from pptx_gen.models import PresentationRequest, PresentationConfig, ToneType
from pptx_gen.cost_tracker import CostTracker
from decimal import Decimal

# Import content processors
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from processors.youtube_processor import YouTubeProcessor
from processors.web_scraper import WebScraperProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pptx", tags=["pptx"])


# ============================================================================
# Request/Response Models
# ============================================================================

class EstimateCostRequest(BaseModel):
    """Request to estimate generation cost."""
    content_source: str = Field(..., description="Source type: ai, youtube, web, file")
    topic: Optional[str] = Field(None, description="Topic for AI generation")
    num_slides: int = Field(10, ge=1, le=50, description="Number of slides")
    model: str = Field("gpt-4o-mini", description="Model to use")


class GenerateOutlineRequest(BaseModel):
    """Request to generate presentation outline."""
    content_source: str
    topic: Optional[str] = None
    brief: Optional[str] = None
    youtube_url: Optional[str] = None
    web_url: Optional[str] = None
    num_slides: int = 10
    tone: str = "professional"
    model: str = "gpt-4o-mini"


# ============================================================================
# Cost Estimation Endpoint
# ============================================================================

@router.post("/estimate-cost")
async def estimate_cost(request: EstimateCostRequest):
    """
    Estimate cost for PPTX generation.

    Returns estimated cost in USD based on content source, slides, and model.
    """
    try:
        # Base token estimates per slide
        tokens_per_slide = {
            "ai": 500,  # Generate from scratch
            "youtube": 300,  # From transcript
            "web": 300,  # From scraped content
            "file": 200  # From provided text
        }

        # Model pricing (per 1K tokens)
        model_pricing = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }

        base_tokens = tokens_per_slide.get(request.content_source, 400)
        total_tokens = base_tokens * request.num_slides

        pricing = model_pricing.get(request.model, model_pricing["gpt-4o-mini"])

        # Estimate input and output tokens (rough 60/40 split)
        input_tokens = total_tokens * 0.6
        output_tokens = total_tokens * 0.4

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        estimated_cost = input_cost + output_cost

        return {
            "estimated_cost": round(estimated_cost, 4),
            "breakdown": {
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "input_cost": round(input_cost, 4),
                "output_cost": round(output_cost, 4)
            },
            "model": request.model,
            "num_slides": request.num_slides
        }

    except Exception as e:
        logger.error(f"Error estimating cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Outline Generation Endpoint
# ============================================================================

@router.post("/generate-outline")
async def generate_outline(request: GenerateOutlineRequest):
    """
    Generate presentation outline preview.

    Fetches content from source and creates outline without full generation.
    """
    try:
        content = ""
        title = request.topic or "Presentation"

        # Fetch content based on source
        if request.content_source == "youtube" and request.youtube_url:
            logger.info(f"Fetching YouTube content: {request.youtube_url}")
            processor = YouTubeProcessor()
            result = await processor.process_youtube_url(request.youtube_url)
            content = result.get("transcript", "")
            title = result.get("title", title)

        elif request.content_source == "web" and request.web_url:
            logger.info(f"Scraping web content: {request.web_url}")
            result = await WebScraperProcessor.extract_content_from_url(request.web_url)
            if result:
                content = result.get("content", "")
                title = result.get("title", title)
            else:
                content = ""

        elif request.content_source == "ai":
            content = f"Topic: {request.topic}\n\nBrief: {request.brief or 'No additional context provided'}"

        # Generate outline using OpenAI
        from openai import AsyncOpenAI
        from config import CONFIG

        client = AsyncOpenAI(api_key=CONFIG.get("OPEN_AI_API_KEY"))

        prompt = f"""Create a presentation outline with {request.num_slides} slides.

Title: {title}
Tone: {request.tone}

Content:
{content[:4000]}  # Limit to avoid token limits

Generate a structured outline with:
- Presentation title
- {request.num_slides} slide titles
- 3-5 bullet points per slide

Format as JSON:
{{
  "title": "Presentation Title",
  "slides": [
    {{"title": "Slide 1 Title", "bullets": ["Point 1", "Point 2", "Point 3"]}},
    ...
  ]
}}
"""

        response = await client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "system", "content": "You are a professional presentation designer."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        import json
        outline = json.loads(response.choices[0].message.content)

        return {
            "outline": outline,
            "source": request.content_source,
            "content_length": len(content)
        }

    except Exception as e:
        logger.error(f"Error generating outline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Full Generation Endpoint
# ============================================================================

@router.post("/generate")
async def generate_presentation(
    presentation_id: str = Form(...),
    content_source: str = Form(...),
    topic: Optional[str] = Form(None),
    brief: Optional[str] = Form(None),
    num_slides: int = Form(10),
    tone: str = Form("professional"),
    target_audience: Optional[str] = Form(None),
    model: str = Form("gpt-4o-mini"),
    budget_limit: Optional[float] = Form(None),
    youtube_url: Optional[str] = Form(None),
    web_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    ai_enhance: bool = Form(False)
):
    """
    Generate complete PowerPoint presentation.

    Supports multiple content sources:
    - AI: Generate from topic and brief
    - YouTube: Extract transcript and generate from video
    - Web: Scrape website and generate from content
    - File: Generate from uploaded text file
    """
    try:
        logger.info(f"Generating presentation: {presentation_id} from {content_source}")

        # Prepare content based on source
        reference_content = None
        actual_topic = topic or "Presentation"

        if content_source == "youtube" and youtube_url:
            logger.info(f"Processing YouTube URL: {youtube_url}")
            processor = YouTubeProcessor()
            result = await processor.process_youtube_url(youtube_url)
            reference_content = result.get("transcript", "")
            actual_topic = result.get("title", actual_topic)

        elif content_source == "web" and web_url:
            logger.info(f"Scraping web URL: {web_url}")
            result = await WebScraperProcessor.extract_content_from_url(web_url)
            if result:
                reference_content = result.get("content", "")
                actual_topic = result.get("title", actual_topic)
            else:
                reference_content = ""

        elif content_source == "file" and file:
            logger.info(f"Reading uploaded file: {file.filename}")
            content_bytes = await file.read()
            reference_content = content_bytes.decode('utf-8')

        # Create PPTX generation request
        pptx_request = PresentationRequest(
            presentation_id=presentation_id,
            topic=actual_topic,
            brief=brief,
            num_slides=num_slides,
            tone=ToneType(tone),
            target_audience=target_audience,
            reference_content=reference_content
        )

        # Create config and cost tracker
        config = PresentationConfig()
        cost_tracker = CostTracker(
            budget_limit=Decimal(str(budget_limit)) if budget_limit else None
        )

        # Create generator
        output_dir = "./presentations"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        generator = PresentationGenerator(
            config=config,
            cost_tracker=cost_tracker,
            output_dir=output_dir
        )

        # Generate presentation
        result = generator.generate(pptx_request, model=model)

        logger.info(f"Presentation generated: {result.file_path}")

        return {
            "file_path": str(result.file_path),
            "slide_count": result.slide_count,
            "cost_usd": float(result.cost_usd),
            "model_used": result.model_used,
            "cache_hit": result.cache_hit,
            "presentation_id": presentation_id
        }

    except Exception as e:
        logger.error(f"Error generating presentation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Download Endpoint
# ============================================================================

@router.get("/download/{presentation_id}")
async def download_presentation(presentation_id: str):
    """Download generated presentation file."""
    try:
        # Find the file
        output_dir = Path("./presentations")
        files = list(output_dir.glob(f"{presentation_id}*.pptx"))

        if not files:
            raise HTTPException(status_code=404, detail="Presentation not found")

        file_path = files[0]

        return FileResponse(
            path=str(file_path),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=file_path.name
        )

    except Exception as e:
        logger.error(f"Error downloading presentation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# List Presentations Endpoint
# ============================================================================

@router.get("/presentations")
async def list_presentations(limit: int = 50, offset: int = 0):
    """List all generated presentations."""
    try:
        output_dir = Path("./presentations")

        if not output_dir.exists():
            return {"presentations": [], "total": 0}

        files = sorted(output_dir.glob("*.pptx"), key=lambda x: x.stat().st_mtime, reverse=True)

        presentations = []
        for file_path in files[offset:offset+limit]:
            stat = file_path.stat()
            presentations.append({
                "filename": file_path.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime
            })

        return {
            "presentations": presentations,
            "total": len(files),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error listing presentations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Delete Presentation Endpoint
# ============================================================================

@router.delete("/presentations/{presentation_id}")
async def delete_presentation(presentation_id: str):
    """Delete a generated presentation."""
    try:
        output_dir = Path("./presentations")
        files = list(output_dir.glob(f"{presentation_id}*.pptx"))

        if not files:
            raise HTTPException(status_code=404, detail="Presentation not found")

        for file_path in files:
            file_path.unlink()

        return {"message": f"Deleted {len(files)} file(s)"}

    except Exception as e:
        logger.error(f"Error deleting presentation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
