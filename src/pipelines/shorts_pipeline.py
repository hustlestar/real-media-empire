import logging

import click
from zenml.pipelines import pipeline

from pipelines.params.params_for_pipeline import PipelineParams, prepare_and_get_pipeline_params
from pipelines.steps.library import create_quote_by_author, create_shorts_with_voice, create_voice_overs, upload_video_to_youtube, \
    add_comment_to_youtube, create_title_description_thumbnail_title_for_list
from pipelines.utils import recover_last_run_if_required
from util.time import get_now

logger = logging.getLogger(__name__)


@pipeline(enable_cache=True)
def shorts_video_pipeline(
        create_quote_by_author,
        create_voice_overs,
        create_shorts_with_voice,
        create_title_description_thumbnail_title_for_list,
        upload_video_to_youtube,
        add_comment_to_youtube
):
    lines_list = create_quote_by_author()
    mp3_files = create_voice_overs(lines_list)
    final_video = create_shorts_with_voice(lines_list, mp3_files)
    title, description, thumbnail_title, comment = create_title_description_thumbnail_title_for_list(lines_list)
    video_id = upload_video_to_youtube(final_video, title, description)
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

    pipeline = shorts_video_pipeline(
        create_quote_by_author(pipeline_params),
        create_voice_overs(pipeline_params),
        create_shorts_with_voice(pipeline_params),
        create_title_description_thumbnail_title_for_list(pipeline_params),
        upload_video_to_youtube(pipeline_params),
        add_comment_to_youtube(pipeline_params),
    )

    pipeline.run()


if __name__ == '__main__':
    main()
