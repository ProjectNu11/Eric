import contextlib
from abc import ABC
from typing import Callable, Type

from creart import AbstractCreator, CreateTargetInfo, exists_module
from loguru import logger

from library.model.exception import RequirementResolveFailed
from library.model.module import Module
from library.util.module.get import list_module, iter_module


class Modules:
    __all__: dict[str, Module]
    __ordered__: list[Module]

    def __init__(self):
        self.__all__ = {}

    def __iter__(self):
        return iter(self.__ordered__)

    def __len__(self):
        return len(self.__all__)

    @property
    def all(self):
        return self.__all__

    @property
    def ordered(self):
        return self.__ordered__

    def add(self, *modules: Module):
        for module in modules:
            self.__all__[module.pack] = module
        self.resolve()

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

    def resolve(self, *, dry_run: bool = False) -> list[Module]:
        resolved: set[str] = set()
        unresolved: set[Module] = set(self.__all__.values())
        result: list[Module] = []

        while unresolved:
            layer = {
                module for module in unresolved if set(module.required) <= resolved
            }
            if not layer:
                raise RequirementResolveFailed(unresolved)
            unresolved -= layer
            resolved |= {module.pack for module in layer}
            result.extend(layer)

        if dry_run:
            return result
        self.__ordered__ = result
        logger.success("[Modules] 解析模块依赖完成")
        return result


class ModulesCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.util.module", "Modules"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.util.module")

    @staticmethod
    def create(_create_type: Type[Modules]) -> Modules:
        return Modules()
