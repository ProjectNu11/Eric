from creart import it

from library.model.module import Module
from library.util.module import Modules


def search_module(name: str) -> Module | None:
    if result := it(Modules).search(
        lambda module: any(
            [
                name.lower() == module.name.lower(),
                name.lower() == module.pack.lower().split(".")[-1],
                name.lower() == module.name.lower().replace(" ", "").split(".")[-1],
            ]
        )
    ):
        return result[0]
    return None


def bulk_search_module(*names: str) -> tuple[list[Module], list[str]]:
    found: list[Module] = []
    not_found: list[str] = []
    for name in names:
        if module := search_module(name):
            found.append(module)
        else:
            not_found.append(name)
    return found, not_found
