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
    """
    return {
        "models": [
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "description": "Best for creative writing and detailed content",
                "tier": "premium"
            },
            {
                "id": "anthropic/claude-3-opus",
                "name": "Claude 3 Opus",
                "description": "Most capable model for complex tasks",
                "tier": "premium"
            },
            {
                "id": "openai/gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Latest GPT-4 with 128k context",
                "tier": "premium"
            },
            {
                "id": "openai/gpt-4o",
                "name": "GPT-4o",
                "description": "Optimized for creative writing",
                "tier": "premium"
            },
            {
                "id": "google/gemini-pro-1.5",
                "name": "Gemini Pro 1.5",
                "description": "Google's most capable model",
                "tier": "standard"
            },
            {
                "id": "meta-llama/llama-3.1-70b-instruct",
                "name": "Llama 3.1 70B",
                "description": "Open-source, fast and capable",
                "tier": "budget"
            },
            {
                "id": "mistralai/mistral-large",
                "name": "Mistral Large",
                "description": "European model, excellent quality",
                "tier": "standard"
            }
        ]
    }
