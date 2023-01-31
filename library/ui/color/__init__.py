from abc import ABC
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path

from creart import AbstractCreator, CreateTargetInfo, exists_module
from kayaku import create
from loguru import logger
from pydantic import BaseModel, ValidationError
from typing_extensions import Self

from library.model.config import DataPathConfig
from library.ui.color.schema import ColorSchema, ColorSingle

config: DataPathConfig = create(DataPathConfig)


class Color(BaseModel):
    schemas: dict[str, ColorSchema] = {"default": ColorSchema()}
    colors: dict[str, ColorSingle] = {}
    current_using: str = "default"

    @classmethod
    def load(cls) -> Self:
        path = Path(config.library) / "color.json"
        try:
            return cls.parse_file(path)
        except (FileNotFoundError, ValidationError, JSONDecodeError):
            logger.error("[Color] Failed to load color config, using default config.")
            return cls()

    def save(self):
        path = Path(config.library) / "color.json"
        path.write_text(self.json(ensure_ascii=False))

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

    def register_schema(
        self, name: str, color_schema: ColorSchema, *, update: bool = True
    ):
        if name in self.schemas:
            if not update:
                raise ValueError(f"[Color] Schema {name} already exists")
            logger.warning(f"[Color] Schema {name} already exists, updating")
        self.schemas[name] = color_schema
        self.save()

    def register_color(self, name: str, color: ColorSingle, *, update: bool = True):
        if name in self.colors:
            if not update:
                raise ValueError(f"[Color] Color {name} already exists")
            logger.warning(f"[Color] Color {name} already exists, updating")
        self.colors[name] = color
        self.save()

    def set_current(self, name: str):
        if name not in self.schemas:
            raise ValueError(f"[Color] Schema {name} not exists")
        self.current_using = name
        self.save()


class ColorCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.ui.color", "Color"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.ui.color")

    @staticmethod
    def create(_create_type: type[Color]) -> Color:
        return Color.load().initialize()


def is_dark() -> bool:
    return not (6 <= datetime.now().hour < 18)
