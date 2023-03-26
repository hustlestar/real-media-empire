from abc import ABC


class TextToSpeech(ABC):
    def synthesize_ssml(self,
                        ssml=None,
                        output_file=None,
                        voice_language_code='en-US',
                        voice_name='en-US-Wavenet-D',
                        gender=None):
        ...

    def synthesize_text(self,
                        text=None,
                        output_file=None,
                        voice_language_code='en-US',
                        voice_name='en-US-Wavenet-D',
                        gender=None,
                        audio_config=None):
        ...
