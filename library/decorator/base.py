from abc import abstractmethod
from typing import TypeVar

from graia.ariadne.event import MiraiEvent
from graia.broadcast import Decorator, DecoratorInterface, RequirementCrashed

_T = TypeVar("_T")
_TD = TypeVar("_TD")


class EricDecorator(Decorator):
    @property
    @abstractmethod
    def supported_events(self) -> set[type[MiraiEvent]]:
        """装饰器支持的事件类型，空集合表示支持所有事件"""
        return set()

    @staticmethod
    async def lookup_param(
        interface: DecoratorInterface, name: str, annotation: _T, default: _TD
    ) -> _T | _TD:
        try:
            return await interface.dispatcher_interface.lookup_param(
                name, annotation, default
            )
        except RequirementCrashed:
            return default
