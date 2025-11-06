import logging
from zenml.steps import BaseParameters

logger = logging.getLogger(__name__)


class MgmtParams(BaseParameters):
    starting_dir: str = None
    voiceover_json: str = None
    results_dir: str = None
    channel_config_path: str = None
