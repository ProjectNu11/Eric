from datetime import datetime
from typing import NoReturn

from graia.ariadne.event import MiraiEvent
from graia.broadcast import DecoratorInterface, ExecutionStop, RequirementCrashed
from loguru import logger
from typing_extensions import Self

from library.decorator.base import EricDecorator
from library.util.orm import orm
from library.util.orm.table import FunctionCallRecord
from library.util.type import FieldWide, Sender


class FunctionCall(EricDecorator):
    pre = True

    @property
    def supported_events(self) -> set[type[MiraiEvent]]:
        return set()

    _pack: str

    def __init__(self, pack: str):
        """
        Args:
            pack: 包名
        """
        self._pack = pack

    async def target(self, interface: DecoratorInterface):
        try:
            sender: Sender = await self.lookup_param(interface, "sender", Sender, None)
            field: FieldWide = await self.lookup_param(interface, "field", FieldWide, 0)
            if sender is None:
                raise RequirementCrashed
        except RequirementCrashed as e:
            logger.warning(f"[{self.__class__.__name__}] RequirementCrashed: {e.args}")
            raise ExecutionStop from e
        field = field or 0
        await self.add_record(self._pack, int(field), int(sender))

    @classmethod
    def record(cls, pack: str) -> Self:
        """
        DeprecationWarning: 请使用 `Frequency` 装饰器
        """
        return cls(pack)

    @staticmethod
    async def add_record(pack: str, field: int, supplicant: int) -> NoReturn:
        """
        添加函数调用记录

        Args:
            pack: 包名
            field: 聊天区域
            supplicant: 发信人

        Returns:
            None
        """
        await orm.add(
            FunctionCallRecord,
            time=datetime.now(),
            field=field,
            supplicant=supplicant,
            function=pack,
        )
