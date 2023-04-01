import logging
import os.path
from typing import Callable

import click
from zenml.pipelines import pipeline
from zenml.steps import step, BaseParameters, Output

from pipelines.you_tube_channel import YouTubeChannel
from social.you_tube import VALID_PRIVACY_STATUSES
from text import helpers
from util.time import get_now

logger = logging.getLogger(__name__)


class PipelineParams(BaseParameters):
    channel_config_path: str = None
    execution_date: str = None


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
def upload_video_and_thumbnail_to_youtube(final_video: str, text_script: str, params: PipelineParams) -> Output(video_id=str, thumbnail_url=str):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    video_id, thumbnail_url = channel.upload_to_youtube(final_video, text_script)
    logger.info(f"Video id {video_id} thumbnail url {thumbnail_url}")
    return video_id, thumbnail_url


@step
def create_title_description_thumbnail_title(text_script: str, params: PipelineParams) -> Output(title=str, description=str, thumbnail_title=str):
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_title_description_thumbnail_title(text_script)


@step
def create_thumbnail(thumbnail_title: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    return channel.create_thumbnail(thumbnail_title)


@step
def upload_video_to_youtube(final_video: str, title: str, description: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    logger.info(f"Before YouTube upload\n{title}\n{description}")
    video_id = channel.socials_manager.upload_video_to_youtube(final_video, title, description, privacy_status=VALID_PRIVACY_STATUSES[1])
    return video_id


@step
def upload_thumbnail_to_youtube(thumbnail_image_path: str, video_id: str, params: PipelineParams) -> str:
    channel = YouTubeChannel(channel_config_path=params.channel_config_path, execution_date=params.execution_date)
    thumbnail_url = channel.socials_manager.upload_thumbnail_for_youtube(thumbnail_image_path, video_id)
    return thumbnail_url


@pipeline(enable_cache=True)
def safe_simple_video_pipeline(
        build_prompt,
        create_text_script,
        create_basic_youtube_video,
        create_title_description_thumbnail_title,
        upload_video_to_youtube,
        create_thumbnail,
        upload_thumbnail_to_youtube
):
    prompt = build_prompt()
    text_script, is_ssml = create_text_script(prompt)
    final_video = create_basic_youtube_video(text_script, is_ssml)
    title, description, thumbnail_title = create_title_description_thumbnail_title(text_script)
    video_id = upload_video_to_youtube(final_video, title, description)
    thumbnail_image_path = create_thumbnail(thumbnail_title)
    thumbnail_url = upload_thumbnail_to_youtube(thumbnail_image_path, video_id)


def prepare_and_get_pipeline_params(click_ctx, _pipeline_params_class: Callable):
    """
    Helps to create PipelineVariables instance out of click CLI options.

    You might take it as a starting point for your own implementation of PipelineVariables parsing
    """
    click_options_as_dict = {}
    for p in click_ctx.command.params:
        if isinstance(p, click.Option):
            click_options_as_dict[p.name] = click_ctx.params.get(p.name)
    logger.info(f"All click CLI options: {click_options_as_dict}")
    logger.info(f"Pipeline variables class instance {_pipeline_params_class}")
    pipeline_variables = _pipeline_params_class(**click_options_as_dict)
    return pipeline_variables


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option("--execution_date", default=get_now(), help="Pipeline execution date")
@click.option("--channel_config_path", default="", help="Learning rate for training")
@click.option('--recover', '-r', is_flag=True, default=False, help='Recover previous failed run')
@click.argument('other_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(click_context, execution_date: str, channel_config_path, recover, other_args):
    pipeline_params: PipelineParams = prepare_and_get_pipeline_params(click_context, PipelineParams)
    logger.info(f"Pipeline params are:\n{pipeline_params}")
    pipeline_params = recover_last_run_if_required(channel_config_path, pipeline_params, recover)

    pipeline = safe_simple_video_pipeline(
        build_prompt(pipeline_params),
        create_text_script(pipeline_params),
        create_basic_youtube_video(pipeline_params),
        create_title_description_thumbnail_title(pipeline_params),
        upload_video_to_youtube(pipeline_params),
        create_thumbnail(pipeline_params),
        upload_thumbnail_to_youtube(pipeline_params)
    )

    pipeline.run()


def recover_last_run_if_required(channel_config_path, pipeline_params, recover):
    if recover:
        channel = YouTubeChannel(channel_config_path=channel_config_path, is_recover=True)
        channel_dir = os.listdir(channel.channel_root_dir)
        channel_dir.sort(reverse=True)
        logger.info(f"RECOVERING last pipeline run is {channel_dir[0]}")
        pipeline_params = pipeline_params.copy(update={"execution_date": channel_dir[0]})
    return pipeline_params


if __name__ == '__main__':
    main()
