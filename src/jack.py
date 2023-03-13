import math
from random import randint

from moviepy.editor import *

from audio.audio_processor import read_audio_clip
from audio.google_tts import extract_only_ssml, remove_extra_spaces, synthesize_ssml, synthesize_text
from config import CONFIG
from text.chat_gpt import ChatGPTTask
from util.time import get_now
from video.movie import trim_video_duration, read_n_video_clips
from video.video_transitions import TRANSITIONS_BETWEEN_TWO, DEFAULT_TRANSITION, first_fade_out_second_fade_in_all


def take_random_transition(number_of_transitions=0):
    if number_of_transitions:
        return TRANSITIONS_BETWEEN_TWO[list(TRANSITIONS_BETWEEN_TWO.keys())[randint(0, number_of_transitions)]]
    else:
        return DEFAULT_TRANSITION


def prepare_result_file(transition_name):
    now = get_now()
    res_file = os.path.join(CONFIG.get('TMP_DOWNLOAD_DIR'), f"{now}_{transition_name}.mp4")
    res_file_without_tr = os.path.join(CONFIG.get('TMP_DOWNLOAD_DIR'), f"{now}_without_transition.mp4")
    if os.path.exists(res_file):
        os.remove(res_file)
    return res_file, res_file_without_tr


class YouTubeVideoTask:
    def __init__(self,
                 prompt=None,
                 background_audio_file=None,
                 voice_name=None,
                 number_of_trials=5,
                 text=None,
                 voice_audio_file=None,
                 audio_output_file=None,
                 start_end_voice_delay=6,
                 single_video_duration=10
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

    def prepare_text_for_voiceover(self):
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
        voice_with_delay = voice_with_delay.volumex(2)
        final_duration = math.ceil(self.start_end_voice_delay + voice_with_delay.duration + self.start_end_voice_delay)
        background_audio = read_audio_clip(self.background_audio_file).volumex(0.4)

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

    def prepare_video(self, final_duration):
        video_dir = os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'), "VIDEO")
        results = []
        counter = 0
        video = None
        used_video_clips = []
        while True:
            counter += 1
            print("Reading video clip")
            clip = read_n_video_clips(video_dir, 1)[0]
            if clip.duration < self.single_video_duration / 2:
                continue
            clip = trim_video_duration(clip, self.single_video_duration)
            results.append(clip)
            used_video_clips.append(clip.filename)
            video = first_fade_out_second_fade_in_all(results, 2)
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


if __name__ == '__main__':
    # # task = PexelsDownloadTask(query="city", download_dir=CONFIG.get('DOWNLOAD_DIR'), number_of_downloads=5).run()
    # #
    # # video_clips = create_all_video_clips(task.downloaded_files)
    #
    # # video_clips = read_all_video_clips(path_to_dir=CONFIG.get('DOWNLOAD_DIR'))
    # video_clips = read_n_video_clips(path_to_dir=CONFIG.get('DOWNLOAD_DIR'), number=10)
    #
    # print(video_clips)
    #
    # number_of_subclips = 3
    #
    # video_clips = video_clips[:number_of_subclips] if len(video_clips) > number_of_subclips else video_clips
    #
    # for c in video_clips:
    #     print(c.filename)
    # video_clips = [trim_video_duration(c, 7) for c in video_clips]
    #
    # all_transitions_names = TRANSITIONS_BETWEEN_TWO.keys()
    #
    # current_clip = None
    #
    # results_with_transition = []
    # # transition_index = len(all_transitions_names)
    # transition_index = 0
    #
    # # transition_name = "first_fade_out_second_fade_in"
    # transition_name = "first_fade_out_second_fade_in_all"
    #
    # # for l, r in zip(video_clips, video_clips[1:]):
    # #     print(l, r)
    # #     # Apply transition between clips
    # #     # transition = take_random_transition(transition_index)
    # #     # transition = TRANSITIONS.get("fadeinout")
    # #     transition = TRANSITIONS_BETWEEN_TWO.get(transition_name)
    # #     clip = transition(l, r, duration=1)
    # #     results_with_transition.append(clip)
    #
    # res_file, res_file_without_tr = prepare_result_file(transition_name)
    #
    # print(results_with_transition)
    # video = first_fade_out_second_fade_in_all(video_clips, 1)
    # video.audio = read_audio_clip('/Users/yauhenim/JACK/media-empire/tmp/en-US-Neural2-J_sample.mp3')
    # video.write_videofile(res_file,
    #                       codec='libx264',
    #                       audio_codec='aac',
    #                       temp_audiofile='temp-audio.m4a',
    #                       remove_temp=True)
    # slide_in_left_all(video_clips).write_videofile(res_file)
    # slide_in_top_all(video_clips).write_videofile(res_file)
    # concatenate_videoclips(results_with_transition, method='compose').write_videofile(res_file)
    # concatenate_videoclips(video_clips).write_videofile(res_file_without_tr)
    # print(results_with_transition)
    prompt = "Provide me with 2000 words motivational speech about having positive mindset in the style of Tony Robbins. " \
             "Represent your answer as ssml for google text to speech api." \
             "Use 5 seconds breaks between different parts, emphasize important parts by increasing or decreasing pitch." \
             "Prosody rate should be slow." \
             "Your answer should contain only xml"
    voice_name = 'en-US-Wavenet-J'
    audio_file_path = os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'), "VOICE", f"{get_now()}_{voice_name}.mp3")
    YouTubeVideoTask(
        prompt=prompt,
        audio_output_file=audio_file_path,
        voice_name=voice_name,
        number_of_trials=5,
        # background_audio_file="E:\\MEDIA_GALLERY\\AUDIO\\ES_For What Is Right - Trevor Kowalski epic,dreamy.mp3",
        background_audio_file="E:\\MEDIA_GALLERY\\AUDIO\\ES_Wandering Ahead - Trevor Kowalski epic,happy.mp3",
    ).run()
    # YouTubeVideoTask(
    #     prompt=prompt,
    #     voice_audio_file=audio_file_path,
    #     voice_name=voice_name,
    #     number_of_trials=1,
    #     background_audio_file="E:\\MEDIA_GALLERY\\AUDIO\\ES_For What Is Right - Trevor Kowalski epic,dreamy.mp3",
    # ).run()
    # audio_file_path = os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'), "VOICE", f"1jack.mp3")
    # YouTubeVideoTask(
    #     prompt=None,
    #     voice_audio_file=audio_file_path,
    #     voice_name=None,
    #     number_of_trials=1,
    #     background_audio_file="E:\\MEDIA_GALLERY\\AUDIO\\ES_For What Is Right - Trevor Kowalski epic,dreamy.mp3",
    # ).run()
