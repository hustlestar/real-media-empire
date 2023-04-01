import os
import random
from typing import List
from moviepy.editor import VideoFileClip

from moviepy.config import get_setting

import moviepy.config as cfg
import numpy as np
from config import CONFIG

cfg.IMAGEMAGICK_BINARY = CONFIG.get("IMAGEMAGICK_BINARY")

print(get_setting("IMAGEMAGICK_BINARY"))

RES_1920_1080 = repr([1920, 1080])
RES_3840_2160 = repr([3840, 2160])

DIR_CACHE = {}


def read_all_video_clips(path_to_dir, video_format='mp4'):
    return [VideoFileClip(os.path.join(path_to_dir, f)).without_audio() for f in os.listdir(path_to_dir) if f.endswith(video_format)]


def read_n_video_clips(path_to_dir, number, video_format='mp4'):
    dir_files = DIR_CACHE.get(path_to_dir)
    if not dir_files:
        dir_files = os.listdir(path_to_dir)
        DIR_CACHE[path_to_dir] = dir_files
    dir_files = [f for f in dir_files if f.endswith(video_format)]
    number_of_files_in_dir = len(dir_files)
    result = []
    for n in range(number):
        f = dir_files[random.randint(0, number_of_files_in_dir - 1)]
        result.append(VideoFileClip(os.path.join(path_to_dir, f)).without_audio())
    return result


def read_video_clip(path_to_clip):
    return VideoFileClip(path_to_clip).without_audio()


def create_all_video_clips(list_of_files):
    return [VideoFileClip(f).without_audio() for f in list_of_files]


def map_clips_to_buckets_by_size(clips: List[VideoFileClip]):
    clip_buckets = {}
    for c in clips:
        bucket = clip_buckets.get(repr(c.size))
        if bucket:
            bucket.append(c)
        else:
            clip_buckets[repr(c.size)] = [c]
    return clip_buckets


def prepare_video_sublcip(clip: VideoFileClip):
    clip = trim_clip_duration(clip)

    clip = concatenate_videoclips([
        clip.subclip(0, clip.duration - 2),
        clip.subclip(clip.duration - 2).fx(vfx.fadeout, 2)
    ])

    return clip


def trim_clip_duration(clip, to_max_duration_of=10):
    return clip if clip.duration < to_max_duration_of else clip.subclip(0, to_max_duration_of)


if __name__ == '__main__':
    from moviepy.editor import *

    # Define the size and duration of the video clip
    duration = 5

    # Create a black background clip with three color channels
    # bg = ImageClip(np.zeros((height, width, 3), dtype=np.uint8), duration=duration)
    bg = read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                         "VIDEO",
                                         'landscape',
                                         f"1920_1080"), 1)[0]
    lines = [
        "This is first line and it's long",
        "This is second line",
        "Guess what now?",
        "Here comes the 4th line"
    ]

    res = []

    current = 0
    for i, l in enumerate(lines):
        if len(l) <= 20:
            txt = TextClip(l, fontsize=70, color='white').set_pos(('center', 'center')).set_duration(duration).set_start(current)
            # create a color clip with rounded corners
            bg = ColorClip(txt.size, color='black', corner_radius=50)
            res.append(bg)
        else:
            split_at = l.find(' ', 20)
            if split_at == -1:
                clip = TextClip(l, fontsize=70, color='white', bg_color='black').set_pos(('center', 'center')).set_duration(duration).set_start(current)
                res.append(clip)
            else:
                first_part = l[:split_at]
                second_part = l[split_at + 1:]
                clip = TextClip(first_part, fontsize=70, color='white', bg_color='black').set_pos(('center', 'center')).set_duration(duration).set_start(current)
                res.append(clip)
                clip = TextClip(second_part, fontsize=70, color='white', bg_color='black').set_pos(('center', 'bottom')).set_duration(duration).set_start(current)
                res.append(clip)
                print(first_part)
                print(second_part)
        current += duration

    # from moviepy.video.tools.subtitles import SubtitlesClip
    # Composite the text clip onto the background clip
    final_clip = CompositeVideoClip([bg, *res])

    # Write the final clip to a file
    final_clip.write_videofile('text_on_black_bg.mp4', fps=30)
