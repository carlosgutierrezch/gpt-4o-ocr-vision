import logging

def set_logging():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format
    )
    return logging.getLogger(__name__)