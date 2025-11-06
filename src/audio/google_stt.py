import io
import os
import subprocess

from google.cloud import speech

from config import CONFIG

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CONFIG.get("GOOGLE_TEXT_TO_SPEECH_API_KEY_PATH")


def convert_mp3_to_wav(audio_file):
    command = ["ffmpeg", "-i", audio_file, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", "-y", f"{audio_file}.wav"]
    subprocess.call(command)


def transcribe_audio_with_timecodes(audio_file):
    client = speech.SpeechClient()

    convert_mp3_to_wav(audio_file)

    with io.open(f"{audio_file}.wav", "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(language_code="en", enable_word_time_offsets=True)

    response = client.recognize(config=config, audio=audio)

    transcript = ""
    for result in response.results:
        alternative = result.alternatives[0]
        transcript += f"{alternative.transcript} "
        for word in alternative.words:
            start_time = word.start_time.seconds + (word.start_time.total_seconds())
            end_time = word.end_time.seconds + (word.end_time.total_seconds())
            transcript += f"[{start_time:.2f}-{end_time:.2f}] "

    return transcript


if __name__ == "__main__":
    print(transcribe_audio_with_timecodes("E:\\MEDIA_GALLERY\\RESULTS\\daily_mindset_shorts\\2023_04_07_19_59_03\\0_voiceover.mp3"))
