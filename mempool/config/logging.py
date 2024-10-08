import logging


def setup_logger(
    name=None, log_file="mempool/logs/application.log", level=logging.INFO
):
    logger = logging.getLogger(name or __name__)

    if not logger.handlers:
        logger.setLevel(level)

        formatter = logging.Formatter(
            "- %(levelname)s - %(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
