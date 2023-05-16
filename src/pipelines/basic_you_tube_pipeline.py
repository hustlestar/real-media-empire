import logging

import click
from zenml.pipelines import pipeline

from pipelines.params.params_for_pipeline import PipelineParams, prepare_and_get_pipeline_params
from pipelines.steps.library import build_prompt, create_text_script, create_basic_youtube_video, create_video_meta, create_thumbnail, \
    upload_thumbnail_to_youtube, add_comment_to_youtube, upload_video_to_youtube_with_tags
from pipelines.utils import recover_last_run_if_required
from util.time import get_now

logger = logging.getLogger(__name__)


@pipeline(enable_cache=True)
def safe_simple_video_pipeline(
        build_prompt,
        create_text_script,
        create_basic_youtube_video,
        create_video_meta,
        upload_video_to_youtube_with_tags,
        create_thumbnail,
        upload_thumbnail_to_youtube,
        add_comment_to_youtube
):
    prompt = build_prompt()
    text_script, is_ssml = create_text_script(prompt)
    final_video = create_basic_youtube_video(text_script, is_ssml)
    title, description, thumbnail_title, comment, tags = create_video_meta(text_script)
    video_id = upload_video_to_youtube_with_tags(final_video, title, description, tags)
    thumbnail_image_path = create_thumbnail(thumbnail_title)
    thumbnail_url = upload_thumbnail_to_youtube(thumbnail_image_path, video_id)
    add_comment_to_youtube(comment, video_id)


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
        create_video_meta(pipeline_params),
        upload_video_to_youtube_with_tags(pipeline_params),
        create_thumbnail(pipeline_params),
        upload_thumbnail_to_youtube(pipeline_params),
        add_comment_to_youtube(pipeline_params),
    )

    pipeline.run()


if __name__ == '__main__':
    main()
