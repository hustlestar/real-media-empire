import os
from collections import namedtuple

from moviepy.video.VideoClip import TextClip

from config import CONFIG
from video.movie import video_with_text, LineToMp3File
from video.utils import read_n_video_clips

if __name__ == '__main__':
    bg_video = read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                               "VIDEO",
                                               'portrait',
                                               f"1080_1920"), 1)[0]

    lines = [
        LineToMp3File("Only way", "1.mp3"),
        # LineToMp3File("to do", "2.mp3"),
        # LineToMp3File("great work", "3.mp3"),
        # LineToMp3File("is to love", "4.mp3")
    ]

    f = "THEBOLDFONT"
    color = 'white'
    # for shadow in TextClip.list('color'):
    #     try:
    #         video_with_text(bg_video, lines, font=f, shadow_color=shadow.decode('utf-8'), result_file=f"{f}_{color}_{shadow.decode('utf-8')}.mp4")
    #     except Exception as x:
    #         print(f"failed on {shadow.decode('utf-8')}")
    f = 'THEBOLDFONT'
    # video_with_text(bg_video, lines, font=f, shadow_color='black', result_file=f"{f}.mp4")
    # yellows = ['yellow',
    #            'yellow1',
    #            'yellow2',
    #            'yellow3',
    #            'yellow4',
    #            'YellowGreen']
    yellows = [
        'orange',
        'orange1',
        'orange2',
        'orange3',
        'orange4',
        'OrangeRed',
        'OrangeRed1',
        'OrangeRed2',
        'OrangeRed3',
        'OrangeRed4',
    ]
    for y in yellows:
        video_with_text(bg_video, lines, text_colors=y, font=f, shadow_color='black', result_file=f"{f}_{y}.mp4")