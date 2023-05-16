import os
from collections import namedtuple

from moviepy.audio.AudioClip import CompositeAudioClip, concatenate_audioclips
from moviepy.video.VideoClip import TextClip

from audio.audio_processor import read_audio_clip
from config import CONFIG
from video.movie import video_with_text, LineToMp3File
from video.utils import read_n_video_clips

if __name__ == '__main__':
    bg_video = read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                               "VIDEO",
                                               'portrait',
                                               f"1080_1920"), 1)[0]

    clips = [read_audio_clip(a) for a in [
        "1.mp3",
        "2.mp3",
        "3.mp3",
        "4.mp3"
    ]]

    fade_duration = 1

    # Create a composite audio clip from the list of clips with fade-in and fade-out
    all_audio_clips = [clip.set_start(sum([c.duration for c in clips[:i]])).audio_fadein(fade_duration).audio_fadeout(fade_duration) for i, clip in enumerate(clips)]
    # final_clip = CompositeAudioClip(all_audio_clips)
    final_clip = concatenate_audioclips(all_audio_clips)
    # Export the final audio clip
    final_clip.write_audiofile("final_clip.wav")
