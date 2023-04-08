import os
import random
from collections import namedtuple
from typing import List, NamedTuple
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

import moviepy.config as cfg
from moviepy.editor import *
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import TextClip

from audio.audio_processor import read_audio_clip
from config import CONFIG
from text.helpers import pick_random_from_list

cfg.IMAGEMAGICK_BINARY = CONFIG.get("IMAGEMAGICK_BINARY")
RES_1920_1080 = repr([1920, 1080])
RES_3840_2160 = repr([3840, 2160])

DIR_CACHE = {}

LineToMp3File = namedtuple('LineToMp3File', ['line', 'audio_file'])


def read_all_video_clips(path_to_dir, video_format='mp4'):
    return [VideoFileClip(os.path.join(path_to_dir, f)).setout_audio() for f in os.listdir(path_to_dir) if f.endswith(video_format)]


def read_n_video_clips(path_to_dir, number, video_format='mp4') -> List[VideoFileClip]:
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


def video_with_text(
        bg_video,
        line_to_voice_list: List[NamedTuple('LineToMp3File', [('line', str), ('audio_file', str)])],
        big_pause_duration=1.2,
        small_pause_duration=0.2,
        result_file='text_on_black_bg.mp4',
        bg_audio_filename=None,
        fonts_dir=None
):
    # Define the size and duration of the video clip
    # Create a black background clip with three color channels
    # bg = ImageClip(np.zeros((height, width, 3), dtype=np.uint8), duration=duration)
    font = os.path.join(fonts_dir, pick_random_from_list(os.listdir(fonts_dir)))
    text_clips = []
    audio_clips = []

    # if bg_video.w < bg_video.h:
    #     font_size = 70
    #     pos_1 = (0.1, 0.7)
    #     pos_2 = (0.1, 0.8)
    # else:
    #     font_size = 100
    #     pos_1 = (0.3, 0.5)
    #     pos_2 = (0.3, 0.7)
    font_size = 70
    pos_1 = (0.5, 0.5)
    pos_2 = (0.5, 0.6)
    print(f"Font size {font_size}")
    bg_width = bg_video.w
    bg_width_half = bg_width * pos_1[0]
    previous_end = 0
    for i, line_and_audio in enumerate(line_to_voice_list):
        audio = read_audio_clip(line_and_audio.audio_file)
        # audio = audio.fx(vfx.speedx, factor=0.9)
        duration = audio.duration
        text_line = line_and_audio.line
        if '.' in text_line:
            duration = duration + big_pause_duration
        elif text_line.startswith(',') or text_line.lower().startswith('and') or text_line.lower().startswith('or'):
            duration = duration + 0.25
        elif text_line.lower().startswith('but'):
            duration = duration + 0.4
        else:
            duration = duration + 0.05

        text_line = text_line.strip(',').strip()
        # if len(line_and_audio) <= 20:
        txt_clip = build_txt_clip(text_line, bg_width, bg_width_half, duration, font_size, pos_1, previous_end, font)
        # Make the text bold by overlaying a slightly shifted version of the text
        # in black with a small opacity
        shadow = build_txt_clip(text_line, bg_width, bg_width_half, duration, font_size, (pos_1[0] + 0.005, pos_1[1] + 0.005), previous_end, font, color='black')\
            .set_opacity(0.7)
        # .set_position(pos_1, relative=True)

        # text_clips.append(CompositeVideoClip([txt_clip, shadow]))
        text_clips.append(shadow)
        text_clips.append(txt_clip)

        audio = audio.set_start(previous_end)
        audio_clips.append(audio)
        # else:
        #     split_at = line_and_audio.line.find(' ', 20)
        #     if split_at == -1:
        #         clip = TextClip(
        #             line_and_audio.line,
        #             fontsize=font_size,
        #             color='white',
        #         ).set_position(pos_1, relative=True).set_duration(duration).set_start(previous_end)
        #         text_clips.append(clip)
        #     else:
        #         first_part = line_and_audio.line[:split_at]
        #         second_part = line_and_audio.line[split_at + 1:]
        #         clip = TextClip(first_part, fontsize=font_size, color='white') \
        #             .set_position(pos_1, relative=True).set_duration(duration).set_start(previous_end)
        #         text_clips.append(clip)
        #         clip = TextClip(second_part, fontsize=font_size, color='white') \
        #             .set_position(pos_2, relative=True).set_duration(duration).set_start(previous_end)
        #         text_clips.append(clip)
        previous_end += duration

    final_duration = sum([d.duration for d in text_clips]) / 2
    print(f"FINAL DURATION WOULD BE {final_duration}")

    if bg_audio_filename:
        bg_audio_clip = read_audio_clip(bg_audio_filename)
        bg_audio_clip = bg_audio_clip.set_duration(final_duration).volumex(0.6)
        audio_clips.append(bg_audio_clip)

    # from moviepy.video.tools.subtitles import SubtitlesClip
    # Composite the text clip onto the background clip
    final_audio = CompositeAudioClip(audio_clips)
    # final_audio = concatenate_audioclips(audio_clips)
    if bg_video.duration < final_duration:
        print(f"Background video is shorter than final duration {final_duration}")
    else:
        bg_video = bg_video.set_duration(final_duration)
    final_clip = CompositeVideoClip([bg_video, *text_clips])
    final_audio.set_duration(final_duration)
    final_clip = final_clip.set_audio(final_audio)
    final_clip.set_duration(final_duration)
    # Write the final clip to a file

    final_clip.write_videofile(
        result_file,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a'
    )


def build_txt_clip(text_line, bg_width, bg_width_half, duration, font_size, pos_1, previous_end, font, color='white'):
    txt_clip = TextClip(text_line, font=font, fontsize=font_size, color=color).set_duration(duration).set_start(previous_end)
    txt_width = txt_clip.w
    if txt_width > bg_width:
        raise Exception(f"Line text is too long {txt_width}")
    pos_w_rel = (bg_width_half - txt_width / 2) / bg_width
    print(f"Text Clip position is {pos_w_rel} {pos_1[1]}")
    txt_clip = txt_clip.set_position((pos_w_rel, pos_1[1]), relative=True)
    return txt_clip


if __name__ == '__main__':
    for f in TextClip.list('font'):
        print(f)
