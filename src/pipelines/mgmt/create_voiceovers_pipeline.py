import click
import logging
from zenml.pipelines import pipeline

from pipelines.params.mgmt_params import MgmtParams
from pipelines.params.params_for_pipeline import PipelineParams, prepare_and_get_pipeline_params
from pipelines.steps.audio_steps import batch_create_voiceover

logger = logging.getLogger(__name__)


@pipeline(enable_cache=True)
def create_voiceovers_pipeline(
    batch_create_voiceover,
):
    batch_create_voiceover()


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option("--voiceover_json", default="", help="Starting dir")
@click.option("--results_dir", default="", help="Results dir")
@click.option("--channel_config_path", default="", help="Channel config path")
@click.argument("other_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(click_context, voiceover_json, results_dir, channel_config_path, other_args):
    pipeline_params: PipelineParams = prepare_and_get_pipeline_params(click_context, MgmtParams)
    logger.info(f"Pipeline params are:\n{pipeline_params}")

    pipeline = create_voiceovers_pipeline(
        batch_create_voiceover(pipeline_params),
    )

    pipeline.run()


if __name__ == "__main__":
    main()
