from typing import NoReturn

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Member
from graia.broadcast import ExecutionStop, PropagationCancelled
from graia.broadcast.builtin.decorators import Depend

from library.model.permission import UserPerm
from library.util.message import send_message


class Permission:
    @classmethod
    def require(
        cls,
        level: UserPerm,
        on_failure: str | None = "权限不足，你需要来自 {permission} 的权限",
        cancel_propagation: bool = False,
    ) -> Depend:
        async def check(app: Ariadne, event: MessageEvent) -> NoReturn:
            if await UserPerm.get(event.sender) < level:
                if on_failure:
                    await send_message(
                        event.sender.group
                        if isinstance(event, GroupMessage)
                        else event.sender,
                        MessageChain(on_failure.format(permission=level.value[-1])),
                        app.account,
                    )
                raise PropagationCancelled() if cancel_propagation else ExecutionStop()
            return

        return Depend(check)

    @staticmethod
    async def check(supplicant: int | Member | Friend, level: UserPerm) -> bool:
        return await UserPerm.get(supplicant) >= level

    @classmethod
    async def check_and_raise(
        cls, supplicant: int | Member | Friend, level: UserPerm
    ) -> NoReturn:
        if not await cls.check(supplicant, level):
            raise ExecutionStop()
