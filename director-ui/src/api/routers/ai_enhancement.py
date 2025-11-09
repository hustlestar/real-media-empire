"""
AI Enhancement API Router

Provides AI-powered enhancement for form fields using OpenRouter API.
Supports multiple AI models for creative writing and content generation.
"""

import os
import httpx
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class AIEnhanceRequest(BaseModel):
    """Request for AI enhancement."""
    model: str = Field(..., description="OpenRouter model ID (e.g., 'anthropic/claude-3.5-sonnet')")
    system_prompt: str = Field(..., description="System prompt for the AI")
    user_prompt: str = Field(..., description="User prompt with content to enhance")
    field_name: str = Field(..., description="Name of the field being enhanced")
    form_data: Dict[str, Any] = Field(default_factory=dict, description="Current form data for context")
    max_tokens: Optional[int] = Field(default=2000, description="Maximum tokens in response")
    temperature: Optional[float] = Field(default=0.7, description="Temperature for generation (0.0-1.0)")


class AIEnhanceResponse(BaseModel):
    """Response from AI enhancement."""
    enhanced_text: str = Field(..., description="AI-enhanced or generated text")
    model: str = Field(..., description="Model used for enhancement")
    tokens_used: Optional[int] = Field(default=None, description="Estimated tokens used")


@router.post("/enhance", response_model=AIEnhanceResponse)
async def enhance_with_ai(request: AIEnhanceRequest) -> AIEnhanceResponse:
    """
    Enhance form field content using AI via OpenRouter.

    This endpoint supports multiple AI models and provides context-aware
    enhancement for creative writing tasks.
    """

    # Get OpenRouter API key from environment
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY not configured. Please set it in .env file."
        )

    # Prepare OpenRouter API request
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://media-empire.local",  # Optional, for rankings
        "X-Title": "Media Empire Director UI"  # Optional, shows in rankings
    }

    payload = {
        "model": request.model,
        "messages": [
            {
                "role": "system",
                "content": request.system_prompt
            },
            {
                "role": "user",
                "content": request.user_prompt
            }
        ],
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
    }

    try:
        # Call OpenRouter API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                openrouter_url,
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", error_detail)
                except:
                    pass

                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenRouter API error: {error_detail}"
                )

            result = response.json()

            # Extract enhanced text from response
            enhanced_text = result["choices"][0]["message"]["content"].strip()

            # Extract token usage if available
            tokens_used = None
            if "usage" in result:
                tokens_used = result["usage"].get("total_tokens")

            return AIEnhanceResponse(
                enhanced_text=enhanced_text,
                model=request.model,
                tokens_used=tokens_used
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AI enhancement request timed out. Please try again."
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to OpenRouter API: {str(e)}"
        )
    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected response format from OpenRouter API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI enhancement failed: {str(e)}"
        )


@router.get("/models")
async def list_available_models():
    """
    List available AI models for enhancement.

    Returns the same model list used in the frontend AIEnhancer component.
    Optimized for text/blog/post writing with cost-effective options.
    """
    return {
        "models": [
            # Quality Tier - Best for polished, refined content
            {
                "id": "google/gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "description": "Best all-around for blog posts and scripts with built-in reasoning",
                "tier": "quality",
                "pricing": "~$0.70 input / $2.10 output per million tokens"
            },
            {
                "id": "qwen/qwen3-235b-a22b-instruct",
                "name": "Qwen 3 235B",
                "description": "Excellent for technical content and detailed analysis",
                "tier": "quality",
                "pricing": "~$0.40-0.80 per million tokens"
            },
            {
                "id": "meta-llama/llama-4-maverick",
                "name": "Llama 4 Maverick",
                "description": "Strong at diverse content types with multimodal capabilities",
                "tier": "quality",
                "pricing": "~$0.24 input / $0.97 output per million tokens"
            },

            # Mid-Range Tier - Best balance of quality and cost
            {
                "id": "mistralai/mistral-medium-3.1",
                "name": "Mistral Medium 3.1",
                "description": "Enterprise quality at budget pricing, great for creative writing",
                "tier": "standard",
                "pricing": "$0.10 input / $0.30 output per million tokens"
            },

            # Budget Tier - Ultra-cheap for high volume
            {
                "id": "deepseek/deepseek-chat-v3-0324",
                "name": "DeepSeek Chat V3",
                "description": "Best cheap option, strong reasoning and technical content",
                "tier": "budget",
                "pricing": "~$0.27 input / $1.10 output per million tokens"
            },
            {
                "id": "google/gemini-2.5-flash-lite",
                "name": "Gemini 2.5 Flash Lite",
                "description": "Ultra-low latency for batch processing and high-volume generation",
                "tier": "budget",
                "pricing": "$0.10 input / $0.40 output per million tokens"
            }
        ]
    }
