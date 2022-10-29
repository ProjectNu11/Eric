from creart import it

from library.model.module import ModuleMetadata
from library.module.manager.model.module import RemoteModule, RemoteModuleCache
from library.util.module import Modules


def remote_newer(local: ModuleMetadata, remote: ModuleMetadata) -> bool:
    return tuple(map(int, str.split(remote.version, "."))) > tuple(
        map(int, str.split(local.version, "."))
    )


def check_update() -> list[tuple[ModuleMetadata, RemoteModule]]:
    modules: Modules = it(Modules)
    remote: RemoteModuleCache = it(RemoteModuleCache)

    pairs: list[tuple[ModuleMetadata, RemoteModule]] = []

    for module in modules:
        if module in remote:
            if remote_newer(
                module, (remote_module := remote.modules_dict.get(module.pack))
            ):
                pairs.append((module, remote_module))

    return pairs
