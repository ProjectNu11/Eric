from pathlib import Path
from typing import Iterable

from creart import it
from graia.saya import Saya

from library.model.module import ModuleMetadata, Module
from library.util.misc import inflate
from library.util.module.get_all import list_module


def require_by_dir(base_dir: Path):
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in list_module(base_dir):
            saya.require(module.pack)


def require_by_metadata(*metadata: ModuleMetadata | Iterable[ModuleMetadata]):
    modules: list[ModuleMetadata] = inflate(metadata)
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in modules:
            saya.require(module.pack)


def require(*modules: Module | Iterable[Module]):
    require_by_metadata([module for module in inflate(modules) if module.loaded])
