from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, exists_module

from library.ui.color import Color


class ColorCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.ui.color", "Color"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.ui.color")

    @staticmethod
    def create(_create_type: type[Color]) -> Color:
        return Color.load().initialize()
