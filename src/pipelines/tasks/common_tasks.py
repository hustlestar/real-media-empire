import math
import random
from typing import List, Tuple

from moviepy.editor import *

from audio.audio_processor import read_audio_clip
from audio.google_tts import remove_extra_spaces, extract_only_ssml, synthesize_ssml, synthesize_text
from common.exception import WrongMediaException
from config import CONFIG
from image.colors import get_image_main_colors
from image.image_tagging import get_image_classes
from image.video_to_image import extract_frames
from pipelines.tasks import DEFAULT_ORIENTATION, DEFAULT_HEIGHT, DEFAULT_WIDTH
from text.chat_gpt import ChatGPTTask
from util.time import get_now
from video.downloader import PexelsDownloadTask
from video.movie import read_n_video_clips, trim_clip_duration, read_video_clip
from video.video_transitions import first_fade_out_second_fade_in_all


def prepare_clip(video_dir, is_should_download, topics, orientation, width, height):
    if is_should_download and topics:
        res = PexelsDownloadTask(query=topics[random.randint(0, len(topics))], number_of_downloads=1, orientation=orientation, height=height, width=width).run()
        clip = read_video_clip(res.downloaded_files[0])
    else:
        clip = read_n_video_clips(video_dir, 1)[0]
    return clip


def extract_video_colors_and_topics(clip, colors, topics):
    images = extract_frames(clip.filename, num_frames=5)
    all_topics = set()
    all_colors = set()
    if topics:
        for i in images:
            image_classes = get_image_classes(image_ndarray=i, number_of_classes=6)
            all_topics.update(image_classes)
        print(f"All TOPICS from video {all_topics}")

    if colors:
        for i in images:
            image_colors = get_image_main_colors(image_ndarray=i, number_of_colors=6)
            all_colors.update(image_colors)
        print(f"All COLORS from video: {all_colors}")
    return all_colors, all_topics


def is_video_matching(clip, colors, colors_to_avoid, topics, topics_to_avoid):
    if topics or colors or colors_to_avoid:
        all_colors, all_topics = extract_video_colors_and_topics(clip, colors, topics)
        if colors and not any(color in colors for color in all_colors):
            raise WrongMediaException(f"Video colors are not in required {colors}")
        if colors_to_avoid and any(color in colors_to_avoid for color in all_colors):
            raise WrongMediaException(f"Video colors are in forbidden {colors_to_avoid}")
        if topics and not any(topic in topics for topic in all_topics):
            raise WrongMediaException(f"Video topics are not in required {topics}")
        if topics_to_avoid and any(topic in topics_to_avoid for topic in all_topics):
            raise WrongMediaException(f"Video topics are in forbidden {topics_to_avoid}")


def build_video_dir_path(orientation=DEFAULT_ORIENTATION, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
    return os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                        "VIDEO",
                        orientation,
                        f"{width}_{height}")


class CommonTasks:
    def __init__(
            self,
            prompt=None,
            background_audio_file=None,
            voice_name=None,
            number_of_trials=5,
            text=None,
            voice_audio_file=None,
            audio_output_file=None,
            start_end_voice_delay=6,
            single_video_duration=10,
            is_allow_duplicate_clips=False
    ):
        self.start_end_voice_delay = start_end_voice_delay
        if voice_audio_file and audio_output_file:
            raise ValueError("Can't specify both audio_file and audio_output_file")
        self.prompt = prompt
        self.background_audio_file = background_audio_file
        self.voice_name = voice_name
        self.number_of_trials = number_of_trials
        self.text = text
        self.audio_file = voice_audio_file
        self.audio_output_file = audio_output_file
        self.now = get_now()
        self.single_video_duration = single_video_duration
        self.result_video_clips = []
        self.is_allow_duplicate_clips = is_allow_duplicate_clips

    def prepare_text_for_voiceover(self) -> Tuple[str, bool]:
        is_ssml = False
        if self.text:
            text_for_voiceover = self.text
            if '<speak>' in self.text:
                is_ssml = True
        else:
            if not self.text:
                gpt_result = ChatGPTTask(self.prompt).run().text
            else:
                gpt_result = self.text

            gpt_result_trimmed = remove_extra_spaces(gpt_result)
            if 'ssml' not in self.prompt:
                text_for_voiceover = gpt_result_trimmed
            else:
                text_for_voiceover = extract_only_ssml(gpt_result_trimmed)
                is_ssml = True

        return text_for_voiceover, is_ssml

    def prepare_text_and_audio_with_voice(self):
        if not self.audio_file:
            text, is_ssml = self.prepare_text_for_voiceover()
            if is_ssml:
                synthesize_ssml(text, output_file=self.audio_output_file, voice_name=self.voice_name)
            else:
                synthesize_text(text, output_file=self.audio_output_file, voice_name=self.voice_name)
            audio_with_voice = read_audio_clip(self.audio_output_file)
        else:
            audio_with_voice = read_audio_clip(self.audio_file)
        return audio_with_voice

    def prepare_final_audio(self, audio_with_voice):
        voice_with_delay = audio_with_voice.set_start(self.start_end_voice_delay)
        voice_with_delay = voice_with_delay.volumex(2.2)
        final_duration = math.ceil(self.start_end_voice_delay + voice_with_delay.duration + self.start_end_voice_delay)
        background_audio = read_audio_clip(self.background_audio_file).volumex(0.3)

        if background_audio.duration < final_duration:
            number_of_loops = math.ceil(final_duration * 1.0 / background_audio.duration)
            print(f"Looping background audio for {number_of_loops} times")
            background_audio = background_audio.fx(afx.audio_loop, number_of_loops).set_duration(final_duration)
        else:
            background_audio = background_audio.set_duration(final_duration)

        final_audio = CompositeAudioClip([background_audio, voice_with_delay])
        # Fade out the audio at the beginning of the clip
        final_audio = final_audio.audio_fadeout(1)
        # Fade in the audio at the end of the clip
        final_audio = final_audio.audio_fadein(1)
        print(f"Audio with voice duration {final_audio.duration}")
        return final_audio, final_duration

    def prepare_video(
            self,
            final_duration,
            topics: List[str] = None,
            colors: List[str] = None,
            colors_to_avoid: List[str] = None,
            topics_to_avoid: List[str] = None,
            is_should_download=False,
            video_dir=build_video_dir_path(),
            orientation=DEFAULT_ORIENTATION,
            width=DEFAULT_WIDTH,
            height=DEFAULT_HEIGHT
    ):
        video = None
        videos_list = []
        used_video_clips = set()
        counter = 0
        while True:
            counter += 1
            print(f"Reading video clip {counter}")
            clip = prepare_clip(video_dir, is_should_download, topics, orientation, width, height)
            if not self.is_allow_duplicate_clips and clip.filename in used_video_clips:
                continue
            try:
                is_video_matching(clip, colors, colors_to_avoid, topics, topics_to_avoid)
            except WrongMediaException as x:
                print(x)
                continue

            if clip.duration < self.single_video_duration / 2:
                continue
            clip = trim_clip_duration(clip, self.single_video_duration)
            videos_list.append(clip)
            used_video_clips.add(clip.filename)
            video = first_fade_out_second_fade_in_all(videos_list, 1)
            if video.duration > final_duration:
                print("Achieved desired duration of video. Stopping")
                break
        return video, used_video_clips

    def prepare_and_save_final_video(self, video, final_audio, final_duration, result_filename):
        video = video.set_audio(final_audio)
        video = video.set_duration(final_duration)
        print(f"Final video duration would be {video.duration}")
        res_filename = result_filename
        video.write_videofile(res_filename,
                              codec='libx264',
                              audio_codec='aac',
                              temp_audiofile='temp-audio.m4a',
                              threads=6,
                              remove_temp=True)
        self.result_video_clips.append(res_filename)
        print(f"Final video saved to {res_filename}")

    def run(self):
        audio_with_voice = self.prepare_text_and_audio_with_voice()
        final_audio, final_duration = self.prepare_final_audio(audio_with_voice)

        for i in range(self.number_of_trials):
            print(f"Starting trial {i}")
            video, used_video_clips = self.prepare_video(final_duration)
            used_videos_str = "_".join([os.path.splitext(os.path.basename(f))[0] for f in used_video_clips])
            filename = f"{self.now}_{i}_N_{used_videos_str}"
            filename = filename[:180] + '.mp4' if len(filename) > 180 else filename + '.mp4'
            result_filename = os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'), "RESULT", filename)
            self.prepare_and_save_final_video(video, final_audio, final_duration, result_filename=result_filename)
        return self
