import json
import logging
import os
import re
import shutil
from typing import List

from zenml.steps import step, Output

from common.exception import WrongMediaException
from config import CONFIG
from pipelines.params.params_for_pipeline import PipelineParams
from pipelines.you_tube_channel import YouTubeChannel
from text import helpers
from text.helpers import pick_random_from_list, finish_line, TemplateArg
from util.time import get_now
from video.movie import LineToMp3File, video_with_text, trim_clip_duration, video_with_text_full_sentence, video_with_text_full_sentence_many_clips, \
    BG_CLIP_STRATEGIES
from video.utils import is_video_matching, read_n_video_clips
from video.video_transitions import first_fade_out_second_fade_in_all

QUOTE_TXT = "1_quote.txt"

logger = logging.getLogger(__name__)


@step
def build_prompt(params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    prompt = helpers.build_prompt(
        channel.config.main_prompt_template,
        channel.config.main_prompt_topics_file,
        narrative_types=channel.config.main_prompt_narrative_types,
        engagement_techniques=channel.config.main_prompt_engagement_techniques,
    )
    return prompt


@step
def create_quote_by_author(params: PipelineParams) -> List[str]:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    author = pick_random_from_list(json.loads(open(channel.config.main_prompt_topics_file).read())['authors'])
    topic = pick_random_from_list(channel.config.main_prompt_narrative_types)
    prompt_params = {
        "topic": topic,
        "author": author,
        "main_idea": ""
    }
    args = [
        TemplateArg(
            text_definition="field named quote having [[topic]] by [[author]] as string. It shouldn't be well known or popular, it should be random",
            json_field_name='quote',
            value='\"\"'
        ),
        TemplateArg(
            text_definition="field named author having author of quote",
            json_field_name='author',
            value='\"\"'
        ),
    ]
    quote_dict = helpers.create_result_dict_from_prompt_template(
        channel.config.main_prompt_template,
        args,
        prompt_params,
    )
    quote = quote_dict.get("quote")
    logger.info(f"Result quote is\n{quote}")
    quote_lines = [finish_line(s) for s in quote.split(".") if s]
    result = helpers.prepare_short_lines(quote_lines)

    with open(os.path.join(channel.result_dir, f"{QUOTE_TXT}"), "w") as k:
        k.write(f"{quote} {finish_line(author)}")

    result.append(quote_dict.get("author"))
    for l in result:
        logger.info(l)
    return result


@step
def use_predefined_quote_by_author(params: PipelineParams) -> List[str]:
    return predefined_quote_by_author(params)


def predefined_quote_by_author(params):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    quote_file = pick_random_from_list(channel.config.all_extras.get("quote_sources"))
    with open(quote_file) as f:
        all_authors = json.loads(f.read())
    single_author = pick_random_from_list(all_authors)
    quote = pick_random_from_list(single_author.get('quotes'))
    logger.info(f"Result quote is\n{quote}")
    quote_lines = [finish_line(s) for s in quote.split(".") if s]
    result = quote_lines if not params.is_split_quote else helpers.prepare_short_lines(quote_lines)
    result.append(finish_line(single_author.get("author")))
    with open(os.path.join(channel.result_dir, f"{QUOTE_TXT}"), "w") as k:
        k.write(f"{quote} {single_author.get('author')}")
    for l in result:
        logger.info(l)
    return result


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
def find_shorts_in_swamp(params: PipelineParams) -> Output(video_path=str, quote=str):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    part_to_count = {}

    files_in_dir = os.listdir(channel.swamp_dir)
    for f in files_in_dir:
        filename_parts = f.split("_", maxsplit=2)
        part_to_count[filename_parts[0]] = part_to_count.get(filename_parts[0]) + 1 if part_to_count.get(filename_parts[0]) else 1

    filtered_files = []
    for part, times in part_to_count.items():
        if times == 1:
            filtered_files.append([f for f in files_in_dir if f.startswith(part)][0])

    logger.info(f"All filtered files {filtered_files}")
    if not filtered_files:
        raise Exception("NOT FOUND ANY CENSORED SHORTS IN THE SWAMP - PLEASE SORT AND REMOVE GARBAGE FIRTS")
    random_filtered_video = pick_random_from_list(filtered_files)

    start_part = random_filtered_video.split("_", maxsplit=2)[0]
    video_dir = channel.build_result_dir(start_part)
    with open(os.path.join(video_dir, QUOTE_TXT)) as q:
        quote = q.read()
    return os.path.join(channel.swamp_dir, random_filtered_video), quote


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


def read_video_for_channel(channel):
    return read_n_video_clips(os.path.join(CONFIG.get('MEDIA_GALLERY_DIR'),
                                           "VIDEO",
                                           channel.config.video_orientation,
                                           f"{channel.config.video_width}_{channel.config.video_height}"), 1)[0]


@step
def create_voice_overs(text_lines: List[str], params: PipelineParams) -> List[str]:
    return voice_overs(params, text_lines)


def voice_overs(params, text_lines):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    channel.socials_manager.youtube_uploader.authenticate()
    return [channel.audio_manager.create_audio_voice_over(line, is_ssml=False, result_file=f"{i}_voiceover.mp3", speaking_rate=channel.config.voice_over_speed)
            for i, line in enumerate(text_lines)]


@step
def create_shorts_with_voice(text_lines: List[str], voice_over_files: List[str], params: PipelineParams) -> str:
    return shorts_with_voice(params, text_lines, voice_over_files)


def shorts_with_voice(params, text_lines, voice_over_files, is_swamp=False):
    from video.utils import find_matching_video
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    for i in range(len(BG_CLIP_STRATEGIES)):
        try:
            clean_text = re.sub(r"[^a-zA-Z]+", " ", " ".join(text_lines))
            clean_text = re.sub(r"\\s+", "_", clean_text).lower()

            result_video_filename = build_file_name(clean_text, channel, i, is_swamp, params)

            lines = [LineToMp3File(k, v) for k, v in zip(text_lines, voice_over_files)]
            bg_audio_filename = os.path.join(channel.config.audio_background_dir_path, pick_random_from_list(os.listdir(channel.config.audio_background_dir_path)))
            if params.is_split_quote:
                bg_video = find_matching_video(channel)
                logger.warning(f"Split quote is used for text preparation.")
                video_with_text(bg_video,
                                lines,
                                result_file=result_video_filename,
                                fonts_list=channel.config.video_fonts_list,
                                bg_audio_filename=bg_audio_filename,
                                text_colors=channel.config.video_text_color_list
                                )
            else:
                for s in BG_CLIP_STRATEGIES:
                    video_with_text_full_sentence_many_clips(
                        channel,
                        lines,
                        result_file=build_file_name(clean_text, channel, i, is_swamp, params, bg_clip_strategy=s),
                        fonts_list=channel.config.video_fonts_list,
                        bg_audio_filename=bg_audio_filename,
                        text_colors=channel.config.video_text_color_list,
                        bg_clip_strategy=s,
                        single_clip_duration=2
                    )
        except Exception as x:
            logger.error(f"Error while creating video {i}", x)
            continue
    return result_video_filename


def build_file_name(clean_text, channel, i, is_swamp, params, bg_clip_strategy=""):
    return os.path.join(
        channel.swamp_dir if is_swamp else channel.result_dir,
        f"{params.execution_date}_{clean_text}_{bg_clip_strategy}_{i}.mp4"
    )


@step
def create_text_script(prompt: str, params: PipelineParams) -> Output(text_script=str, is_ssml=bool):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    text_script, is_ssml = channel.create_text_script(prompt)
    return text_script, is_ssml


@step
def create_basic_youtube_video(text_script: str, is_ssml: bool, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    final_video = channel.create_basic_youtube_video(text_script, is_ssml)
    logger.info(f"Video {final_video}")
    return final_video


@step
def move_to_lake(video_path: str, video_id: str, params: PipelineParams) -> None:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Moving {video_path} from swamp to lake")
    shutil.move(video_path, channel.lake_dir)


@step
def upload_video_and_thumbnail_to_youtube(final_video: str, text_script: str, params: PipelineParams) -> Output(video_id=str, thumbnail_url=str):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    video_id, thumbnail_url = channel.upload_to_youtube_video_and_thumbnail(final_video, text_script)
    logger.info(f"Video id {video_id} thumbnail url {thumbnail_url}")
    return video_id, thumbnail_url


@step
def create_video_meta(text_script: str, params: PipelineParams) \
        -> Output(title=str, description=str, thumbnail_title=str, comment=str, tags=List[str]):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_title_description_thumbnail_title(text_script)


@step
def create_video_meta_for_list(text_script: List[str], params: PipelineParams) \
        -> Output(title=str, description=str, thumbnail_title=str, comment=str, tags=List[str]):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_title_description_thumbnail_title(" ".join(text_script))


@step
def create_thumbnail(thumbnail_title: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_thumbnail(thumbnail_title)


@step
def upload_video_to_youtube(final_video: str, title: str, description: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Starting YouTube video upload\n{final_video}\n{title}\n{description}")
    video_id = channel.socials_manager.upload_video_to_youtube(final_video, title, description, privacy_status=channel.youtube_privacy_status)
    return video_id


@step
def upload_thumbnail_to_youtube(thumbnail_image_path: str, video_id: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Uploading {thumbnail_image_path} for video {video_id}")
    thumbnail_url = channel.socials_manager.upload_thumbnail_for_youtube(thumbnail_image_path, video_id)
    return thumbnail_url


@step
def add_comment_to_youtube(thumbnail_image_path: str, video_id: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    if channel.youtube_privacy_status == 'public':
        comment_id = channel.socials_manager.add_comment_to_youtube(thumbnail_image_path, video_id)
        return comment_id
    else:
        return ''
