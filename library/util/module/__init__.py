from typing import Callable

from library.model.module import Module


class Modules:
    __all__: dict[str, Module]

    def __init__(self):
        self.__all__ = {}

    def add(self, module: Module):
        self.__all__[module.pack] = module

    def remove(self, module: Module):
        del self.__all__[module.pack]

    def get(self, pack: str) -> Module:
        return self.__all__[pack]

    def search(self, *criterion: Callable[[Module], bool]) -> list[Module]:
        result = []
        for criteria in criterion:
            result.extend(
                [
                    module
                    for module in self.__all__.values()
                    if criteria(module) and module not in result
                ]
            )
        return result
