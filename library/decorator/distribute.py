from typing import NoReturn

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Source
from graia.ariadne.model import Group, Member
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from kayaku import create as kayaku_create
from loguru import logger

from library.model.config.eric import EricConfig
from library.util.multi_account.public_group import PublicGroup


class Distribution:
    @classmethod
    def distribute(cls, show_log: bool = False) -> Depend:
        async def judge(
            app: Ariadne, group: Group, member: Member, source: Source
        ) -> NoReturn:
            if cls.is_self(member):
                if show_log:
                    logger.warning(f"[Distribution] 由已登录账号 {member.id} 触发，停止分发")
                raise ExecutionStop()
            p_group = it(PublicGroup)
            if p_group.need_distribute(group, app.account) and p_group.execution_stop(
                group, app.account, source
            ):
                if show_log:
                    logger.warning(f"[Distribution] {app.account} 不执行分发")
                raise ExecutionStop()
            if show_log:
                logger.success(f"[Distribution] {app.account} 执行分发")

        return Depend(judge)

    @staticmethod
    def is_self(member: Member | int) -> bool:
        return int(member) in kayaku_create(EricConfig).accounts
