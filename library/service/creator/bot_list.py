from abc import ABC
from json import JSONDecodeError
from pathlib import Path

from creart import AbstractCreator, CreateTargetInfo, exists_module
from kayaku import create
from pydantic import ValidationError

from library.model.bot_list import BotList
from library.model.config import DataPathConfig


class BotListCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.model.bot_list", "BotList"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.bot_list")

    @staticmethod
    def create(_create_type: type[BotList]) -> BotList:
        path_cfg: DataPathConfig = create(DataPathConfig)
        try:
            bot_list = BotList.parse_file(Path(path_cfg.library) / "bot_list.json")
            bot_list.sources.clear()
            return bot_list
        except (FileNotFoundError, ValidationError, JSONDecodeError):
            return BotList()
