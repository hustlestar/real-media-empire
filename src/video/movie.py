import os
from typing import List

from moviepy.editor import VideoFileClip, vfx, concatenate_videoclips

MEDIA_DIR = "/Users/yauhenim/MEDIA"

RES_1920_1080 = repr([1920, 1080])
RES_3840_2160 = repr([3840, 2160])

print(dir(vfx))


def read_all_video_clips(path_to_dir, video_format='mp4'):
    return [VideoFileClip(os.path.join(path_to_dir, f)) for f in os.listdir(path_to_dir) if f.endswith(video_format)]


def map_clips_to_buckets_by_size(clips: List[VideoFileClip]):
    clip_buckets = {}
    for c in clips:
        bucket = clip_buckets.get(repr(c.size))
        if bucket:
            bucket.append(c)
        else:
            clip_buckets[repr(c.size)] = [c]
    return clip_buckets


clips = read_all_video_clips(MEDIA_DIR)

clips_buckets = map_clips_to_buckets_by_size(clips)

print(clips_buckets)

fhd_clips = clips_buckets.get(RES_1920_1080)


def prepare_video_sublcip(clip: VideoFileClip):
    clip = clip if clip.duration < 10 else clip.subclip(0, 10)

    clip = concatenate_videoclips([
        clip.subclip(0, clip.duration - 2),
        clip.subclip(clip.duration - 2).fx(vfx.fadeout, 2)
    ])

    return clip


ready_fhd_clips = [prepare_video_sublcip(c) for c in fhd_clips]

ready = concatenate_videoclips(ready_fhd_clips)

ready.write_videofile(os.path.join(MEDIA_DIR, "xxx.mp4"))
