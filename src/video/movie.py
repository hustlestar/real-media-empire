import logging
import math
import random
import textwrap
from collections import namedtuple
from typing import List, NamedTuple

import moviepy.config as cfg
from colorama import Fore
from moviepy.editor import *
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import TextClip

from audio.audio_processor import read_audio_clip
from config import CONFIG
from text.helpers import pick_random_from_list
from video.utils import find_matching_video

logger = logging.getLogger(__name__)

BG_CLIP_CHANGE_EVERY_N_SECONDS = 'every_n_seconds'
BG_CLIP_CHANGE_PER_SENTENCE = 'per_sentence'
BG_CLIP_CHANGE_PER_LINE = 'per_line'

BG_CLIP_STRATEGIES = {
    BG_CLIP_CHANGE_EVERY_N_SECONDS,
    BG_CLIP_CHANGE_PER_SENTENCE,
    BG_CLIP_CHANGE_PER_LINE
}

cfg.IMAGEMAGICK_BINARY = CONFIG.get("IMAGEMAGICK_BINARY")
RES_1920_1080 = repr([1920, 1080])
RES_3840_2160 = repr([3840, 2160])

LineToMp3File = namedtuple('LineToMp3File', ['line', 'audio_file'])


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
        fonts_list=None,
        font=None,
        text_colors=None,
        shadow_color='black'
):
    text_color = pick_random_from_list(text_colors)
    font = font if font else pick_random_from_list(fonts_list)
    text_clips = []
    audio_clips = []

    font_size = 70
    pos_1 = (0.5, 0.5)
    pos_2 = (0.5, 0.6)
    logger.info(f"Font size {font_size}")
    bg_width = bg_video.w
    bg_width_half = bg_width * pos_1[0]
    previous_end = 0
    for i, line_and_audio in enumerate(line_to_voice_list):
        audio = read_audio_clip(line_and_audio.audio_file)
        duration = audio.duration
        text_line = line_and_audio.line
        if '.' in text_line:
            duration = duration + big_pause_duration
        elif text_line.startswith(',') or text_line.lower().startswith('and') or text_line.lower().startswith('or'):
            duration = duration + 0.25
        elif text_line.lower().startswith('but'):
            duration = duration + 0.4
        else:
            duration = duration

        logger.info(f"Duration is {duration} where initial is {audio.duration} for line - {text_line}")
        text_line = text_line.strip(',').strip()
        txt_clip = build_txt_clip(text_line, bg_width, bg_width_half, duration, font_size, pos_1, previous_end, font, color=text_color)
        # Make the text bold by overlaying a slightly shifted version of the text
        # in black with a small opacity
        shadow = build_txt_clip(text_line, bg_width, bg_width_half, duration, font_size, (pos_1[0] + 0.005, pos_1[1] + 0.005), previous_end, font, color=shadow_color)

        text_clips.append(shadow)
        text_clips.append(txt_clip)

        audio = audio.set_start(previous_end)
        audio_clips.append(audio)
        previous_end += duration

    final_duration = sum([d.duration for d in text_clips]) / 2
    logger.info(f"FINAL DURATION WOULD BE {final_duration}")

    if bg_audio_filename:
        bg_audio_clip = read_audio_clip(bg_audio_filename)
        bg_audio_clip = bg_audio_clip.set_duration(final_duration).volumex(0.5)
        audio_clips.append(bg_audio_clip)

    # from moviepy.video.tools.subtitles import SubtitlesClip
    # Composite the text clip onto the background clip
    final_audio = CompositeAudioClip(audio_clips)
    # final_audio = concatenate_audioclips(audio_clips)
    if bg_video.duration < final_duration:
        logger.info(f"Background video is shorter than final duration {final_duration}")
    else:
        bg_video = bg_video.set_duration(final_duration)
    final_clip = CompositeVideoClip([bg_video, *text_clips])
    final_audio.set_duration(final_duration)
    final_clip = final_clip.set_audio(final_audio)
    final_clip.set_duration(final_duration)
    # Write the final clip to a file

    save_final_video_file(final_clip, result_file)


def video_with_text_full_sentence(
        bg_video,
        line_to_voice_list: List[NamedTuple('LineToMp3File', [('line', str), ('audio_file', str)])],
        big_pause_duration=1.2,
        result_file='text_on_black_bg.mp4',
        bg_audio_filename=None,
        fonts_list=None,
        font=None,
        text_colors=None,
        shadow_color='black',
        line_width=17,
        font_size=100
):
    text_color = pick_random_from_list(text_colors)
    font = font if font else pick_random_from_list(fonts_list)
    text_clips = []
    audio_clips = []

    pos_1 = (0.5, 0.5)
    logger.info(f"Font size {font_size}")
    bg_width = bg_video.w
    bg_width_half = bg_width * pos_1[0]
    previous_end = 0
    for i, line_and_audio in enumerate(line_to_voice_list):
        audio = read_audio_clip(line_and_audio.audio_file)
        audio = audio.set_start(previous_end)
        audio_clips.append(audio)
        duration = audio.duration
        text_lines = textwrap.wrap(line_and_audio.line, line_width, break_long_words=False)

        single_duration = duration / len(text_lines)

        for i, text_line in enumerate(text_lines):
            if i == len(text_lines) - 1:
                single_duration = single_duration + big_pause_duration
            logger.info(f"Duration is {single_duration} for line - {text_line}")
            # text_line = text_line.strip(',').strip()
            txt_clip = build_txt_clip(text_line, bg_width, bg_width_half, single_duration, font_size, pos_1, previous_end, font, color=text_color)
            shadow = build_txt_clip(text_line, bg_width, bg_width_half, single_duration, font_size, (pos_1[0] + 0.005, pos_1[1] + 0.005), previous_end, font, color=shadow_color)

            text_clips.append(shadow)
            text_clips.append(txt_clip)

            previous_end += single_duration

    final_duration = sum([d.duration for d in text_clips]) / 2
    logger.info(f"FINAL DURATION WOULD BE {final_duration}")

    if bg_audio_filename:
        bg_audio_clip = read_audio_clip(bg_audio_filename)
        bg_audio_clip = bg_audio_clip.set_duration(final_duration).volumex(0.5)
        audio_clips.append(bg_audio_clip)

    final_audio = CompositeAudioClip(audio_clips)
    if bg_video.duration < final_duration:
        logger.info(f"Background video is shorter than final duration {final_duration}")
    else:
        bg_video = bg_video.set_duration(final_duration)
    final_clip = CompositeVideoClip([bg_video, *text_clips])
    final_audio.set_duration(final_duration)
    final_clip = final_clip.set_audio(final_audio)
    final_clip.set_duration(final_duration)
    # Write the final clip to a file

    save_final_video_file(final_clip, result_file)


def video_with_text_full_sentence_many_clips(
        channel: "YouTubeChannel",
        line_to_voice_list: List[NamedTuple('LineToMp3File', [('line', str), ('audio_file', str)])],
        big_pause_duration=1.2,
        result_file='text_on_black_bg.mp4',
        bg_audio_filename=None,
        fonts_list=None,
        font=None,
        text_colors=None,
        shadow_color='black',
        line_width=17,
        font_size=90,
        bg_clip_strategy=BG_CLIP_CHANGE_EVERY_N_SECONDS,
        single_clip_duration=2
):
    logger.info(f"Starting clip generation with bg clip {bg_clip_strategy}")
    text_color = pick_random_from_list(text_colors)
    font = font if font else pick_random_from_list(fonts_list)
    bg_clips = []
    text_clips = []
    audio_clips = []

    pos_1 = (0.5, 0.5)
    logger.info(f"Font size {font_size}")
    bg_width = channel.config.video_width
    bg_width_half = bg_width * pos_1[0]
    previous_end = 0

    previous_batch_end = 0
    for i, line_and_audio in enumerate(line_to_voice_list):
        audio = read_audio_clip(line_and_audio.audio_file)
        audio = audio.set_start(previous_end)
        audio_clips.append(audio)
        duration = audio.duration
        text_lines = textwrap.wrap(line_and_audio.line, line_width, break_long_words=False)
        single_duration = duration / len(text_lines)

        for j, text_line in enumerate(text_lines):
            if j == len(text_lines) - 1:
                single_duration = single_duration + big_pause_duration
            logger.info(f"Duration is {single_duration} for line - {text_line}")
            txt_clip = build_txt_clip(text_line, bg_width, bg_width_half, single_duration, font_size, pos_1, previous_end, font, color=text_color)
            shadow = build_txt_clip(text_line, bg_width, bg_width_half, single_duration, font_size, (pos_1[0] + 0.005, pos_1[1] + 0.005), previous_end, font, color=shadow_color)

            text_clips.append(shadow)
            text_clips.append(txt_clip)

            if bg_clip_strategy == BG_CLIP_CHANGE_PER_LINE:
                video = find_matching_video(channel, single_duration)
                video = video.set_duration(single_duration)
                video = video.set_start(previous_end)
                logger.info(Fore.RED + f"{bg_clip_strategy}: Adding video to bg_clips starting at {previous_end}, with duration of {single_duration}")
                bg_clips.append(video)

            previous_end += single_duration

            if bg_clip_strategy == BG_CLIP_CHANGE_PER_SENTENCE and j == len(text_lines) - 1:
                required_duration = previous_end - previous_batch_end
                video = find_matching_video(channel, required_duration)
                video = video.set_start(previous_batch_end)
                video = video.set_duration(required_duration)
                logger.info(Fore.GREEN + f"{bg_clip_strategy}: Adding video to bg_clips starting at {required_duration}, with duration of {required_duration}")
                bg_clips.append(video)

            if j == len(text_lines) - 1:
                previous_batch_end = previous_end

    final_duration = sum([d.duration for d in text_clips]) / 2
    logger.info(f"FINAL DURATION WOULD BE {final_duration}")

    previous_end = 0
    if bg_clip_strategy == BG_CLIP_CHANGE_EVERY_N_SECONDS:
        while previous_end < final_duration:
            video = find_matching_video(channel, single_clip_duration)
            video = video.set_start(previous_end)
            video = video.set_duration(single_clip_duration)
            logger.info(Fore.BLUE + f"{bg_clip_strategy}: Adding video to bg_clips starting at {previous_end}, with duration of {single_clip_duration}")
            previous_end = previous_end + single_clip_duration
            bg_clips.append(video)

    bg_video = CompositeVideoClip(bg_clips)

    if bg_audio_filename:
        bg_audio_clip = read_audio_clip(bg_audio_filename)
        bg_audio_clip = bg_audio_clip.set_duration(final_duration).volumex(0.3)
        audio_clips.append(bg_audio_clip)

    final_audio = CompositeAudioClip(audio_clips)

    if bg_video.duration < final_duration:
        logger.info(f"Background video is shorter than final duration {final_duration}")
    else:
        bg_video = bg_video.set_duration(final_duration)
    final_clip = CompositeVideoClip([bg_video, *text_clips])
    final_audio.set_duration(final_duration)
    final_clip = final_clip.set_audio(final_audio)
    final_clip.set_duration(final_duration)
    # Write the final clip to a file
    logger.info(Fore.WHITE + "Finished clip creation, saving result")
    save_final_video_file(final_clip, result_file)


def save_final_video_file(final_clip, result_file):
    final_clip.write_videofile(
        result_file,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=f'{random.randint(0, 100)}_temp-audio.m4a',
        remove_temp=True
    )


def build_txt_clip(text_line, bg_width, bg_width_half, duration, font_size, pos_1, previous_end, font, color='white') -> TextClip:
    txt_clip = TextClip(text_line, font=font, fontsize=font_size, color=color).set_duration(duration).set_start(previous_end)
    txt_width = txt_clip.w
    if txt_width > bg_width:
        raise Exception(f"Line text is too long {txt_width}")
    pos_w_rel = (bg_width_half - txt_width / 2) / bg_width + (pos_1[0] - 0.5)
    logger.info(f"Text Clip width for font {font} is {txt_clip.w} for {text_line} position is {pos_w_rel} {pos_1[1]} for {text_line}")
    txt_clip = txt_clip.set_position((pos_w_rel, pos_1[1]), relative=True)
    return txt_clip


def music_video(
        bg_video,
        music_file_list: List[str],
        result_file='music_on_black_bg.mp4',
        desired_duration=60 * 60,
        fade_duration=5
):
    # Define the size and duration of the video clip
    final_duration = desired_duration
    logger.info(f"FINAL DURATION WOULD BE {final_duration}")

    # Create a composite audio clip from the list of clips with fade-in and fade-out
    all_audio_clips = []
    for i, music_file in enumerate(music_file_list):
        clip = read_audio_clip(music_file)
        audio_start_at = sum([c.duration for c in music_file_list[:i]])
        all_audio_clips.append(clip.set_start(audio_start_at).audio_fadein(fade_duration).audio_fadeout(fade_duration))
    final_audio = concatenate_audioclips(all_audio_clips)

    if final_audio.duration < final_duration:
        number_of_loops = math.ceil(final_duration * 1.0 / final_audio.duration)
        logger.info(f"Looping Music audio for {number_of_loops} times")
        final_audio = final_audio.fx(afx.audio_loop, number_of_loops).set_duration(final_duration)

    if bg_video.duration < final_duration:
        logger.info(f"Background video is shorter than final duration {final_duration}")
        number_of_loops = math.ceil(final_duration * 1.0 / bg_video.duration)
        logger.info(f"Looping Video for {number_of_loops} times")
        bg_video = bg_video.fx(vfx.loop, number_of_loops).set_duration(final_duration)
    else:
        bg_video = bg_video.set_duration(final_duration)

    final_clip = bg_video
    final_audio.set_duration(final_duration)
    final_clip = final_clip.set_audio(final_audio)
    final_clip.set_duration(final_duration)

    # Write the final clip to a file
    save_final_video_file(final_clip, result_file)


if __name__ == '__main__':
    for f in TextClip.list('font'):
        logger.info(f)
    # for c in TextClip.list('color'):
    #     logger.info(c)
