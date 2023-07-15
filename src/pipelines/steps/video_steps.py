import logging
import os
from moviepy.video.compositing.concatenate import concatenate_videoclips
from typing import List
from zenml.steps import step, Output

from audio.audio_processor import read_audio_clip
from common.exception import WrongMediaException
from data.dao import get_db, add_author_to_channel
from pipelines.params.params_for_pipeline import PipelineParams
from pipelines.steps.utils import predefined_quote_by_author, get_single_author, find_unused_author, prepare_author_title, prepare_extra_label, prepare_quote_intro_questions, \
    is_bad_intro_question, prepare_intro_video, prepare_thematic_download_generator, read_video_for_channel, voice_overs, single_voice_over, shorts_with_voice, build_file_name
from pipelines.you_tube_channel import YouTubeChannel
from text.helpers import pick_random_from_list
from util.time import get_now
from video.movie import LineToMp3File, trim_clip_duration, video_with_text_full_sentence_many_clips, \
    video_with_quote_and_label, AuthorLabel, save_final_video_file, BIG_PAUSE, add_bg_audio_starting_at
from video.utils import is_video_matching, find_matching_video, pick_audio_background_file
from video.video_transitions import first_fade_out_second_fade_in_all

logger = logging.getLogger(__name__)


@step
def generate_shorts_swamp(params: PipelineParams) -> None:
    logger.info(f"Starting generation of new shorts {params.number_of_videos}")
    for i in range(params.number_of_videos):
        now = get_now()
        logger.info(f"Starting generation of video {i} at {now}")
        params = params.copy(update={"execution_date": now})
        quote_lines = predefined_quote_by_author(params)
        voice_over_files = voice_overs(params, quote_lines)
        shorts_with_voice(params, quote_lines, voice_over_files, is_swamp=True)
    logger.info("Finished shorts generation")


@step
def generate_quotes_video(params: PipelineParams) -> Output(video_file_path=str, text_script=str):
    logger.info(f"Starting generation of new QUOTES video{params.number_of_videos}")
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    now = get_now()
    logger.info(f"Starting generation of video at {now}")
    # params = params.copy(update={"execution_date": now})
    author_dict = find_unused_author(params)
    if not author_dict:
        raise Exception(f"NOT FOUND UNUSED AUTHOR")
    logger.info(f"Result author that was chosen\n{author_dict}")
    author_funny_facts = author_dict.get("author_funny_facts")
    author_interesting_facts = author_dict.get("author_interesting_facts")
    author_inspiring_facts = author_dict.get("author_inspiring_facts")
    used_facts = set()
    all_quotes_videos = []
    voice_over_id = 0
    quotes = author_dict.get('quotes')
    result_text_script = "".join(author_dict.get("quotes") + author_funny_facts + author_interesting_facts + author_inspiring_facts)
    with open(os.path.join(channel.result_dir, f"0_text_script.txt"), "w") as f:
        f.write(result_text_script)
    quotes = set(quotes)
    for i, quote in enumerate(quotes):
        if i % 9 == 0:
            fact_label_tuple = prepare_extra_label(author_funny_facts, author_interesting_facts, author_inspiring_facts, used_facts)
            if fact_label_tuple:
                voice_over_file = single_voice_over(fact_label_tuple[0], channel, index=voice_over_id, is_secondary=True)
                voice_over_id = voice_over_id + 1
                required_duration = (read_audio_clip(voice_over_file).duration + BIG_PAUSE) * 1.2
                bg_video = find_matching_video(channel, required_duration=required_duration)
                fact_video = video_with_quote_and_label(
                    bg_video,
                    LineToMp3File(fact_label_tuple[0], voice_over_file),
                    text_colors=['yellow'],
                    fonts_list=channel.config.video_fonts_list,
                    author_label=AuthorLabel(author_dict.get("author"), prepare_author_title(author_dict.get("author_description"))),
                    additional_pause=BIG_PAUSE,
                    extra_label=fact_label_tuple[1]
                )
                if fact_video:
                    all_quotes_videos.append(fact_video)

        if len(quote) > 35 * 5:
            logger.warning(f"Quote is too long, skipping: {quote}")
            continue

        voice_over_file = single_voice_over(quote, channel, index=voice_over_id)
        voice_over_id = voice_over_id + 1

        required_duration = (read_audio_clip(voice_over_file).duration + BIG_PAUSE) * 1.2
        bg_video = find_matching_video(channel, required_duration=required_duration)
        single_quote_video = video_with_quote_and_label(
            bg_video,
            LineToMp3File(quote, voice_over_file),
            text_colors=['white'],
            fonts_list=channel.config.video_fonts_list,
            shadow_color='black',
            author_label=AuthorLabel(author_dict.get("author"), prepare_author_title(author_dict.get("author_description"))),
            additional_pause=BIG_PAUSE,
        )
        if single_quote_video:
            all_quotes_videos.append(single_quote_video)

    final_video = concatenate_videoclips(all_quotes_videos, method="compose")
    result_video_file_path = build_file_name(author_dict.get("author"), channel, 0, is_swamp=False, params=params)
    save_final_video_file(final_video, result_video_file_path)
    add_author_to_channel(next(get_db()), channel_name=channel.config.youtube_channel_id, author_name=author_dict.get('author'))
    logger.info("Finished QUOTES generation")
    return result_video_file_path, result_text_script


@step
def generate_quotes_shorts(params: PipelineParams) -> Output(video_file_path=str, text_script=str):
    logger.info(f"Starting generation of new QUOTES video{params.number_of_videos}")
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    now = get_now()
    logger.info(f"Starting generation of video at {now}")
    author_dict = get_single_author(params)
    logger.info(f"Result author that was chosen\n{author_dict}")
    final_video_sequence = []

    quote = pick_random_from_list(author_dict.get('quotes'))
    logger.info(f"Selected randomly following quote:\n{quote}\nwith length {len(quote)}")

    while len(quote) > 35 * 5:
        quote = pick_random_from_list(author_dict.get('quotes'))

    author = author_dict.get('author')
    thematic_download_generator = prepare_thematic_download_generator(channel, quote)

    voice_over_index = 0
    voice_over_file = single_voice_over(quote, channel, index=voice_over_index)
    voice_over_index = voice_over_index + 1
    author_voice_over_file = single_voice_over(author, channel, index=voice_over_index)
    voice_over_index = voice_over_index + 1

    intro_questions = prepare_quote_intro_questions(quote, author)
    for i, intro_question in enumerate(intro_questions):
        skip_question = is_bad_intro_question(intro_question)

        if skip_question:
            logger.info("!" * 100)
            logger.info(f"Skipping question: {intro_question}")
            logger.info("!" * 100)
            continue
        intro_video, intro_question, voice_over_index = prepare_intro_video(channel, final_video_sequence, voice_over_index, thematic_download_generator,
                                                                            intro_question=intro_question)

        main_quote = video_with_text_full_sentence_many_clips(
            channel,
            [LineToMp3File(quote, voice_over_file)],
            text_colors=['white'],
            fonts_list=channel.config.video_fonts_list,
            shadow_color='black',
            thematic_download_generator=thematic_download_generator,
            is_save_result=False,
            single_clip_duration=3,
            bg_audio_filename=pick_audio_background_file(channel)
        )
        final_video_sequence.append(main_quote)

        if author.lower() not in intro_question.lower():
            the_end_author = video_with_text_full_sentence_many_clips(
                channel,
                [LineToMp3File(author, author_voice_over_file)],
                text_colors=['yellow'],
                fonts_list=channel.config.video_fonts_list,
                shadow_color='black',
                thematic_download_generator=thematic_download_generator,
                is_save_result=False,
                single_clip_duration=4)
            final_video_sequence.append(the_end_author)

        logger.info(f"Final video sequence is {len(final_video_sequence)} videos long, concatenating them")
        final_video = concatenate_videoclips(final_video_sequence, method="compose")
        add_bg_audio_starting_at(channel, final_video, intro_video, audio_start_at=intro_video.duration)
        result_text_script = "".join([intro_question, quote])
        with open(os.path.join(channel.result_dir, f"{i}_text_script.txt"), "w") as f:
            f.write(result_text_script)
        result_video_file_path = build_file_name(author_dict.get("author"), channel, i, is_swamp=False, params=params)
        save_final_video_file(final_video, result_video_file_path)
        final_video_sequence = []
        logger.info("Finished QUOTES shorts generation")
    return result_video_file_path, result_text_script


@step
def music_video(params: PipelineParams) -> None:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    videos_list = []
    used_video_clips = set()
    counter = 0
    video = None
    while True:
        counter += 1
        logger.info(f"Reading video clip {counter}")
        clip = read_video_for_channel(channel)
        try:
            is_video_matching(clip,
                              topics=channel.video_manager.topics,
                              colors=channel.video_manager.colors,
                              colors_to_avoid=channel.video_manager.colors_to_avoid,
                              topics_to_avoid=channel.video_manager.topics_to_avoid)
        except WrongMediaException as x:
            logger.info(x)
            continue

        if clip.duration < channel.config.video_single_video_duration:
            continue
        clip = trim_clip_duration(clip, channel.config.video_single_video_duration)
        videos_list.append(clip)
        used_video_clips.add(clip.filename)
        video = first_fade_out_second_fade_in_all(videos_list, 0.5)
        if video.duration > 60 * 60:
            logger.info("Achieved desired duration of video. Stopping")
            break

    video.set_duration(60 * 60)


@step
def create_shorts_with_voice(text_lines: List[str], voice_over_files: List[str], params: PipelineParams) -> str:
    return shorts_with_voice(params, text_lines, voice_over_files)


@step
def create_basic_youtube_video(text_script: str, is_ssml: bool, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    final_video = channel.create_basic_youtube_video(text_script, is_ssml)
    logger.info(f"Video {final_video}")
    return final_video


if __name__ == '__main__':
    author_funny_facts = [
        "Isaac Newton was born premature and was so small he could fit into a quart-sized mug.",
        "He is said to have invented the cat flap, but there's no evidence of it.",
        "Newton was known to have a great sense of humor and loved telling jokes."
    ]
    author_interesting_facts = [
        "Newton was the first person to describe the laws of motion and the law of gravity.",
        "He also made significant advances in the field of optics, discovering the properties of light and color.",
        "Newton was a member of the Royal Society and served as its president from 1703 to 1727."
    ]
    author_inspiring_facts = [
        "Despite facing many obstacles, Newton persevered in his scientific pursuits and left a lasting legacy in the field of physics.",
        "He once said, 'If I have seen further than others, it is by standing upon the shoulders of giants.'",
        "Newton's dedication to his work and his willingness to question accepted knowledge continues to inspire scientists and thinkers today."
    ]
    used_facts = set()
    for i in range(100):
        print(prepare_extra_label(author_funny_facts, author_interesting_facts, author_inspiring_facts, used_facts))
