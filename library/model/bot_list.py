from abc import abstractmethod
from pathlib import Path

from graia.ariadne.model import Friend, Member
from kayaku import create
from loguru import logger
from pydantic import BaseModel

from library.model.config import DataPathConfig


class BotType(BaseModel):
    name: str
    repo: list[str] = []
    site: str = ""
    description: str = ""

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"<BotType name={self.name!r} repo={self.repo!r} "
            f"site={self.site!r} description={self.description!r}>"
        )

    def __hash__(self):
        return hash(" ".join(self.repo))


class Bot(BaseModel):
    id: int
    nickname: str = "Unknown"
    maintainers: set[str] = set()
    type: BotType = BotType(name="Unknown")

    def __int__(self):
        return self.id

    def __str__(self):
        return self.nickname

    def __repr__(self):
        return (
            f"<Bot id={self.id} nickname={self.nickname!r} "
            f"maintainers={self.maintainers!r} type={self.type!r}>"
        )

    def __hash__(self):
        return hash(self.id)


class BotSource(BaseModel):
    name: str = "UnknownSource"
    url: str

    def __str__(self):
        return self.url

    def __repr__(self):
        return f"<BotSource name={self.name!r} url={self.url!r}>"

    def __hash__(self):
        return hash(self.url)

    @abstractmethod
    async def fetch(self) -> set[Bot]:
        pass


class BotList(BaseModel):
    sources: set[BotSource] = set()
    bots: set[Bot] = set()

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
            try:
                for bot in (bots := await source.fetch()):
                    self.register_bot(bot, no_assert=True)
                logger.success(f"[BotList] 已从 {source.name} 获取 {len(bots)} 个 Bot 实例")
            except Exception as e:
                logger.error(f"[BotList] 从 {source.name} 获取 Bot 实例时出现错误: {e}")
        logger.success(f"[BotList] 当前列表共有 {len(self.bots)} 个 Bot 实例")

    def save(self):
        path_cfg: DataPathConfig = create(DataPathConfig)
        with (Path(path_cfg.library) / "bot_list.json").open(
            "w", encoding="utf-8"
        ) as file:
            # Convert type or self.json() will raise exception
            self.sources = list(self.sources)  # type: ignore
            self.bots = list(self.bots)  # type: ignore
            file.write(self.json(indent=4, ensure_ascii=False))
            self.sources = set(self.sources)
            self.bots = set(self.bots)
