from abc import ABC
from typing import Type

from creart import CreateTargetInfo, AbstractCreator, exists_module, add_creator
from kayaku import create

from library.model.config.service.manager import ManagerConfig
from library.model.repo import GenericPluginRepo


class ParsedRepository:
    __all__: list[GenericPluginRepo]

    def __init__(self):
        mgr_cfg: ManagerConfig = create(ManagerConfig)
        self.__all__ = sorted(list(set(mgr_cfg.parse_repo())), key=lambda r: r.__name__)

    def __iter__(self):
        return iter(self.__all__)


class ParsedRepositoryCreator(AbstractCreator, ABC):
    targets = (
        CreateTargetInfo("library.module.manager.model.repository", "ParsedRepository"),
    )

    @staticmethod
    def available() -> bool:
        return exists_module("library.module.manager.model.repository")

    @staticmethod
    def create(_create_type: Type[ParsedRepository]) -> ParsedRepository:
        return ParsedRepository()


add_creator(ParsedRepositoryCreator)
