import logging

import click
from zenml.pipelines import pipeline

from pipelines.params.params_for_pipeline import PipelineParams, prepare_and_get_pipeline_params
from pipelines.steps.library import generate_quotes_video
from pipelines.utils import recover_last_run_if_required
from util.time import get_now

logger = logging.getLogger(__name__)


@pipeline(enable_cache=True)
def generate_quotes_video_pipeline(
        generate_quotes_video,
):
    generate_quotes_video()


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option("--execution_date", default=get_now(), help="Pipeline execution date")
@click.option("--channel_config_path", default="", help="Learning rate for training")
@click.option("--number_of_videos", default=1, help="Learning rate for training")
@click.option('--is_split_quote', '-s', is_flag=True, default=False, help='To split quote or not')
@click.option('--recover', '-r', is_flag=True, default=False, help='Recover previous failed run')
@click.argument('other_args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(click_context, execution_date: str, channel_config_path, number_of_videos, is_split_quote, recover, other_args):
    pipeline_params: PipelineParams = prepare_and_get_pipeline_params(click_context, PipelineParams)
    logger.info(f"Pipeline params are:\n{pipeline_params}")
    pipeline_params = recover_last_run_if_required(channel_config_path, pipeline_params, recover)

    pipeline = generate_quotes_video_pipeline(
        generate_quotes_video(pipeline_params),
    )

    pipeline.run()


if __name__ == '__main__':
    main()
