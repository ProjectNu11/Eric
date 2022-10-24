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
