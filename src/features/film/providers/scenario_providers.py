"""
Scenario providers for generating shot definitions from text descriptions.

Uses LLMs via OpenRouter to create high-quality cinematic shot sequences.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Literal
from decimal import Decimal
import json
import httpx
from pydantic import BaseModel

from film.models import ShotDefinition
from config import CONFIG


class ScenarioRequest(BaseModel):
    """Request for scenario generation."""

    description: str
    num_shots: int = 5
    style: Optional[str] = None
    mood: Optional[str] = None
    duration_per_shot: int = 5
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = "16:9"


class ScenarioResult(BaseModel):
    """Result from scenario generation."""

    shots: List[ShotDefinition]
    scenario_summary: str
    estimated_duration: int
    provider: str
    model: str
    cost_usd: Decimal


class BaseScenarioProvider(ABC):
    """Base class for scenario generation providers."""

    @abstractmethod
    async def generate_scenario(self, request: ScenarioRequest, model: Optional[str] = None) -> ScenarioResult:
        """Generate shot definitions from scenario description."""
        pass

    @abstractmethod
    def estimate_cost(self, request: ScenarioRequest, model: Optional[str] = None) -> Decimal:
        """Estimate cost for scenario generation."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their capabilities."""
        pass


class OpenRouterScenarioProvider(BaseScenarioProvider):
    """
    OpenRouter-based scenario generation.

    Supports multiple LLM models for flexible quality/cost tradeoffs.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    # Model presets with costs (per million tokens)
    MODELS = {
        # Premium tier - Best quality
        "claude-3.5-sonnet": {
            "id": "anthropic/claude-3.5-sonnet",
            "input_cost": Decimal("3.00"),
            "output_cost": Decimal("15.00"),
            "context": 200000,
            "description": "Best quality, excellent at creative writing",
        },
        "gpt-4-turbo": {
            "id": "openai/gpt-4-turbo",
            "input_cost": Decimal("10.00"),
            "output_cost": Decimal("30.00"),
            "context": 128000,
            "description": "High quality, good creative output",
        },
        # Balanced tier - Good quality, reasonable cost
        "claude-3-haiku": {
            "id": "anthropic/claude-3-haiku",
            "input_cost": Decimal("0.25"),
            "output_cost": Decimal("1.25"),
            "context": 200000,
            "description": "Fast and cheap, decent quality",
        },
        "gpt-3.5-turbo": {
            "id": "openai/gpt-3.5-turbo",
            "input_cost": Decimal("0.50"),
            "output_cost": Decimal("1.50"),
            "context": 16000,
            "description": "Good balance of speed and quality",
        },
        # Budget tier - Maximum value
        "llama-3.1-70b": {
            "id": "meta-llama/llama-3.1-70b-instruct",
            "input_cost": Decimal("0.35"),
            "output_cost": Decimal("0.40"),
            "context": 131000,
            "description": "Open source, very cost effective",
        },
        "gemini-pro": {
            "id": "google/gemini-pro",
            "input_cost": Decimal("0.125"),
            "output_cost": Decimal("0.375"),
            "context": 32000,
            "description": "Cheap and fast",
        },
    }

    # Default model from environment or fallback
    DEFAULT_MODEL = "claude-3-haiku"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key (or from CONFIG)
        """
        self.api_key = api_key or CONFIG.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/media-empire",
                "X-Title": "Media Empire Film Generator",
            },
            timeout=120.0,
        )

    def _get_system_prompt(self, request: ScenarioRequest) -> str:
        """Generate system prompt for scenario generation."""
        return f"""You are an expert cinematographer and film director. Your task is to break down a scene description into detailed cinematic shots.

For each shot, you must provide:
1. Shot type (wide, medium, close-up, extreme-close-up)
2. Enhanced visual prompt with cinematic details (8K, professional color grading, lighting, mood)
3. Negative prompt (things to avoid)
4. Duration in seconds
5. Optional dialogue
6. Characters present
7. Landscape/location types
8. Visual styles
9. Mood/emotion
10. Time of day

Follow these cinematography principles:
- Start with establishing shots (wide)
- Use shot variety for visual interest
- Include extreme close-ups for dramatic emphasis
- Consider the 180-degree rule
- Think about lighting and composition
- Add cinematic details (film grain, depth of field, color grading)

Aspect ratio: {request.aspect_ratio}
Default shot duration: {request.duration_per_shot}s
Overall style: {request.style or 'cinematic realism'}
Overall mood: {request.mood or 'dramatic'}

Output ONLY valid JSON matching this structure:
{{
  "scenario_summary": "Brief summary of the scene",
  "shots": [
    {{
      "shot_id": "shot_001",
      "shot_number": 1,
      "shot_type": "wide",
      "enhanced_prompt": "8K cinematic...",
      "negative_prompt": "cartoon, anime...",
      "duration": 5,
      "dialogue": null,
      "characters": ["character_name"],
      "landscapes": ["location_type"],
      "styles": ["cinematic", "style_tags"],
      "mood": "emotional_tone",
      "time_of_day": "afternoon"
    }}
  ]
}}"""

    def _get_user_prompt(self, request: ScenarioRequest) -> str:
        """Generate user prompt with scenario description."""
        return f"""Create {request.num_shots} cinematic shots for this scene:

{request.description}

Remember:
- Make prompts VERY detailed and cinematic
- Include technical details (8K, color grading, lighting)
- Specify camera angles and movements
- Add atmosphere and mood descriptors
- Use negative prompts to exclude unwanted elements
- Ensure shot variety and proper coverage
- Consider the emotional arc of the scene"""

    async def generate_scenario(self, request: ScenarioRequest, model: Optional[str] = None) -> ScenarioResult:
        """
        Generate shot definitions from scenario description.

        Args:
            request: Scenario generation request
            model: Model key (e.g., 'claude-3.5-sonnet') or None for default

        Returns:
            ScenarioResult with generated shots
        """
        # Get model configuration
        model_key = model or CONFIG.get("SCENARIO_DEFAULT_MODEL") or self.DEFAULT_MODEL
        if model_key not in self.MODELS:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(self.MODELS.keys())}")

        model_config = self.MODELS[model_key]
        model_id = model_config["id"]

        # Build API request
        system_prompt = self._get_system_prompt(request)
        user_prompt = self._get_user_prompt(request)

        payload = {
            "model": model_id,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            "temperature": 0.7,
            "max_tokens": 4000,
            "response_format": {"type": "json_object"},
        }

        # Make API call
        response = await self.client.post(f"{self.BASE_URL}/chat/completions", json=payload)
        response.raise_for_status()

        result = response.json()

        # Parse response
        content = result["choices"][0]["message"]["content"]
        scenario_data = json.loads(content)

        # Convert to ShotDefinition objects
        shots = [ShotDefinition(**shot_data) for shot_data in scenario_data["shots"]]

        # Calculate cost
        usage = result.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        cost = (Decimal(str(input_tokens)) / 1_000_000) * model_config["input_cost"] + (Decimal(str(output_tokens)) / 1_000_000) * model_config[
            "output_cost"
        ]

        return ScenarioResult(
            shots=shots,
            scenario_summary=scenario_data.get("scenario_summary", request.description),
            estimated_duration=sum(shot.duration for shot in shots),
            provider="openrouter",
            model=model_id,
            cost_usd=cost,
        )

    def estimate_cost(self, request: ScenarioRequest, model: Optional[str] = None) -> Decimal:
        """
        Estimate cost for scenario generation.

        Args:
            request: Scenario generation request
            model: Model key or None for default

        Returns:
            Estimated cost in USD
        """
        model_key = model or CONFIG.get("SCENARIO_DEFAULT_MODEL") or self.DEFAULT_MODEL
        if model_key not in self.MODELS:
            raise ValueError(f"Unknown model: {model_key}")

        model_config = self.MODELS[model_key]

        # Estimate tokens (rough approximation)
        # System prompt: ~800 tokens
        # User prompt: ~200 + description length
        # Output: ~200 tokens per shot

        estimated_input = 800 + 200 + len(request.description.split()) * 1.3
        estimated_output = request.num_shots * 200

        cost = (Decimal(str(estimated_input)) / 1_000_000) * model_config["input_cost"] + (Decimal(str(estimated_output)) / 1_000_000) * model_config[
            "output_cost"
        ]

        return cost

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their capabilities."""
        return [
            {
                "key": key,
                "id": config["id"],
                "description": config["description"],
                "cost_per_1k_output_tokens": float(config["output_cost"]) / 1000,
                "context_window": config["context"],
            }
            for key, config in self.MODELS.items()
        ]

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()


class LocalLLMScenarioProvider(BaseScenarioProvider):
    """
    Local LLM scenario generation (e.g., Ollama, LM Studio).

    For offline or privacy-focused scenario generation.
    """

    def __init__(self, base_url: Optional[str] = None, model: str = "llama3.1:70b"):
        """
        Initialize local LLM provider.

        Args:
            base_url: Local LLM API endpoint (e.g., http://localhost:11434)
            model: Model name
        """
        self.base_url = base_url or CONFIG.get("LOCAL_LLM_BASE_URL", "http://localhost:11434")
        self.default_model = model
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate_scenario(self, request: ScenarioRequest, model: Optional[str] = None) -> ScenarioResult:
        """Generate scenario using local LLM."""
        # Similar implementation to OpenRouter but for local API
        raise NotImplementedError("Local LLM provider coming soon")

    def estimate_cost(self, request: ScenarioRequest, model: Optional[str] = None) -> Decimal:
        """Local LLMs are free."""
        return Decimal("0.00")

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available local models."""
        return [{"key": "llama3.1-70b", "description": "Local Llama 3.1 70B", "cost_per_1k_output_tokens": 0.0, "context_window": 131000}]


# Provider registry
SCENARIO_PROVIDER_REGISTRY = {
    "openrouter": OpenRouterScenarioProvider,
    "local": LocalLLMScenarioProvider,
}


def create_scenario_provider(provider_type: str = "openrouter", **kwargs) -> BaseScenarioProvider:
    """
    Factory function to create scenario providers.

    Args:
        provider_type: Type of provider ('openrouter', 'local')
        **kwargs: Provider-specific arguments

    Returns:
        Configured scenario provider
    """
    if provider_type not in SCENARIO_PROVIDER_REGISTRY:
        raise ValueError(f"Unknown scenario provider: {provider_type}. " f"Available: {list(SCENARIO_PROVIDER_REGISTRY.keys())}")

    return SCENARIO_PROVIDER_REGISTRY[provider_type](**kwargs)
