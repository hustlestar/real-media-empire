import logging
import os

from pipelines.you_tube_channel import YouTubeChannel

logger = logging.getLogger(__name__)


def recover_last_run_if_required(channel_config_path, pipeline_params, recover):
    if recover:
        channel = YouTubeChannel(channel_config_path=channel_config_path, is_recover=True)
        channel_dir = os.listdir(channel.channel_root_dir)
        channel_dir.sort(reverse=True)
        logger.info(f"RECOVERING last pipeline run is {channel_dir[0]}")
        pipeline_params = pipeline_params.copy(update={"execution_date": channel_dir[0]})
    return pipeline_params
