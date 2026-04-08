import logging
import os

def create_logger(log_file):

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger("steganography")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger