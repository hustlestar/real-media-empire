import logging

import os
import re

from google.cloud import texttospeech
from google.cloud.texttospeech_v1 import SsmlVoiceGender, AudioEncoding

from audio.text_to_speech import TextToSpeech
from config import CONFIG

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CONFIG.get("GOOGLE_TEXT_TO_SPEECH_API_KEY_PATH")

logger = logging.getLogger(__name__)


class GoogleTextToSpeech(TextToSpeech):
    def synthesize_ssml(
        self, ssml=None, output_file=None, voice_language_code="en-US", voice_name="en-US-Wavenet-D", gender=SsmlVoiceGender.MALE, **kwargs
    ):
        synthesize_ssml(ssml, output_file, voice_language_code, voice_name, gender)

    def synthesize_text(
        self,
        text=None,
        output_file=None,
        voice_language_code="en-US",
        voice_name="en-US-Wavenet-D",
        gender=SsmlVoiceGender.MALE,
        audio_config=texttospeech.AudioConfig(audio_encoding=AudioEncoding.MP3),
        **kwargs,
    ):
        synthesize_text(text, output_file, voice_language_code, voice_name, gender, audio_config)


def synthesize_ssml(ssml=None, output_file=None, voice_language_code="en-US", voice_name="en-US-Wavenet-D", gender=SsmlVoiceGender.MALE):
    """
    Synthesizes speech from the input string of ssml using the selected voice and audio
    encoding configuration. Saves the generated audio file to an MP3 file.
    """
    if not ssml or not output_file:
        raise Exception("Invalid argumets for the Google TTS request, please provide both ssml and output_file")
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(ssml=ssml)
    voice = texttospeech.VoiceSelectionParams(language_code=voice_language_code, name=voice_name, ssml_gender=gender)
    audio_config = texttospeech.AudioConfig(audio_encoding=AudioEncoding.MP3)
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    with open(output_file, "wb") as out:
        out.write(response.audio_content)


def synthesize_text(
    text=None,
    output_file=None,
    voice_language_code="en-US",
    voice_name="en-US-Studio-M",
    gender=SsmlVoiceGender.MALE,
    audio_config=texttospeech.AudioConfig(audio_encoding=AudioEncoding.MP3),
):
    """
    Synthesizes speech from the input string of text using the selected voice and audio
    encoding configuration. Saves the generated audio file to an MP3 file.
    """
    if not text or not output_file:
        raise Exception("Invalid argumets for the Google TTS request")
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=voice_language_code, name=voice_name, ssml_gender=gender)
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    with open(output_file, "wb") as out:
        out.write(response.audio_content)


def list_voices():
    client = texttospeech.TextToSpeechClient()
    voices = client.list_voices().voices
    results = []
    for voice in voices:
        if voice.language_codes[0] == "en-US":
            print(f"Name: {voice.name}")
            print(f"  Language: {voice.language_codes[0]}")
            print(f"  SSML Voice Gender: {voice.ssml_gender}")
            print(f"  Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")
            results.append(voice)
    return results


def remove_extra_spaces(text):
    # we need to drop all extra shit outta text, to not get additional cost for api usage
    ssml = re.sub(r"\s+", " ", text).strip()
    ssml = re.sub(r">\s+", ">", ssml).strip()
    ssml = re.sub(r"\s+<", "<", ssml).strip()
    return ssml


def extract_only_ssml(text):
    try:
        ssml = re.search(r"<speak.*>.*</speak>", text).group(0)
    except Exception as x:
        logger.info(f"Failed to find pattern in this text: \n{text}")
        raise x
    return ssml


def sample_all_voices(ssml):
    en_us_voices = list_voices()
    for v in en_us_voices:
        if v.ssml_gender == SsmlVoiceGender.MALE and "Studio" not in v.name:
            print(f"Generating using voice {v.name}")
            synthesize_ssml(ssml=ssml, output_file=f"{v.name}_sample.mp3", voice_name=v.name)


if __name__ == "__main__":
    # sample_text = ''
    # with open('..\\..\\tmp\\test_text_small.xml', 'r') as f:
    #     read = f.read()
    #
    # ssml_speak = extract_only_ssml(remove_extra_spaces(read))
    # print(ssml_speak)
    # list_voices()
    synthesize_text(
        "The only way",
        output_file="../video/1.mp3",
        voice_name="en-US-Wavenet-J",
    )
    synthesize_text(
        "to do great work",
        output_file="../video/2.mp3",
        voice_name="en-US-Wavenet-J",
    )
    synthesize_text(
        "is to love what you do",
        output_file="../video/3.mp3",
        voice_name="en-US-Wavenet-J",
    )
    synthesize_text(
        "Steve Jobs",
        output_file="../video/4.mp3",
        voice_name="en-US-Wavenet-J",
    )
