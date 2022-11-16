from abc import abstractmethod
from pathlib import Path

from graia.ariadne.model import Member, Friend
from kayaku import create
from loguru import logger
from pydantic import BaseModel

from library.model.config.path import DataPathConfig


class BotType(BaseModel):
    name: str
    repo: str = ""

    def __str__(self):
        return self.name


class Bot(BaseModel):
    id: int
    nickname: str = "Unknown"
    maintainers: set[str] = set()
    type: BotType = BotType(name="Unknown")

    def __int__(self):
        return self.id

    def __str__(self):
        return self.nickname


class BotSource(BaseModel):
    name: str = "UnknownSource"
    url: str

    def __str__(self):
        return self.url

    @abstractmethod
    async def fetch(self) -> set[Bot]:
        pass


class BotList(BaseModel):
    sources: set[BotSource] = []
    bots: set[Bot] = []

    def register_source(self, source: BotSource, no_assert: bool = False):
        assert (
            no_assert or source not in self.sources
        ), f"BotSource {source.url} already exists"
        self.sources.add(source)

    def unregister_source(self, source: str | BotSource, no_assert: bool = False):
        source: str = str(source)
        assert no_assert or set(
            filter(lambda s: str(s) == source, self.sources)
        ), f"BotSource {source} doesn't exist"
        self.sources = set(filter(lambda s: str(s) != source, self.sources))

    def register_bot(self, bot: Bot, no_assert: bool = False):
        assert no_assert or bot not in self.bots, f"Bot {bot.id} already exists"
        self.bots.add(bot)

    def unregister_bot(
        self, bot: Bot | str | int | Member | Friend, no_assert: bool = False
    ):
        bot: int = int(bot)
        assert no_assert or set(
            filter(lambda b: int(b) == bot, self.bots)
        ), f"Bot {bot} doesn't exist"
        self.bots = set(filter(lambda b: int(b) != bot, self.bots))

    async def fetch_all(self):
        logger.info("[BotList] 正在更新 Bot 列表...")
        for source in self.sources:
            for bot in (bots := await source.fetch()):
                self.register_bot(bot, no_assert=True)
            logger.success(f"[BotList] 已从 {source.name} 获取 {len(bots)} 个 Bot 实例")
        logger.success(f"[BotList] 当前列表共有 {len(self.bots)} 个 Bot 实例")

    def save(self):
        path_cfg: DataPathConfig = create(DataPathConfig)
        with (Path(path_cfg.library) / "bot_list.json").open(
            "w", encoding="utf-8"
        ) as file:
            file.write(self.json(ensure_ascii=False))
