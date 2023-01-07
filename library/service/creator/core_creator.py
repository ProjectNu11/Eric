from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.model.core import EricCore


class EricCoreCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.model.core", "EricCore"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.core")

    @staticmethod
    def create(_create_type: type[EricCore]) -> EricCore:
        return EricCore()
