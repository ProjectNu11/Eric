from typing import NoReturn

from graia.ariadne import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend

from library.model.permission import UserPerm
from library.util.message import send_message


class Permission:
    @classmethod
    def require(
        cls, level: UserPerm, on_failure: str = "权限不足，你需要来自 {permission} 的权限"
    ) -> Depend:
        async def check(app: Ariadne, event: MessageEvent) -> NoReturn:
            if await UserPerm.get(event.sender) < level:
                await send_message(
                    event.sender.group
                    if isinstance(event, GroupMessage)
                    else event.sender,
                    MessageChain(on_failure.format(permission=level.value[0])),
                    app.account,
                )
                raise ExecutionStop()
            return

        return Depend(check)
