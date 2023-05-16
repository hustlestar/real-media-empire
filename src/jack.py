from random import randint

from moviepy.editor import *

from config import CONFIG
from pipelines.tasks.video_tasks import CommonTasks
from util.time import get_now
from video.video_transitions import TRANSITIONS_BETWEEN_TWO, DEFAULT_TRANSITION


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
    prompt = "Provide me with 2000 words motivational speech for video about good and useful habits using ideas from Brian Tracy and his books. "
    prompt = prompt + \
             "Avoid using word I, be concise and inspiring." \
             "Represent your answer as ssml for google text to speech api." \
             "Use 5 seconds breaks between different parts, emphasize important parts by increasing or decreasing pitch." \
             "Set prosody rate to slow." \
             "Your answer should contain only xml"
    print(prompt)
    voice_name = 'en-US-Wavenet-J'
    audio_file_path = os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'), "VOICE", f"{get_now()}_{voice_name}.mp3")
    CommonTasks(
        prompt=prompt,
        audio_output_file=audio_file_path,
        voice_name=voice_name,
        number_of_trials=3,
        # background_audio_file="E:\\MEDIA_GALLERY\\AUDIO\\ES_For What Is Right - Trevor Kowalski epic,dreamy.mp3",
        background_audio_file="E:\\MEDIA_GALLERY\\AUDIO\\ES_Is It Worth It - Trailer Worx epic,hopeful.mp3",
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
