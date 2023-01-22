from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.util.locksmith import LockSmith


class LockSmithCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.util.locksmith", "LockSmith"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.config.group_config")

    @staticmethod
    def create(_create_type: type[LockSmith]) -> LockSmith:
        return LockSmith()
