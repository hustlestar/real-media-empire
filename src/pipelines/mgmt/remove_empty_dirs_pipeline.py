import click
import logging
from zenml.pipelines import pipeline

from pipelines.params.mgmt_params import MgmtParams
from pipelines.params.params_for_pipeline import PipelineParams, prepare_and_get_pipeline_params
from pipelines.steps.os_steps import remove_empty_dirs

logger = logging.getLogger(__name__)


@pipeline(enable_cache=True)
def remove_empty_dirs_pipeline(
    remove_empty_dirs,
):
    remove_empty_dirs()


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option("--starting_dir", default="", help="Starting dir")
@click.argument("other_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def main(click_context, starting_dir, other_args):
    pipeline_params: PipelineParams = prepare_and_get_pipeline_params(click_context, MgmtParams)
    logger.info(f"Pipeline params are:\n{pipeline_params}")

    pipeline = remove_empty_dirs_pipeline(
        remove_empty_dirs(pipeline_params),
    )

    pipeline.run()


if __name__ == "__main__":
    main()
