from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.model.config import GroupConfig


class GroupConfigCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.model.config.group_config", "GroupConfig"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.config.group_config")

    @staticmethod
    def create(_create_type: type[GroupConfig]) -> GroupConfig:
        cfg = GroupConfig()
        cfg.load()
        return cfg
