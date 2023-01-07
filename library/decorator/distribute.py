from typing import NoReturn

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.element import Source
from graia.ariadne.model import Member
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from kayaku import create
from loguru import logger

from library.model.config import EricConfig
from library.util.multi_account.public_group import PublicGroup


class Distribution:
    @classmethod
    def distribute(cls, show_log: bool = False) -> Depend:
        async def judge(app: Ariadne, event: MessageEvent, source: Source) -> NoReturn:
            await cls.judge(app, event, source, show_log)

        return Depend(judge)

    @staticmethod
    def is_self(member: Member | int) -> bool:
        return int(member) in create(EricConfig).accounts

    @classmethod
    async def judge(
        cls,
        app: Ariadne,
        event: MessageEvent,
        source: Source = None,
        show_log: bool = False,
    ):
        if not isinstance(event, GroupMessage):
            return
        group = event.sender.group
        member = event.sender
        source = source or event.source
        if cls.is_self(member):
            if show_log:
                logger.warning(f"[Distribution] 由已登录账号 {member.id} 触发，停止分发")
            raise ExecutionStop
        p_group = it(PublicGroup)
        if p_group.need_distribute(group, app.account) and p_group.execution_stop(
            group, app.account, source
        ):
            if show_log:
                logger.warning(f"[Distribution] {app.account} 不执行分发")
            raise ExecutionStop
        if show_log:
            logger.success(f"[Distribution] {app.account} 执行分发")
