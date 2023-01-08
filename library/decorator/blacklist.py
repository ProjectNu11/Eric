from datetime import timedelta
from typing import Self

from creart import it
from graia.amnesia.builtins.memcache import Memcache
from graia.ariadne import Ariadne
from graia.ariadne.event import MiraiEvent
from graia.broadcast import DecoratorInterface, ExecutionStop, RequirementCrashed
from loguru import logger
from sqlalchemy import select

from library.decorator.base import EricDecorator
from library.model.bot_list import BotList
from library.util.orm import orm
from library.util.orm.table import BlacklistTable
from library.util.type import FieldWide, Sender, SenderWide


class Blacklist(EricDecorator):
    """黑名单检查装饰器"""

    pre = True

    @property
    def supported_events(self) -> set[type[MiraiEvent]]:
        return set()

    _show_log: bool
    _check_field: bool
    _check_supplicant: bool
    _check_temporary: bool
    _check_bot: bool | None
    _check_anonymous: bool | None
    _cache: bool = True

    def __init__(
        self,
        show_log: bool = True,
        check_field: bool = True,
        check_supplicant: bool = True,
        check_temporary: bool = True,
        check_bot: bool | None = None,
        check_anonymous: bool | None = None,
        *,
        cache: bool = True,
    ):
        """
        Args:
            show_log: 是否显示日志
            check_field: 是否检查字段
            check_supplicant: 是否检查发信人
            check_temporary: 是否检查临时会话
            check_bot: 是否检查机器人
            check_anonymous: 是否检查匿名
            cache: 是否缓存检查结果
        """
        self._show_log = show_log
        self._check_field = check_field
        self._check_supplicant = check_supplicant
        self._check_temporary = check_temporary
        self._check_bot = check_bot
        self._check_anonymous = check_anonymous
        self._cache = cache

    async def target(self, interface: DecoratorInterface):
        try:
            sender: Sender = await interface.dispatcher_interface.lookup_param(
                "__decorator_parameter__", Sender, None
            )
            field: FieldWide = await interface.dispatcher_interface.lookup_param(
                "__decorator_parameter_group__", FieldWide, None
            )
            event: MiraiEvent = await interface.dispatcher_interface.lookup_param(
                "__decorator_parameter_event__", MiraiEvent, None
            )
            if sender is None and field is None:
                raise RequirementCrashed
        except RequirementCrashed as e:
            raise ExecutionStop from e
        field = field or 0
        if await self._run_check(event, sender, field):
            if self._show_log:
                logger.warning(f"[Blacklist] {field}: {sender} 在黑名单中")
            raise ExecutionStop

    async def _run_check(
        self,
        event: MiraiEvent,
        sender: SenderWide | None,
        field: FieldWide,
    ):
        key = f"{__package__}.{self.__class__.__name__}.{hash(repr(event))}"
        results: dict[str, bool]
        if self._cache and (
            results := await Ariadne.launch_manager.get_interface(Memcache).get(key)
        ):
            return any(results.values())
        results = {
            "field": await self.check_field(field) if self._check_field else None,
            "supplicant": await self.check_supplicant(sender, field)
            if self._check_supplicant
            else None,
            "temporary": await self.check_temporary(sender, field)
            if self._check_temporary
            else None,
            "bot": await self.check_bot(sender) if self._check_bot else None,
            "anonymous": await self.check_anonymous(sender)
            if self._check_anonymous
            else None,
        }
        if self._cache:
            await Ariadne.launch_manager.get_interface(Memcache).set(
                key, results, timedelta(seconds=15)
            )
        return any(results.values())

    @classmethod
    def check(cls, show_log: bool = True) -> Self:
        """
        DeprecationWarning: 请使用 `Blacklist` 装饰器
        """
        return cls(show_log=show_log)

    @classmethod
    async def check_field(cls, field: FieldWide) -> bool:
        """
        检查聊天区域是否在黑名单中

        Args:
            field: 聊天区域

        Returns:
            是否在黑名单中，True 为在
        """
        return await cls.check_by_condition(
            BlacklistTable.target == 0,
            BlacklistTable.field == int(field),
            table=BlacklistTable,
        )

    @classmethod
    async def check_supplicant(cls, supplicant: SenderWide, field: FieldWide) -> bool:
        """
        检查发信人是否在黑名单中

        Args:
            supplicant: 发信人
            field: 聊天区域

        Returns:
            是否在黑名单中，True 为在
        """
        return await cls.check_by_condition(
            BlacklistTable.target == int(supplicant),
            BlacklistTable.field == int(field),
            table=BlacklistTable,
        )

    @staticmethod
    async def check_by_condition(*conditions, table) -> bool:
        """
        检查是否在黑名单中

        Args:
            conditions: 条件
            table: 表

        Returns:
            是否查询到结果，True 为在
        """
        return bool(await orm.all(select(table).where(*conditions)))

    @classmethod
    async def check_temporary(cls, supplicant: SenderWide, field: FieldWide) -> bool:
        """
        检查发信人是否在临时黑名单中

        Args:
            supplicant: 发信人
            field: 聊天区域

        Returns:
            是否在临时黑名单中，True 为在
        """
        # TODO Implement TempBlacklist
        pass

    @classmethod
    async def check_bot(cls, supplicant: SenderWide) -> bool:
        """
        检查发信人是否为机器人

        Args:
            supplicant: 发信人

        Returns:
            是否为机器人，True 为是
        """
        return it(BotList).check(supplicant)

    @staticmethod
    async def check_anonymous(supplicant: SenderWide) -> bool:
        """
        检查发信人是否为匿名

        Args:
            supplicant: 发信人

        Returns:
            是否为匿名，True 为是
        """
        return int(supplicant) == 8000_0000
