# TODO Placeholder for actual module requiring
from pathlib import Path
from typing import Iterable

from creart import it
from graia.saya import Saya

from library.model.module import ModuleMetadata
from library.util.module.get_all import list_all


def require_by_dir(base_dir: Path):
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in list_all(base_dir):
            saya.require(module.pack)


def require_by_metadata(*metadata: ModuleMetadata | Iterable[ModuleMetadata]):
    modules: list[ModuleMetadata] = []
    for m in metadata:
        if isinstance(m, ModuleMetadata):
            modules.append(m)
        else:
            modules.extend(m)
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in modules:
            saya.require(module.pack)
