import contextlib
from abc import ABC
from typing import Callable, Type

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.model.module import Module
from library.util.module.get import list_module, iter_module


class Modules:
    __all__: dict[str, Module]

    def __init__(self):
        self.__all__ = {}

    def add(self, *modules: Module):
        for module in modules:
            self.__all__[module.pack] = module

    def remove(self, *modules: Module):
        with contextlib.suppress(KeyError):
            for module in modules:
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


class ModulesCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.util.module", "Modules"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.util.module")

    @staticmethod
    def create(_create_type: Type[Modules]) -> Modules:
        return Modules()
