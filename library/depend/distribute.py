from typing import NoReturn

from creart import create
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Source
from graia.ariadne.model import Group, Member
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from loguru import logger

from library.model.config.eric import EricConfig
from library.util.multi_account.public_group import PublicGroup


class Distribution:
    @staticmethod
    def distribute(show_log: bool = False) -> Depend:
        async def judge(
            app: Ariadne, group: Group, member: Member, source: Source
        ) -> NoReturn:
            if member.id in create(EricConfig).accounts:
                if show_log:
                    logger.warning(f"[Distribution] 由已登录账号 {member.id} 触发，停止分发")
                raise ExecutionStop()
            p_group = create(PublicGroup)
            if p_group.need_distribute(group, app.account) and p_group.execution_stop(
                group, app.account, source
            ):
                if show_log:
                    logger.warning(f"[Distribution] {app.account} 不执行分发")
                raise ExecutionStop()
            if show_log:
                logger.success(f"[Distribution] {app.account} 执行分发")

        return Depend(judge)
