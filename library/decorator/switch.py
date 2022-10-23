from typing import NoReturn

from creart import it
from graia.ariadne.event.message import MessageEvent, GroupMessage
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from loguru import logger

from library.model.config.group_config import GroupConfig


class Switch:
    @classmethod
    def check(cls, module: str, show_log: bool = False) -> Depend:
        async def judge(event: MessageEvent) -> NoReturn:
            field = int(event.sender.group) if isinstance(event, GroupMessage) else 0
            if not cls.get(module, field):
                if show_log:
                    logger.warning(f"[Switch] {field}: {module} 未开启")
                raise ExecutionStop()

        return Depend(judge)

    @staticmethod
    def get(module: str, field: int):
        switch = it(GroupConfig).get_switch(field)
        return switch.get(module)

    @staticmethod
    def update(module: str, field: int, value: bool):
        switch = it(GroupConfig).get_switch(field)
        switch.update(module, value)
