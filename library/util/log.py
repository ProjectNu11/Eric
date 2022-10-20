from datetime import time
from pathlib import Path

from kayaku import create
from loguru import logger

from library.model.config.eric import EricConfig


def setup_logger():
    config = create(EricConfig)
    log_dir = config.path.log
    logger.add(
        Path(log_dir, "{time:YYYY-MM-DD}", "common.log"),
        level="INFO",
        retention=f"{config.log_rotate} days" if config.log_rotate else None,
        encoding="utf-8",
        rotation=time(),
    )
    logger.add(
        Path(log_dir, "{time:YYYY-MM-DD}", "error.log"),
        level="ERROR",
        retention=f"{config.log_rotate} days" if config.log_rotate else None,
        encoding="utf-8",
        rotation=time(),
    )
