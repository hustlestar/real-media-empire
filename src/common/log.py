import logging.config
import os


def me_init_logger():
    if "src" in os.getcwd():
        path = os.getcwd()
        src_index = path.find("src")  # find the index of "/src" in the path
        src_path = path[: src_index + 3]  # extract the part of the path that ends with "/src"
        logging.config.fileConfig(os.path.join(src_path, "logging.ini"))
