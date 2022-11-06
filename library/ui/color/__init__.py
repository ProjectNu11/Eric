from abc import ABC
from datetime import datetime
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module
from pydantic import BaseModel
from typing_extensions import Self

from library.ui.color.schema import ColorSchema, ColorSingle


class Color(BaseModel):
    schemas: dict[str, ColorSchema] = {"default": ColorSchema()}
    colors: dict[str, ColorSingle] = {}
    current_using: str = "default"

    def initialize(self) -> Self:
        self.colors |= {
            "red": ColorSingle(color=(255, 0, 0)),
            "green": ColorSingle(color=(0, 255, 0)),
            "blue": ColorSingle(color=(0, 0, 255)),
            "yellow": ColorSingle(color=(255, 255, 0)),
            "cyan": ColorSingle(color=(0, 255, 255)),
            "magenta": ColorSingle(color=(255, 0, 255)),
            "white": ColorSingle(color=(255, 255, 255)),
            "black": ColorSingle(color=(0, 0, 0)),
            "grey": ColorSingle(color=(128, 128, 128)),
            "orange": ColorSingle(color=(255, 192, 0)),
            "purple": ColorSingle(color=(192, 0, 192)),
            "brown": ColorSingle(color=(192, 96, 0)),
            "pink": ColorSingle(color=(255, 192, 224)),
            "turquoise": ColorSingle(color=(0, 192, 192)),
            "lime": ColorSingle(color=(192, 255, 0)),
            "maroon": ColorSingle(color=(128, 0, 0)),
            "navy": ColorSingle(color=(0, 0, 128)),
            "olive": ColorSingle(color=(128, 128, 0)),
            "teal": ColorSingle(color=(0, 128, 128)),
            "silver": ColorSingle(color=(192, 192, 192)),
            "violet": ColorSingle(color=(128, 0, 128)),
        }
        return self

    def current(self) -> ColorSchema:
        return self.get_schema(self.current_using)

    def get_schema(self, name: str = None) -> ColorSchema:
        return self.current() if name is None else self.schemas[name]

    def get_color(self, name: str) -> ColorSingle:
        return self.colors[name]

    def mix_color(
        self, *colors: ColorSingle | str | tuple[int, int, int]
    ) -> ColorSingle:
        colors = [
            self.get_color(color)
            if isinstance(color, str)
            else ColorSingle(color=color)
            if isinstance(color, tuple)
            else color
            for color in colors
        ]
        return ColorSingle(
            color=tuple(
                map(lambda x: sum(x) // len(x), zip(*[color.color for color in colors]))
            )
        )


class ColorCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.ui.color", "Color"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.ui.color")

    @staticmethod
    def create(_create_type: Type[Color]) -> Color:
        return Color().initialize()


def is_dark() -> bool:
    return not (6 <= datetime.now().hour < 18)
