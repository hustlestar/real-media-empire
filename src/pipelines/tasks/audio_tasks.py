import logging
import math
import os.path
import random
from typing import Dict

from google.cloud import texttospeech
from google.cloud.texttospeech_v1 import AudioEncoding
from moviepy.editor import *
from moviepy.video.fx.speedx import speedx

from audio import google_tts
from audio.text_to_speech import TextToSpeech

TTS_APIS: Dict[str, TextToSpeech] = {
    'google_tts': google_tts.GoogleTextToSpeech()
}

logger = logging.getLogger(__name__)

class AudioTasks:
    def __init__(self, audio_background_dir_path=None, audio_background_api=None, audio_background_api_key_or_path=None, tts_api='google_tts', tts_type='ssml',
                 tts_voice_name="en-US-Wavenet-J", tts_api_key_or_path=None, start_end_delay=None, results_dir=None, voice_over_speed=None):
        self.audio_background_dir_path = audio_background_dir_path
        self.audio_background_api = audio_background_api
        self.audio_background_api_key_or_path = audio_background_api_key_or_path
        self.start_end_delay = start_end_delay

        self.tts_api = tts_api
        self.tts_type = tts_type
        self.tts_voice_name = tts_voice_name
        self.tts_api_key_or_path = tts_api_key_or_path
        self.results_dir = results_dir
        self.voice_over_speed = voice_over_speed

    def create_audio_background(self):
        if self.audio_background_dir_path:
            all_mp3 = [f for f in os.listdir(self.audio_background_dir_path) if f.endswith('.mp3')]
            random_background_mp3 = os.path.join(self.audio_background_dir_path, all_mp3[random.randint(0, len(all_mp3) - 1)])
            print(f"Audio background clip {random_background_mp3}")
            return random_background_mp3
        else:
            raise NotImplementedError("Api for audio background is not there yet")

    def create_audio_voice_over(self, text_script, is_ssml, result_file=None, speaking_rate=0.0):
        logger.info(f"Creating audio voice over for {text_script}, is_ssml={is_ssml}, result_file={result_file}, speaking_rate={speaking_rate}")
        api = TTS_APIS[self.tts_api]
        result_audio_file = os.path.join(self.results_dir, result_file)
        if is_ssml:
            api.synthesize_ssml(text_script, output_file=result_audio_file, voice_name=self.tts_voice_name)
        else:
            api.synthesize_text(text_script, output_file=result_audio_file, voice_name=self.tts_voice_name,
                                audio_config=texttospeech.AudioConfig(
                                    audio_encoding=AudioEncoding.MP3,
                                    speaking_rate=speaking_rate
                                ))

        return result_audio_file

    def create_final_audio(self, voice_over_audio, background_audio):
        voice_with_delay = voice_over_audio.set_start(self.start_end_delay)
        if self.voice_over_speed and self.voice_over_speed != 1:
            voice_with_delay = speedx(voice_with_delay, self.voice_over_speed)
        voice_with_delay = voice_with_delay.volumex(2.2)
        final_duration = math.ceil(self.start_end_delay + voice_with_delay.duration + self.start_end_delay)
        background_audio = background_audio.volumex(0.2)

        if background_audio.duration < final_duration:
            number_of_loops = math.ceil(final_duration * 1.0 / background_audio.duration)
            print(f"Looping background audio for {number_of_loops} times")
            background_audio = background_audio.fx(afx.audio_loop, number_of_loops).set_duration(final_duration)
        else:
            background_audio = background_audio.set_duration(final_duration)

        final_audio = CompositeAudioClip([background_audio, voice_with_delay])
        # Fade out the audio at the beginning of the clip
        final_audio = final_audio.audio_fadeout(1)
        # Fade in the audio at the end of the clip
        final_audio = final_audio.audio_fadein(1)
        print(f"Audio with voice duration {final_audio.duration}")
        return final_audio, final_duration
