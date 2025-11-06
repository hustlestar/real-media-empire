import random

from typing import List

import shutil

import os

import logging
from zenml.steps import step, Output

from common.constants import QUOTE_TXT
from pipelines.params.params_for_pipeline import PipelineParams
from pipelines.you_tube_channel import YouTubeChannel
from text.helpers import pick_random_from_list

logger = logging.getLogger(__name__)


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
def move_to_lake(video_path: str, video_id: str, params: PipelineParams) -> None:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Moving {video_path} from swamp to lake")
    shutil.move(video_path, channel.lake_dir)


@step
def move_to_manual_lake(video_path: str, video_id: str, params: PipelineParams) -> None:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Moving {video_path} from swamp to lake")
    shutil.move(video_path, channel.config.manual_publish_lake_dir)


@step
def upload_video_and_thumbnail_to_youtube(final_video: str, text_script: str, params: PipelineParams) -> Output(video_id=str, thumbnail_url=str):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    video_id, thumbnail_url = channel.upload_to_youtube_video_and_thumbnail(final_video, text_script)
    logger.info(f"Video id {video_id} thumbnail url {thumbnail_url}")
    return video_id, thumbnail_url


@step(enable_cache=False)
def find_youtube_video(params: PipelineParams) -> Output(video_dir=str, video_file_path=str, text_script=str):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.find_unpublished_youtube_video(params.execution_date, is_simple=params.is_simple_publish)


@step(enable_cache=False)
def find_unpublished_manual_shorts(params: PipelineParams) -> Output(video_dir=str, video_file_path=str, text_script=str):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.find_unpublished_manual_shorts()


@step
def mark_video_as_published(video_dir: str, video_id: str, params: PipelineParams) -> None:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.mark_video_as_published(video_dir)


@step
def create_video_meta(
    text_script: str, params: PipelineParams
) -> Output(title=str, description=str, thumbnail_title=str, comment=str, tags=List[str]):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_title_description_thumbnail_title(text_script)


@step
def create_video_meta_for_list(
    text_script: List[str], params: PipelineParams
) -> Output(title=str, description=str, thumbnail_title=str, comment=str, tags=List[str]):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_title_description_thumbnail_title(" ".join(text_script))


@step
def create_thumbnail(thumbnail_title: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_thumbnail(thumbnail_title) if "shorts" not in channel.config.youtube_channel_name.lower() else ""


@step
def upload_video_to_youtube(final_video: str, title: str, description: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Starting YouTube video upload\n{final_video}\n{title}\n{description}")
    video_id = channel.socials_manager.upload_video_to_youtube(final_video, title, description, privacy_status=channel.youtube_privacy_status)
    return video_id


@step
def upload_video_to_youtube_with_tags(final_video: str, title: str, description: str, tags: List[str], params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Starting YouTube video upload\n{final_video}\n{title}\n{description}\n{tags}")
    if len(tags) > 15:
        random_order_list = random.sample(tags, len(tags))
        tags = random_order_list[:15]
        logger.info(f"Picked 15 tags randomly: {tags}")
    video_id = channel.socials_manager.upload_video_to_youtube(
        final_video, title, description, privacy_status=channel.youtube_privacy_status, tags=tags
    )
    return video_id


@step
def upload_thumbnail_to_youtube(thumbnail_image_path: str, video_id: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    if "shorts" not in channel.config.youtube_channel_name.lower():
        logger.info(f"Uploading {thumbnail_image_path} for video {video_id}")
        thumbnail_url = channel.socials_manager.upload_thumbnail_for_youtube(thumbnail_image_path, video_id)
        return thumbnail_url
    else:
        logger.info("Skipping thumbnail upload for #shorts")
        return ""


@step
def add_comment_to_youtube(thumbnail_image_path: str, video_id: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    if channel.youtube_privacy_status == "public":
        comment_id = channel.socials_manager.add_comment_to_youtube(thumbnail_image_path, video_id)
        return comment_id
    else:
        return ""
