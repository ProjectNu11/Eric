from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.util.permission import PermissionRegistry


class PermissionRegistryCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.util.permission", "PermissionRegistry"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.util.permission")

    @staticmethod
    def create(_create_type: type[PermissionRegistry]) -> PermissionRegistry:
        return PermissionRegistry()
