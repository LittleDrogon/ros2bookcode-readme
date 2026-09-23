"""话题名与日志配置。"""

import logging
import os
from logging.handlers import RotatingFileHandler

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PACKAGE_DIR, "logs")

COLOR_TOPIC = "/camera/color/image_raw"
DETECTION_TOPIC = "/pen_recognition/detections"
ANNOTATED_TOPIC = "/pen_recognition/image"

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def setup_logger(name: str) -> logging.Logger:
    """同时输出到终端和 logs/<name>.log。"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if logger.handlers:
        return logger

    os.makedirs(LOG_DIR, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"{name}.log"),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("日志文件: %s", os.path.join(LOG_DIR, f"{name}.log"))
    return logger
