import logging
import os
from zenml.steps import step

from pipelines.params.mgmt_params import MgmtParams

logger = logging.getLogger(__name__)


@step
def remove_empty_dirs(params: MgmtParams) -> None:
    logger.info(f"Starting empty dir cleanup in: {params.starting_dir}")
    delete_empty_dirs(params.starting_dir)
    logger.info("Finished shorts generation")


def delete_empty_dirs(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                except Exception as x:
                    logger.info(f"Failed to delete empty directory: {dir_path}")
                logger.info(f"Deleted empty directory: {dir_path}")
