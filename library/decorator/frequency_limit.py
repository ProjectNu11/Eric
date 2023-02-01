from graia.ariadne import Ariadne
from graia.ariadne.event import MiraiEvent
from graia.ariadne.model import Friend, Group, Member, Stranger
from graia.broadcast import DecoratorInterface, ExecutionStop, RequirementCrashed
from loguru import logger
from typing_extensions import Self

from library.decorator.base import EricDecorator
from library.model.exception import FrequencyLimitHit
from library.model.permission import UserPerm
from library.util.frequency_limit import FrequencyLimitCache
from library.util.type import FieldWide, Sender


class Frequency(EricDecorator):
    """频率限制装饰器"""

    pre = True

    @property
    def supported_events(self) -> set[type[MiraiEvent]]:
        return set()

    _weight: int
    _show_log: bool
    _bypass_level: UserPerm

    def __init__(
        self,
        weight: int = 1,
        show_log: bool = False,
        bypass_level: UserPerm = UserPerm.BOT_OWNER,
    ):
        """
        Args:
            weight: 权重
            show_log: 是否显示日志
            bypass_level: 通过等级
        """
        self._weight = weight
        self._show_log = show_log
        self._bypass_level = bypass_level

    @property
    def _interface(self) -> FrequencyLimitCache:
        return Ariadne.launch_manager.get_interface(FrequencyLimitCache)

    async def target(self, interface: DecoratorInterface):
        try:
            sender: Sender = await interface.dispatcher_interface.lookup_param(
                "sender", Member | Friend | Stranger, None
            )
            field: FieldWide = await interface.dispatcher_interface.lookup_param(
                "group", Group | int, None
            )
            field = field or 0
            if sender is None or field is None:
                raise RequirementCrashed
        except RequirementCrashed as e:
            raise ExecutionStop from e
        try:
            await self._interface.add(field, sender, self._weight)
            if self._show_log:
                user_weight = self._interface.user_check(int(sender), suppress=True)
                field_weight = self._interface.field_check(int(field), suppress=True)
                global_weight = self._interface.global_check(suppress=True)
                logger.info(
                    f"[{self.__class__.__name__}] {field}: {sender} 权重: "
                    f"{user_weight} / {field_weight} / {global_weight}"
                )
        except FrequencyLimitHit as e:
            if self._show_log:
                logger.warning(f"[{self.__class__.__name__}] {e}")
            raise ExecutionStop from e

    @classmethod
    def limit(
        cls,
        weight: int,
        show_log: bool = True,
        *,
        bypass_level: UserPerm = UserPerm.BOT_OWNER,
    ) -> Self:
        """
        DeprecationWarning: 请使用 `Frequency` 装饰器
        """
        return cls(weight, show_log, bypass_level)
