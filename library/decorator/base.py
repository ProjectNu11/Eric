from abc import abstractmethod

from graia.ariadne.event import MiraiEvent
from graia.broadcast import Decorator


class EricDecorator(Decorator):
    @property
    @abstractmethod
    def supported_events(self) -> set[type[MiraiEvent]]:
        """装饰器支持的事件类型，空集合表示支持所有事件"""
        return set()
