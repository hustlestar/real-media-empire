import os
import random
from typing import List

from moviepy.editor import VideoFileClip, vfx, concatenate_videoclips

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
    MEDIA_DIR = "/Users/yauhenim/MEDIA"

    clips = read_all_video_clips(MEDIA_DIR)

    clips_buckets = map_clips_to_buckets_by_size(clips)

    print(clips_buckets)

    fhd_clips = clips_buckets.get(RES_1920_1080)

    ready_fhd_clips = [prepare_video_sublcip(c) for c in fhd_clips]

    ready = concatenate_videoclips(ready_fhd_clips)

    ready.write_videofile(os.path.join(MEDIA_DIR, "xxx.mp4"))
