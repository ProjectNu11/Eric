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


def walk(path: Path, include_dir: bool = True):
    if path.is_file():
        yield path
    for sub in path.iterdir():
        if path.is_dir():
            yield from walk(sub)
            if include_dir:
                yield path
        elif path.is_file():
            yield path


def get_size(path: Path):
    return sum(file.stat().st_size for file in walk(path, include_dir=False))
