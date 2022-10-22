from pathlib import Path
from typing import Generator

from loguru import logger

from library.model.module import ModuleMetadata
from library.util.module.metadata import update_metadata
from library.util.module.standardize import standardize_structure


def iter_all(path: Path) -> Generator[ModuleMetadata, None, None]:
    for file in path.iterdir():
        if (
            file.name.startswith("_")
            or file.name.startswith(".")
            or path.suffix == ".py"
            or file.name == "metadata.json"
        ):
            continue
        try:
            file = standardize_structure(file)
        except ValueError as e:
            logger.error(e)
            continue
        yield update_metadata(file)


def list_all(path: Path) -> list[ModuleMetadata]:
    return list(iter_all(path))
