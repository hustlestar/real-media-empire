import os
from collections import namedtuple

from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

from config import CONFIG
from video.movie import video_with_text, LineToMp3File, video_with_quote_and_label, save_final_video_file, AuthorLabel, ExtraLabel
from video.utils import read_n_video_clips

if __name__ == '__main__':
    import moviepy.config as cfg

    cfg.IMAGEMAGICK_BINARY = CONFIG.get("IMAGEMAGICK_BINARY")
    bg_video = read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                               "VIDEO",
                                               'portrait',
                                               f"1080_1920"), 1)[0]

    lines = [
        # LineToMp3File("Only way to do great work is to love what you do. And this quote is so huge and awesome, that we can't even think of anything else to do. And other people will recognize",
        #               "1.mp3"),
        LineToMp3File("to do\U0001F602\U0001F632\U0001F607", "2.mp3"),
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
    #    - "LeagueSpartan-ExtraBold"
    #   - "RubikMonoOne-Regular"
    f = 'RubikMonoOne-Regular'
    # video_with_text(bg_video, lines, font=f, shadow_color='black', result_file=f"{f}.mp4")
    # yellows = ['yellow',
    #            'yellow1',
    #            'yellow2',
    #            'yellow3',
    #            'yellow4',
    #            'YellowGreen']
    # test colors
    # yellows = [f.decode('utf-8') for f in TextClip.list('color') if 'blue' in f.decode('utf-8').lower()]
    # for y in yellows:
    #     video_with_text(bg_video, lines, text_colors=[y], font=f, shadow_color='black', result_file=f"{f}_{y}.mp4")
    # test fonts
    # yellows = [f for f in TextClip.list('font')]
    # for y in yellows:
    #     video_with_text(bg_video, lines, text_colors=['white'], font=y, shadow_color='black', result_file=f"{y}.mp4")
    # bg_video = read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
    #                                            "VIDEO",
    #                                            'landscape',
    #                                            f"1920_1080"), 1)[0]
    #
    videos = [video_with_quote_and_label(
        bg_video,
        lines[0],
        text_colors=['yellow'],
        font=f,
        shadow_color='black',
        darken_to=0.2 * i,
        author_label=AuthorLabel("Gabriel García Márquez", "gatos y llegó"),
        extra_label=ExtraLabel(f"Funny Fact", "green1"),
    ) for i in range(1)]

    final_video = concatenate_videoclips(videos, method="compose")

    save_final_video_file(final_video, f"comp_yellow.mp4")
