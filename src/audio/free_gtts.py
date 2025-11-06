from gtts import gTTS
from gtts.lang import tts_langs


def synthesize_text(text, output_file, lang="en", accent="us", slow=False):
    tts = gTTS(text, lang=lang, tld=accent, slow=slow)
    tts.save(output_file)


def get_languages():
    return tts_langs()


if __name__ == "__main__":
    synthesize_text("this is test of google free api of google translate, I hope it won't break", "test_free_gtts.mp3")
