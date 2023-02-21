from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.util.user_profile import UserRegistry


class UserRegistryCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.util.user_profile", "UserRegistry"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.util.user_profile")

    @staticmethod
    def create(_create_type: type[UserRegistry]) -> UserRegistry:
        return UserRegistry()
