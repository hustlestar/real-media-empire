"""
Audio synthesis provider implementations.

Supports:
- OpenAI TTS (cheap: $0.015/1K chars)
- ElevenLabs (premium: $0.30/1K chars)
"""

import logging
import time
from decimal import Decimal
from typing import Optional

import httpx

from film.models import AudioConfig, AudioResult
from film.providers.base import (
    BaseAudioProvider,
    ProviderError,
    ProviderAuthError,
)

logger = logging.getLogger(__name__)


# ============================================================================
# OpenAI TTS Provider
# ============================================================================


class OpenAIAudioProvider(BaseAudioProvider):
    """
    OpenAI Text-to-Speech provider.

    Fast and affordable voice synthesis.
    Cost: $0.015 per 1K characters
    Models: tts-1 (fast), tts-1-hd (higher quality)
    """

    BASE_URL = "https://api.openai.com/v1/audio/speech"
    COST_PER_1K_CHARS = Decimal("0.015")

    # Available voices
    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, name="OpenAI TTS")

    async def generate(
        self,
        text: str,
        config: AudioConfig,
    ) -> AudioResult:
        """
        Synthesize speech using OpenAI TTS.

        Returns audio file as binary data.
        """
        start_time = time.time()

        try:
            logger.info(f"[{self.name}] Generating audio for {len(text)} characters")

            # Validate voice
            if config.voice not in self.VOICES:
                logger.warning(f"Voice '{config.voice}' not in standard OpenAI voices. " f"Available: {self.VOICES}")

            payload = {
                "model": config.model,
                "input": text,
                "voice": config.voice,
                "speed": config.speed,
            }

            # Response format determined by config
            if config.output_format == "mp3":
                payload["response_format"] = "mp3"
            elif config.output_format == "wav":
                payload["response_format"] = "wav"
            elif config.output_format == "opus":
                payload["response_format"] = "opus"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

                # Audio returned as binary data
                audio_data = response.content

            generation_time = int(time.time() - start_time)

            # Estimate duration (approximate: ~150 words/minute, ~5 chars/word)
            words = len(text) / 5
            duration_seconds = (words / 150) * 60

            logger.info(f"[{self.name}] Audio generated in {generation_time}s " f"(~{duration_seconds:.1f}s duration)")

            return AudioResult(
                success=True,
                provider=self.name,
                model=config.model,
                cost_usd=self.estimate_cost(text, config),
                generation_time_seconds=generation_time,
                audio_url=None,  # OpenAI returns binary, not URL
                duration_seconds=duration_seconds,
                # Note: audio_data would be stored separately, not in this model
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ProviderAuthError(f"Authentication failed: {e}")
            raise ProviderError(f"HTTP error: {e}")

        except Exception as e:
            logger.error(f"[{self.name}] Generation failed: {e}")
            raise ProviderError(f"Audio generation failed: {e}")

    def estimate_cost(self, text: str, config: AudioConfig) -> Decimal:
        """
        Estimate cost for OpenAI TTS.

        Pricing: $0.015 per 1K characters
        """
        char_count = len(text)
        cost_per_char = self.COST_PER_1K_CHARS / 1000
        return cost_per_char * char_count


# ============================================================================
# ElevenLabs TTS Provider
# ============================================================================


class ElevenLabsAudioProvider(BaseAudioProvider):
    """
    ElevenLabs Text-to-Speech provider.

    Premium quality, natural-sounding voices.
    Cost: $0.30 per 1K characters
    """

    BASE_URL = "https://api.elevenlabs.io/v1"
    COST_PER_1K_CHARS = Decimal("0.30")

    # Default voice ID (Rachel)
    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key, name="ElevenLabs")

    async def generate(
        self,
        text: str,
        config: AudioConfig,
    ) -> AudioResult:
        """
        Synthesize speech using ElevenLabs API.

        Returns audio file as binary data.
        """
        start_time = time.time()

        try:
            logger.info(f"[{self.name}] Generating audio for {len(text)} characters")

            # Use voice from config or default
            voice_id = config.voice if config.voice else self.DEFAULT_VOICE_ID

            url = f"{self.BASE_URL}/text-to-speech/{voice_id}"

            payload = {
                "text": text,
                "model_id": config.model if config.model != "tts-1" else "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                },
            }

            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

                audio_data = response.content

            generation_time = int(time.time() - start_time)

            # Estimate duration
            words = len(text) / 5
            duration_seconds = (words / 150) * 60

            logger.info(f"[{self.name}] Audio generated in {generation_time}s " f"(~{duration_seconds:.1f}s duration)")

            return AudioResult(
                success=True,
                provider=self.name,
                model=config.model,
                cost_usd=self.estimate_cost(text, config),
                generation_time_seconds=generation_time,
                audio_url=None,
                duration_seconds=duration_seconds,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ProviderAuthError(f"Authentication failed: {e}")
            raise ProviderError(f"HTTP error: {e}")

        except Exception as e:
            logger.error(f"[{self.name}] Generation failed: {e}")
            raise ProviderError(f"Audio generation failed: {e}")

    def estimate_cost(self, text: str, config: AudioConfig) -> Decimal:
        """
        Estimate cost for ElevenLabs TTS.

        Pricing: $0.30 per 1K characters
        """
        char_count = len(text)
        cost_per_char = self.COST_PER_1K_CHARS / 1000
        return cost_per_char * char_count


# ============================================================================
# Provider Registry
# ============================================================================


def create_audio_provider(provider_name: str, api_key: str) -> BaseAudioProvider:
    """Factory function to create audio providers"""
    providers = {
        "openai": OpenAIAudioProvider,
        "elevenlabs": ElevenLabsAudioProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown audio provider: {provider_name}. " f"Available: {list(providers.keys())}")

    return provider_class(api_key)
