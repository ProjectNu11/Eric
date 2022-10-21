from pathlib import Path

from loguru import logger


def standardize_structure(path: Path):
    if path.is_dir():
        return
    if path.suffix != ".py":
        return
    new_path = path.parent / path.stem
    new_path.mkdir(exist_ok=True)
    path.rename(new_path / "__init__.py")
    logger.info(f"Standardized {path} to {new_path}")
    return
