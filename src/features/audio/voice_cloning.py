"""
Voice Cloning and Management System using ElevenLabs Voice Lab.

This module provides comprehensive voice cloning capabilities for creating
consistent brand voices across all video content.

Features:
- Clone voices from audio samples (Voice Lab)
- Create custom voice designs
- Manage voice library (list, get, update, delete)
- Optimize voice settings for different content types
- Brand voice consistency enforcement
- Cost tracking and optimization

Run from project root with:
    PYTHONPATH=src python -c "from features.audio.voice_cloning import VoiceCloner; ..."
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Literal, Tuple
from dataclasses import dataclass
import requests
import json

try:
    from config import CONFIG
    ELEVEN_LABS_API_KEY = CONFIG.get("ELEVEN_LABS_API_KEY")
except ImportError:
    ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")


# Type definitions
VoiceCategory = Literal["narrator", "character", "brand", "celebrity", "custom"]
ContentType = Literal["short", "reel", "ad", "tutorial", "storytelling", "energetic"]


@dataclass
class VoiceSettings:
    """Voice synthesis settings for fine-tuning output."""
    stability: float = 0.5          # 0.0-1.0: Lower = more expressive, Higher = more stable
    similarity_boost: float = 0.75  # 0.0-1.0: How much to match original voice
    style: float = 0.0              # 0.0-1.0: Style exaggeration (v2 models only)
    use_speaker_boost: bool = True  # Boost similarity to speaker

    def to_dict(self) -> dict:
        """Convert to API format."""
        return {
            "stability": self.stability,
            "similarity_boost": self.similarity_boost,
            "style": self.style,
            "use_speaker_boost": self.use_speaker_boost
        }


@dataclass
class Voice:
    """Voice metadata."""
    voice_id: str
    name: str
    category: str = "custom"
    description: str = ""
    labels: Dict[str, str] = None
    samples: List[str] = None
    settings: VoiceSettings = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.samples is None:
            self.samples = []
        if self.settings is None:
            self.settings = VoiceSettings()


class VoiceCloner:
    """
    Voice cloning and management system using ElevenLabs Voice Lab.

    Use Cases:
    1. Clone founder/CEO voice for brand consistency
    2. Create character voices for storytelling
    3. Design voices optimized for different platforms
    4. Build voice library for content variety

    Example:
        >>> cloner = VoiceCloner(api_key="your-key")
        >>>
        >>> # Clone a voice from audio samples
        >>> voice = cloner.clone_voice(
        ...     name="Brand Voice - CEO",
        ...     audio_files=["sample1.mp3", "sample2.mp3"],
        ...     description="Our CEO's voice for product announcements"
        ... )
        >>>
        >>> # Generate speech with cloned voice
        >>> cloner.generate_speech(
        ...     text="Welcome to our product demo!",
        ...     voice_id=voice.voice_id,
        ...     output_path="output.mp3"
        ... )
    """

    BASE_URL = "https://api.elevenlabs.io/v1"

    # Optimized settings for different content types
    CONTENT_PRESETS = {
        "short": VoiceSettings(stability=0.4, similarity_boost=0.8, style=0.3, use_speaker_boost=True),
        "reel": VoiceSettings(stability=0.3, similarity_boost=0.85, style=0.4, use_speaker_boost=True),
        "ad": VoiceSettings(stability=0.6, similarity_boost=0.75, style=0.2, use_speaker_boost=True),
        "tutorial": VoiceSettings(stability=0.7, similarity_boost=0.7, style=0.0, use_speaker_boost=True),
        "storytelling": VoiceSettings(stability=0.5, similarity_boost=0.8, style=0.5, use_speaker_boost=True),
        "energetic": VoiceSettings(stability=0.2, similarity_boost=0.9, style=0.6, use_speaker_boost=True),
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize voice cloner.

        Args:
            api_key: ElevenLabs API key (or set ELEVEN_LABS_API_KEY env var)
        """
        self.api_key = api_key or ELEVEN_LABS_API_KEY
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVEN_LABS_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.headers = {
            "xi-api-key": self.api_key,
            "Accept": "application/json"
        }

    def clone_voice(
        self,
        name: str,
        audio_files: List[str],
        description: str = "",
        labels: Optional[Dict[str, str]] = None
    ) -> Voice:
        """
        Clone a voice from audio samples using Voice Lab.

        Requirements:
        - At least 1 audio sample (3+ recommended for better quality)
        - Each sample should be 30s-5min of clean speech
        - WAV or MP3 format
        - No background music/noise
        - Single speaker only

        Args:
            name: Voice name (e.g., "Brand Voice - CEO")
            audio_files: List of audio file paths
            description: Voice description
            labels: Optional metadata (e.g., {"use_case": "product_demos"})

        Returns:
            Voice object with voice_id for synthesis

        Cost:
            Cloning is free on most plans, but check your quota

        Example:
            >>> voice = cloner.clone_voice(
            ...     name="CEO Voice",
            ...     audio_files=["interview1.mp3", "interview2.mp3"],
            ...     description="CEO voice for announcements"
            ... )
        """
        if not audio_files:
            raise ValueError("At least 1 audio file required for voice cloning")

        # Validate files exist
        for audio_file in audio_files:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")

        # Prepare multipart form data
        url = f"{self.BASE_URL}/voices/add"

        files = []
        try:
            # Open all files
            for audio_file in audio_files:
                files.append(("files", (Path(audio_file).name, open(audio_file, "rb"), "audio/mpeg")))

            data = {
                "name": name,
                "description": description
            }

            if labels:
                data["labels"] = json.dumps(labels)

            # Make request
            response = requests.post(url, headers=self.headers, files=files, data=data)
            response.raise_for_status()

            result = response.json()
            voice_id = result["voice_id"]

            print(f"✅ Voice cloned successfully: {name} (ID: {voice_id})")

            return Voice(
                voice_id=voice_id,
                name=name,
                category="custom",
                description=description,
                labels=labels or {}
            )

        finally:
            # Close all file handles
            for _, file_tuple in files:
                file_tuple[1].close()

    def design_voice(
        self,
        name: str,
        gender: Literal["male", "female"],
        age: Literal["young", "middle_aged", "old"],
        accent: str,
        accent_strength: float = 0.5,
        description: str = "",
        labels: Optional[Dict[str, str]] = None
    ) -> Voice:
        """
        Design a synthetic voice using Voice Design (no audio samples needed).

        Args:
            name: Voice name
            gender: "male" or "female"
            age: "young", "middle_aged", or "old"
            accent: Accent name (e.g., "american", "british", "australian")
            accent_strength: 0.0-1.0, how strong the accent should be
            description: Voice description
            labels: Optional metadata

        Returns:
            Voice object with voice_id

        Note:
            Voice Design may require Professional tier or higher.
        """
        url = f"{self.BASE_URL}/voices/design"

        payload = {
            "name": name,
            "gender": gender,
            "age": age,
            "accent": accent,
            "accent_strength": accent_strength,
            "description": description
        }

        if labels:
            payload["labels"] = labels

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        result = response.json()
        voice_id = result["voice_id"]

        print(f"✅ Voice designed successfully: {name} (ID: {voice_id})")

        return Voice(
            voice_id=voice_id,
            name=name,
            category="custom",
            description=description,
            labels=labels or {}
        )

    def list_voices(self, show_legacy: bool = False) -> List[Voice]:
        """
        List all available voices (including cloned and premade).

        Args:
            show_legacy: Include legacy voices

        Returns:
            List of Voice objects
        """
        url = f"{self.BASE_URL}/voices"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        voices_data = response.json()["voices"]
        voices = []

        for v in voices_data:
            if not show_legacy and v.get("category") == "legacy":
                continue

            voice = Voice(
                voice_id=v["voice_id"],
                name=v["name"],
                category=v.get("category", "custom"),
                description=v.get("description", ""),
                labels=v.get("labels", {}),
                samples=[s["sample_id"] for s in v.get("samples", [])]
            )
            voices.append(voice)

        return voices

    def get_voice(self, voice_id: str) -> Voice:
        """
        Get detailed information about a specific voice.

        Args:
            voice_id: Voice ID

        Returns:
            Voice object with full details
        """
        url = f"{self.BASE_URL}/voices/{voice_id}"
        params = {"with_settings": "true"}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        v = response.json()

        # Extract settings if available
        settings = None
        if "settings" in v:
            s = v["settings"]
            settings = VoiceSettings(
                stability=s.get("stability", 0.5),
                similarity_boost=s.get("similarity_boost", 0.75),
                style=s.get("style", 0.0),
                use_speaker_boost=s.get("use_speaker_boost", True)
            )

        return Voice(
            voice_id=v["voice_id"],
            name=v["name"],
            category=v.get("category", "custom"),
            description=v.get("description", ""),
            labels=v.get("labels", {}),
            samples=[s["sample_id"] for s in v.get("samples", [])],
            settings=settings
        )

    def delete_voice(self, voice_id: str) -> bool:
        """
        Delete a cloned voice.

        Args:
            voice_id: Voice ID to delete

        Returns:
            True if successful

        Warning:
            Cannot delete premade voices, only custom cloned voices.
        """
        url = f"{self.BASE_URL}/voices/{voice_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()

        print(f"✅ Voice deleted: {voice_id}")
        return True

    def update_voice_settings(
        self,
        voice_id: str,
        settings: VoiceSettings
    ) -> bool:
        """
        Update voice synthesis settings.

        Args:
            voice_id: Voice ID
            settings: New voice settings

        Returns:
            True if successful
        """
        url = f"{self.BASE_URL}/voices/{voice_id}/settings/edit"

        response = requests.post(url, headers=self.headers, json=settings.to_dict())
        response.raise_for_status()

        print(f"✅ Voice settings updated: {voice_id}")
        return True

    def generate_speech(
        self,
        text: str,
        voice_id: str,
        output_path: str,
        model: str = "eleven_multilingual_v2",
        settings: Optional[VoiceSettings] = None,
        content_type: Optional[ContentType] = None
    ) -> str:
        """
        Generate speech from text using a voice.

        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            output_path: Output audio file path (.mp3)
            model: Model to use (eleven_multilingual_v2, eleven_monolingual_v1)
            settings: Custom voice settings (overrides content_type)
            content_type: Use preset settings for content type

        Returns:
            Path to generated audio file

        Models:
            - eleven_multilingual_v2: Best quality, 29 languages
            - eleven_monolingual_v1: English only, faster
            - eleven_turbo_v2: Fastest, good quality

        Example:
            >>> cloner.generate_speech(
            ...     text="Hello from our brand!",
            ...     voice_id="abc123",
            ...     output_path="output.mp3",
            ...     content_type="short"  # Optimized for shorts
            ... )
        """
        # Determine settings
        if settings is None:
            if content_type:
                settings = self.CONTENT_PRESETS.get(content_type, VoiceSettings())
            else:
                settings = VoiceSettings()

        url = f"{self.BASE_URL}/text-to-speech/{voice_id}"

        headers = {**self.headers, "Accept": "audio/mpeg", "Content-Type": "application/json"}

        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": settings.to_dict()
        }

        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        # Save audio
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        print(f"✅ Speech generated: {output_path}")
        return output_path

    def generate_speech_stream(
        self,
        text: str,
        voice_id: str,
        model: str = "eleven_multilingual_v2",
        settings: Optional[VoiceSettings] = None
    ) -> bytes:
        """
        Generate speech and return as bytes (for streaming or in-memory use).

        Args:
            text: Text to synthesize
            voice_id: Voice ID
            model: Model to use
            settings: Voice settings

        Returns:
            Audio data as bytes
        """
        settings = settings or VoiceSettings()

        url = f"{self.BASE_URL}/text-to-speech/{voice_id}/stream"

        headers = {**self.headers, "Accept": "audio/mpeg", "Content-Type": "application/json"}

        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": settings.to_dict()
        }

        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        # Collect all chunks
        audio_data = b""
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                audio_data += chunk

        return audio_data

    def find_voice_by_name(self, name: str) -> Optional[Voice]:
        """
        Find a voice by name.

        Args:
            name: Voice name (case-insensitive partial match)

        Returns:
            Voice object or None if not found
        """
        voices = self.list_voices()
        name_lower = name.lower()

        for voice in voices:
            if name_lower in voice.name.lower():
                return voice

        return None

    def get_usage_stats(self) -> dict:
        """
        Get API usage statistics.

        Returns:
            Dictionary with usage information (character count, quota, etc.)
        """
        url = f"{self.BASE_URL}/user"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        user_data = response.json()

        subscription = user_data.get("subscription", {})

        stats = {
            "character_count": subscription.get("character_count", 0),
            "character_limit": subscription.get("character_limit", 0),
            "remaining_characters": subscription.get("character_limit", 0) - subscription.get("character_count", 0),
            "can_use_instant_voice_cloning": user_data.get("can_use_instant_voice_cloning", False),
            "can_use_professional_voice_cloning": user_data.get("can_use_professional_voice_cloning", False),
            "tier": subscription.get("tier", "free")
        }

        return stats


# Convenience functions

def clone_voice(
    name: str,
    audio_files: List[str],
    description: str = "",
    api_key: Optional[str] = None
) -> Voice:
    """
    Convenience function to clone a voice.

    Example:
        >>> voice = clone_voice(
        ...     name="CEO Voice",
        ...     audio_files=["sample1.mp3", "sample2.mp3"],
        ...     description="Our CEO's voice"
        ... )
    """
    cloner = VoiceCloner(api_key=api_key)
    return cloner.clone_voice(name=name, audio_files=audio_files, description=description)


def generate_speech(
    text: str,
    voice_id: str,
    output_path: str,
    content_type: ContentType = "short",
    api_key: Optional[str] = None
) -> str:
    """
    Convenience function to generate speech.

    Example:
        >>> generate_speech(
        ...     text="Welcome!",
        ...     voice_id="abc123",
        ...     output_path="welcome.mp3",
        ...     content_type="short"
        ... )
    """
    cloner = VoiceCloner(api_key=api_key)
    return cloner.generate_speech(
        text=text,
        voice_id=voice_id,
        output_path=output_path,
        content_type=content_type
    )


if __name__ == "__main__":
    # Example usage
    print("Voice Cloning System - ElevenLabs Voice Lab")
    print("=" * 60)

    try:
        cloner = VoiceCloner()

        # List available voices
        print("\nAvailable Voices:")
        voices = cloner.list_voices()
        for voice in voices[:5]:  # Show first 5
            print(f"  • {voice.name} ({voice.voice_id}) - {voice.category}")

        # Show usage stats
        print("\nAPI Usage:")
        stats = cloner.get_usage_stats()
        print(f"  Characters used: {stats['character_count']:,} / {stats['character_limit']:,}")
        print(f"  Remaining: {stats['remaining_characters']:,}")
        print(f"  Tier: {stats['tier']}")
        print(f"  Instant voice cloning: {'✅' if stats['can_use_instant_voice_cloning'] else '❌'}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure ELEVEN_LABS_API_KEY is set in your environment or .env file")
