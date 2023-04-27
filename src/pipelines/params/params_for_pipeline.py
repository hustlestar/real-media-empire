import logging
from typing import Callable

import click
from zenml.steps import BaseParameters

logger = logging.getLogger(__name__)


class PipelineParams(BaseParameters):
    channel_config_path: str = None
    execution_date: str = None
    number_of_videos: int = None
    is_split_quote: bool = False


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
