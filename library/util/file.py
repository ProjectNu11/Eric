from pathlib import Path

from loguru import logger


def remove_recursive(path: Path):
    if path.is_dir():
        for child in path.iterdir():
            remove_recursive(child)
        path.rmdir()
        logger.success(f"已移除目录 {path}")
        return
    while path.is_file():
        path.unlink()
    logger.success(f"已移除文件 {path}")
