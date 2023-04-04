import os
from collections import namedtuple

from config import CONFIG
from video.movie import read_n_video_clips, video_with_text

if __name__ == '__main__':
    bg_video = read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                               "VIDEO",
                                               'portrait',
                                               f"1080_1920"), 1)[0]

    LineToMp3File = namedtuple('LineToMp3File', ['line', 'audio_file'])

    lines = [
        LineToMp3File("The only way", "1.mp3"),
        LineToMp3File("to do great work", "2.mp3"),
        LineToMp3File("is to love what you do.", "3.mp3"),
        LineToMp3File("Steve Jobs", "4.mp3")
    ]

    video_with_text(bg_video, lines)
