from creart import it

from library.module.manager.model.module import RemoteModule, RemoteModuleCache


def search(name: str) -> RemoteModule | None:
    cache = it(RemoteModuleCache)
    if result := list(
        filter(
            lambda module: any(
                [
                    name.lower() == module.name.lower(),
                    name.lower() == module.pack.lower().split(".")[-1],
                    name.lower() == module.name.lower().replace(" ", "").split(".")[-1],
                ]
            ),
            cache.modules,
        )
    ):
        return result[0]
    return None


def bulk_search(*names: str) -> tuple[list[RemoteModule], list[str]]:
    found: list[RemoteModule] = []
    not_found: list[str] = []
    for name in names:
        if module := search(name):
            found.append(module)
        else:
            not_found.append(name)
    return found, not_found
