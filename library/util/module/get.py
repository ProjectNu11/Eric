from pathlib import Path
from typing import Generator

from kayaku import create
from loguru import logger

from library.model.config.state import ModuleState
from library.model.module import ModuleMetadata, Module
from library.util.module.metadata import update_metadata, parse_metadata
from library.util.module.standardize import standardize_structure


def iter_metadata(
    path: Path, *, no_update: bool = False
) -> Generator[ModuleMetadata, None, None]:
    for file in path.iterdir():
        if (
            file.name.startswith("_")
            or file.name.startswith(".")
            or path.suffix == ".py"
            or (file.is_file() and file.suffix != ".py")
        ):
            continue
        try:
            file = standardize_structure(file)
        except ValueError as e:
            logger.error(e)
            continue
        yield parse_metadata(file) if no_update else update_metadata(file)


def list_metadata(path: Path, *, no_update: bool = False) -> list[ModuleMetadata]:
    return list(iter_metadata(path, no_update=no_update))


def iter_module(
    path: Path, *, no_update: bool = False
) -> Generator[Module, None, None]:
    state: ModuleState = create(ModuleState)
    for metadata in iter_metadata(path, no_update=no_update):
        yield Module(**metadata.dict(), loaded=state.loaded.get(metadata.pack, False))


def list_module(path: Path, *, no_update: bool = False) -> list[Module]:
    return list(iter_module(path, no_update=no_update))
