from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.util.session_container import SessionContainer


class SessionContainerCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.util.session_container", "SessionContainer"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.config.group_config")

    @staticmethod
    def create(_create_type: type[SessionContainer]) -> SessionContainer:
        return SessionContainer()
