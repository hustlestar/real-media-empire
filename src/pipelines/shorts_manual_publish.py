import click
import logging
from zenml.pipelines import pipeline

from pipelines.params.params_for_pipeline import PipelineParams, prepare_and_get_pipeline_params
from pipelines.steps.publish_steps import (
    create_video_meta,
    upload_video_to_youtube_with_tags,
    add_comment_to_youtube,
    find_unpublished_manual_shorts,
    move_to_manual_lake,
)
from pipelines.utils import recover_last_run_if_required
from util.time import get_now

logger = logging.getLogger(__name__)


@pipeline(enable_cache=True)
def shorts_manual_publish_pipeline(
    find_unpublished_manual_shorts,
    create_title_description_thumbnail_title,
    upload_video_to_youtube_with_tags,
    add_comment_to_youtube,
    move_to_manual_lake,
):
    video_dir, video_file_path, text_script = find_unpublished_manual_shorts()
    title, description, thumbnail_title, comment, tags = create_title_description_thumbnail_title(text_script)
    video_id = upload_video_to_youtube_with_tags(video_file_path, title, description, tags)
    add_comment_to_youtube(comment, video_id)
    move_to_manual_lake(video_file_path, video_id)


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option("--execution_date", default=get_now(), help="Pipeline execution date")
@click.option("--channel_config_path", default="", help="Learning rate for training")
@click.option("--recover", "-r", is_flag=True, default=False, help="Recover previous failed run")
@click.argument("other_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(click_context, execution_date: str, channel_config_path, recover, other_args):
    pipeline_params: PipelineParams = prepare_and_get_pipeline_params(click_context, PipelineParams)
    logger.info(f"Pipeline params are:\n{pipeline_params}")
    pipeline_params = recover_last_run_if_required(channel_config_path, pipeline_params, recover)

    pipeline = shorts_manual_publish_pipeline(
        find_unpublished_manual_shorts(pipeline_params),
        create_video_meta(pipeline_params),
        upload_video_to_youtube_with_tags(pipeline_params),
        add_comment_to_youtube(pipeline_params),
        move_to_manual_lake(pipeline_params),
    )

    pipeline.run()


if __name__ == "__main__":
    main()
