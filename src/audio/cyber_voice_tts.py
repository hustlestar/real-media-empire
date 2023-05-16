import httpx
import requests

from audio.text_to_speech import TextToSpeech
from config import CONFIG

CYBER_VOICE_API_KEY = CONFIG.get("CYBERVOICE_API_KEY")

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": CYBER_VOICE_API_KEY
}


def synthesize_text(text, output_file=None,
                    voice_language_code=2,
                    voice_name=37,
                    gender='male'  # 'female'
                    ):
    if len(text) > 1000:
        raise Exception("This API takes 1000 symbols max")
    body = {
        'voice_id': voice_name,
        'text': text,
        'format': 'mp3'
    }

    url = "https://api.voice.steos.io/v1/get/tts"
    generate_response = httpx.post(url, headers=headers, json=body)
    data = generate_response.json()

    response = requests.get(data['audio_url'])
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
            print('File downloaded successfully.')
    else:
        print('Error occurred while downloading file.')

    print(data)


class CyberVoiceTextToSpeech(TextToSpeech):
    def synthesize_ssml(self, ssml=None, output_file=None, voice_language_code=2, voice_name=37, **kwargs):
        synthesize_text(ssml, output_file, voice_language_code, voice_name)

    def synthesize_text(self, text=None, output_file=None, voice_language_code=2, voice_name=37, **kwargs):
        synthesize_text(text, output_file, voice_language_code, voice_name)


def list_voices(is_print=False):
    url = "https://api.voice.steos.io/v1/get/voices"
    response = httpx.get(url, headers=headers)
    data = response.json()
    if is_print:
        for v in data['voices']:
            print(v)
    return data['voices']


def sample_all_voices(text):
    for v in list_voices():
        if v['id_lang'] == 2:  # and v['sex'] == 'male':  # english
            print(f"Generating using voice {v['voice_id']}")
            synthesize_text(
                text,
                output_file=f"{v['voice_id']}_sample.mp3",
                voice_name=v['voice_id']
            )


if __name__ == '__main__':
    # sample_all_voices("I want to test out how good this api became")
    list_voices(is_print=True)