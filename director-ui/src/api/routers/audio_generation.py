"""
Enhanced audio generation API with TTS provider-specific optimizations.

Supports:
- Multiple TTS providers (Google, ElevenLabs, OpenAI)
- Provider-specific prompt generation
- Pronunciation fixes (IPA phonetic notation)
- SSML generation for Google TTS
- Emotion and prosody control
- Multi-take generation for A/B/C comparison
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
import uuid
import logging

# Audio provider imports - optional dependencies
try:
    from audio.google_tts import GoogleTextToSpeech, synthesize_ssml
    GOOGLE_TTS_AVAILABLE = True
except ImportError:
    GOOGLE_TTS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("google-cloud-texttospeech not available. Google TTS provider will be disabled.")

try:
    from audio.xi_labs_tts import ElevenLabsTextToSpeech
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("ElevenLabs TTS not available. ElevenLabs provider will be disabled.")

# OpenAI TTS would be imported here when available

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models
# ============================================================================


class PronunciationFix(BaseModel):
    """Pronunciation correction using IPA notation"""
    word: str
    phonetic: str = Field(..., description="IPA phonetic notation")
    alternative: Optional[str] = None


class PauseConfig(BaseModel):
    """Pause configuration"""
    after_word: str
    duration_ms: int = Field(ge=0, le=5000)


class AudioGenerationRequest(BaseModel):
    """Request to generate audio with full control"""
    text: str = Field(..., description="Raw text to convert to speech")
    provider_prompt: Optional[str] = Field(None, description="Provider-optimized prompt (auto-generated if not provided)")
    provider: Literal['google', 'elevenlabs', 'openai'] = 'elevenlabs'
    voice: str = 'en-US-Studio-M'
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: Optional[int] = Field(None, ge=-10, le=10, description="Pitch adjustment in semitones (Google only)")
    volume: float = Field(1.0, ge=0.0, le=2.0)
    emotion: Optional[str] = Field(None, description="Emotion preset: neutral, excited, calm, sad, angry, fearful")
    pronunciation_fixes: List[PronunciationFix] = []
    emphasis_words: List[str] = []
    pauses: List[PauseConfig] = []


class MultiTakeRequest(BaseModel):
    """Request to generate multiple takes for comparison"""
    text: str
    provider_prompt: Optional[str] = None
    provider: Literal['google', 'elevenlabs', 'openai'] = 'elevenlabs'
    voice: str = 'en-US-Studio-M'
    variations: List[Dict[str, Any]] = Field(
        default=[
            {'speed': 0.9, 'emotion': 'neutral'},
            {'speed': 1.0, 'emotion': 'neutral'},
            {'speed': 1.1, 'emotion': 'excited'}
        ],
        description="List of variation configs to generate"
    )


class AudioGenerationResponse(BaseModel):
    """Response with generated audio"""
    audio_url: str
    duration: float
    provider: str
    voice: str
    config: Dict[str, Any]
    provider_prompt_used: str = Field(..., description="The actual prompt sent to TTS provider")


class MultiTakeResponse(BaseModel):
    """Response with multiple takes"""
    takes: List[AudioGenerationResponse]
    count: int


# ============================================================================
# Helper Functions
# ============================================================================


def build_elevenlabs_prompt(
    text: str,
    pronunciation_fixes: List[PronunciationFix],
    emphasis_words: List[str],
    pauses: List[PauseConfig]
) -> str:
    """
    Build ElevenLabs-optimized prompt.

    ElevenLabs supports:
    - Phonetic notation in parentheses: word (pronunciation)
    - Emphasis with **markers**: **word**
    - Pauses with punctuation: word... or word,
    """
    enhanced_text = text

    # Apply pronunciation fixes
    for fix in pronunciation_fixes:
        # ElevenLabs format: word (phonetic)
        import re
        pattern = re.compile(rf'\b{re.escape(fix.word)}\b', re.IGNORECASE)
        enhanced_text = pattern.sub(f"{fix.word} ({fix.phonetic})", enhanced_text)

    # Apply emphasis
    for word in emphasis_words:
        import re
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        enhanced_text = pattern.sub(f"**{word}**", enhanced_text)

    # Apply pauses
    for pause in pauses:
        import re
        pattern = re.compile(rf'\b{re.escape(pause.after_word)}\b', re.IGNORECASE)
        pause_marker = '...' if pause.duration_ms > 500 else ','
        enhanced_text = pattern.sub(f"{pause.after_word}{pause_marker}", enhanced_text)

    return enhanced_text


def build_google_ssml(
    text: str,
    pronunciation_fixes: List[PronunciationFix],
    emphasis_words: List[str],
    pauses: List[PauseConfig],
    emotion: Optional[str] = None,
    speed: float = 1.0,
    pitch: int = 0
) -> str:
    """
    Build Google TTS SSML with full prosody control.

    Google SSML supports:
    - <phoneme> tags for pronunciation
    - <emphasis> tags
    - <break> tags for pauses
    - <prosody> for emotion/speed/pitch
    """
    ssml = '<speak>'

    # Apply emotion via prosody
    if emotion and emotion != 'neutral':
        emotion_map = {
            'excited': {'rate': 'fast', 'pitch': '+2st'},
            'calm': {'rate': 'slow', 'pitch': '-1st'},
            'sad': {'rate': 'slow', 'pitch': '-2st'},
            'angry': {'rate': 'medium', 'pitch': '+3st'},
            'fearful': {'rate': 'fast', 'pitch': '+1st'}
        }
        if emotion in emotion_map:
            config = emotion_map[emotion]
            ssml += f'<prosody rate="{config["rate"]}" pitch="{config["pitch"]}">'
    elif speed != 1.0 or pitch != 0:
        rate = 'fast' if speed > 1.1 else 'slow' if speed < 0.9 else 'medium'
        ssml += f'<prosody rate="{rate}" pitch="{pitch:+d}st">'

    enhanced_text = text

    # Apply pronunciation fixes
    for fix in pronunciation_fixes:
        import re
        pattern = re.compile(rf'\b{re.escape(fix.word)}\b', re.IGNORECASE)
        enhanced_text = pattern.sub(
            f'<phoneme alphabet="ipa" ph="{fix.phonetic}">{fix.word}</phoneme>',
            enhanced_text
        )

    # Apply emphasis
    for word in emphasis_words:
        import re
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        enhanced_text = pattern.sub(f'<emphasis level="strong">{word}</emphasis>', enhanced_text)

    # Apply pauses
    for pause in pauses:
        import re
        pattern = re.compile(rf'\b{re.escape(pause.after_word)}\b', re.IGNORECASE)
        enhanced_text = pattern.sub(
            f'{pause.after_word}<break time="{pause.duration_ms}ms"/>',
            enhanced_text
        )

    ssml += enhanced_text

    if (emotion and emotion != 'neutral') or speed != 1.0 or pitch != 0:
        ssml += '</prosody>'

    ssml += '</speak>'
    return ssml


def build_openai_prompt(
    text: str,
    emphasis_words: List[str],
    pauses: List[PauseConfig]
) -> str:
    """
    Build OpenAI-optimized prompt.

    OpenAI TTS works best with:
    - Capitalization for emphasis: WORD
    - Punctuation for pacing: word... or word,
    """
    enhanced_text = text

    # Apply pauses with punctuation
    for pause in pauses:
        import re
        pattern = re.compile(rf'\b{re.escape(pause.after_word)}\b', re.IGNORECASE)
        pause_marker = '...' if pause.duration_ms > 300 else ','
        enhanced_text = pattern.sub(f"{pause.after_word}{pause_marker}", enhanced_text)

    # Apply emphasis with capitalization
    for word in emphasis_words:
        import re
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        enhanced_text = pattern.sub(word.upper(), enhanced_text)

    return enhanced_text


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/generate", response_model=AudioGenerationResponse)
async def generate_audio(request: AudioGenerationRequest):
    """
    Generate audio with provider-specific optimizations.

    Automatically builds optimized prompts for each TTS provider:
    - ElevenLabs: Phonetic notation + emphasis markers
    - Google: Full SSML with prosody
    - OpenAI: Punctuation-based pacing
    """
    # Check provider availability
    if request.provider == 'google' and not GOOGLE_TTS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Google TTS provider is not available. Install google-cloud-texttospeech dependency."
        )
    if request.provider == 'elevenlabs' and not ELEVENLABS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs TTS provider is not available. Check ElevenLabs integration."
        )

    try:
        # Generate provider-specific prompt if not provided
        if request.provider_prompt:
            provider_prompt = request.provider_prompt
        else:
            if request.provider == 'elevenlabs':
                provider_prompt = build_elevenlabs_prompt(
                    request.text,
                    request.pronunciation_fixes,
                    request.emphasis_words,
                    request.pauses
                )
            elif request.provider == 'google':
                provider_prompt = build_google_ssml(
                    request.text,
                    request.pronunciation_fixes,
                    request.emphasis_words,
                    request.pauses,
                    request.emotion,
                    request.speed,
                    request.pitch or 0
                )
            elif request.provider == 'openai':
                provider_prompt = build_openai_prompt(
                    request.text,
                    request.emphasis_words,
                    request.pauses
                )
            else:
                provider_prompt = request.text

        logger.info(f"Generating audio with {request.provider}")
        logger.info(f"Provider prompt: {provider_prompt[:200]}...")

        # Generate audio based on provider
        output_file = f"/tmp/audio_{uuid.uuid4()}.mp3"

        if request.provider == 'elevenlabs':
            tts = ElevenLabsTextToSpeech()
            tts.synthesize_text(
                text=provider_prompt,
                output_file=output_file,
                voice_name=request.voice
            )
        elif request.provider == 'google':
            tts = GoogleTextToSpeech()
            tts.synthesize_ssml(
                ssml=provider_prompt,
                output_file=output_file,
                voice_name=request.voice
            )
        elif request.provider == 'openai':
            # OpenAI TTS integration would go here
            raise HTTPException(status_code=501, detail="OpenAI TTS not yet implemented")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {request.provider}")

        # Calculate duration (placeholder - would use actual audio analysis)
        duration = len(request.text.split()) * 0.3  # Rough estimate

        # Return public URL (in production, upload to CDN)
        audio_url = f"/audio/{uuid.uuid4()}.mp3"

        return AudioGenerationResponse(
            audio_url=audio_url,
            duration=duration,
            provider=request.provider,
            voice=request.voice,
            config={
                'speed': request.speed,
                'pitch': request.pitch,
                'emotion': request.emotion,
                'pronunciation_fixes_count': len(request.pronunciation_fixes),
                'emphasis_words_count': len(request.emphasis_words),
                'pauses_count': len(request.pauses)
            },
            provider_prompt_used=provider_prompt
        )

    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")


@router.post("/generate-takes", response_model=MultiTakeResponse)
async def generate_multiple_takes(request: MultiTakeRequest):
    """
    Generate multiple takes with different configurations for A/B/C comparison.

    Useful for directors to compare different speeds, emotions, and styles.
    """
    try:
        takes = []

        for idx, variation in enumerate(request.variations):
            # Build audio request for this variation
            audio_request = AudioGenerationRequest(
                text=request.text,
                provider_prompt=request.provider_prompt,
                provider=request.provider,
                voice=request.voice,
                speed=variation.get('speed', 1.0),
                pitch=variation.get('pitch'),
                emotion=variation.get('emotion', 'neutral'),
                pronunciation_fixes=[],
                emphasis_words=[],
                pauses=[]
            )

            # Generate audio
            result = await generate_audio(audio_request)
            takes.append(result)

            logger.info(f"Generated take {idx + 1}/{len(request.variations)}")

        return MultiTakeResponse(
            takes=takes,
            count=len(takes)
        )

    except Exception as e:
        logger.error(f"Error generating multiple takes: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-take generation failed: {str(e)}")


@router.get("/providers")
async def list_providers():
    """
    List available TTS providers and their capabilities.
    """
    return {
        "providers": [
            {
                "id": "elevenlabs",
                "name": "ElevenLabs",
                "available": ELEVENLABS_AVAILABLE,
                "quality": "premium",
                "supports": ["phonetic_pronunciation", "emphasis", "emotion", "voice_cloning"],
                "cost": "high",
                "latency": "medium",
                "recommended_for": "final_production"
            },
            {
                "id": "google",
                "name": "Google Cloud TTS",
                "available": GOOGLE_TTS_AVAILABLE,
                "quality": "high",
                "supports": ["ssml", "prosody", "phonemes", "emphasis", "breaks"],
                "cost": "medium",
                "latency": "low",
                "recommended_for": "ssml_control"
            },
            {
                "id": "openai",
                "name": "OpenAI TTS",
                "available": False,  # Not yet implemented
                "quality": "high",
                "supports": ["speed_control", "voice_selection"],
                "cost": "low",
                "latency": "very_low",
                "recommended_for": "rapid_iteration"
            }
        ]
    }


@router.get("/voices/{provider}")
async def list_voices(provider: str):
    """
    List available voices for a specific provider.
    """
    if provider == 'elevenlabs':
        # Would call ElevenLabs API to list voices
        return {
            "voices": [
                {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "gender": "female"},
                {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "gender": "female"},
                {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "gender": "female"},
                {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "gender": "male"},
                {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "gender": "female"},
            ]
        }
    elif provider == 'google':
        return {
            "voices": [
                {"id": "en-US-Studio-M", "name": "Studio Male", "gender": "male"},
                {"id": "en-US-Studio-O", "name": "Studio Female", "gender": "female"},
                {"id": "en-US-Wavenet-A", "name": "Wavenet A", "gender": "female"},
                {"id": "en-US-Wavenet-B", "name": "Wavenet B", "gender": "male"},
            ]
        }
    elif provider == 'openai':
        return {
            "voices": [
                {"id": "alloy", "name": "Alloy", "gender": "neutral"},
                {"id": "echo", "name": "Echo", "gender": "male"},
                {"id": "fable", "name": "Fable", "gender": "neutral"},
                {"id": "onyx", "name": "Onyx", "gender": "male"},
                {"id": "nova", "name": "Nova", "gender": "female"},
                {"id": "shimmer", "name": "Shimmer", "gender": "female"},
            ]
        }
    else:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
