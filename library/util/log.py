from datetime import time
from pathlib import Path

from kayaku import create
from loguru import logger

from library.model.config import EricConfig, PathConfig


def setup_logger():
    config: EricConfig = create(EricConfig)
    path_config: PathConfig = create(PathConfig)
    log_dir = path_config.log
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
