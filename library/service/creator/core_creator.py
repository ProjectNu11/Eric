from abc import ABC
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.model.core import EricCore


class EricCoreCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.model.core", "EricCore"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.core")

    @staticmethod
    def create(_create_type: Type[EricCore]) -> EricCore:
        return EricCore()
