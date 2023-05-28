import requests

from audio.text_to_speech import TextToSpeech
from config import CONFIG

ELEVEN_LABS_API_KEY = CONFIG.get("ELEVEN_LABS_API_KEY")


def synthesize_text(text, output_file, voice_language_code, voice_name, model_id="eleven_monolingual_v1", **kwargs):
    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_name}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)


def list_models():
    url = "https://api.elevenlabs.io/v1/models"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }
    response = requests.get(url, headers=headers)
    print(response.text)
    return response.text

def list_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    return response.json()['voices']

class ElevenLabsTextToSpeech(TextToSpeech):
    def synthesize_ssml(self, ssml=None, output_file=None, voice_language_code=2, voice_name=37, **kwargs):
        synthesize_text(ssml, output_file, voice_language_code, voice_name, **kwargs)

    def synthesize_text(self, text=None, output_file=None, voice_language_code=2, voice_name=37, **kwargs):
        synthesize_text(text, output_file, voice_language_code, voice_name, **kwargs)


if __name__ == '__main__':
    # ElevenLabsTextToSpeech().synthesize_text("Hello World", "test.mp3", voice_name=37)
    for v in list_voices():
        print(v)