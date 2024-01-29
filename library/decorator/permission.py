from typing import NoReturn

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.broadcast import ExecutionStop, PropagationCancelled
from graia.broadcast.builtin.decorators import Depend

from library.model.permission import FineGrainedPermission, UserPerm
from library.util.message import send_message
from library.util.typ import Sender, SenderWide
from library.util.user_profile import UserRegistry


class Permission:
    @classmethod
    def require(
        cls,
        level: UserPerm,
        *fg_perms: FineGrainedPermission,
        on_failure: str | None = "权限不足，你需要来自 {permission} 的权限",
        cancel_propagation: bool = False,
    ) -> Depend:
        async def check(app: Ariadne, event: MessageEvent) -> NoReturn:
            if await UserPerm.get(event.sender) < level:
                if on_failure:
                    await send_message(
                        (
                            event.sender.group
                            if isinstance(event, GroupMessage)
                            else event.sender
                        ),
                        MessageChain(on_failure.format(permission=level.value[-1])),
                        app.account,
                    )
                raise PropagationCancelled() if cancel_propagation else ExecutionStop()
            if fg_perms and not await cls.check_fine_grained(event.sender, *fg_perms):
                if on_failure:
                    await send_message(
                        (
                            event.sender.group
                            if isinstance(event, GroupMessage)
                            else event.sender
                        ),
                        MessageChain(
                            on_failure.format(
                                permission=", ".join(fg.id for fg in fg_perms)
                            )
                        ),
                        app.account,
                    )
                raise PropagationCancelled() if cancel_propagation else ExecutionStop()
            return

        return Depend(check)

    @staticmethod
    async def check(supplicant: SenderWide, level: UserPerm) -> bool:
        return await UserPerm.get(supplicant) >= level

    @classmethod
    async def check_and_raise(cls, supplicant: SenderWide, level: UserPerm) -> NoReturn:
        if not await cls.check(supplicant, level):
            raise ExecutionStop

    @classmethod
    async def check_fine_grained(
        cls, supplicant: Sender, *fg_perms: FineGrainedPermission
    ) -> bool:
        profile = await UserRegistry.get_or_create_profile(supplicant)
        return len(set(fg_perms).intersection(profile.fg_permission)) == len(fg_perms)
