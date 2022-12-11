from typing import NoReturn

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from loguru import logger

from library.model.permission import UserPerm
from library.util.frequency_limit import FrequencyLimit


class Frequency:
    @classmethod
    def limit(
        cls,
        weight: int,
        show_log: bool = True,
        *,
        bypass_level: UserPerm = UserPerm.BOT_ADMIN,
    ) -> Depend:
        async def check(app: Ariadne, event: MessageEvent) -> NoReturn:
            frequency_instance: FrequencyLimit = it(FrequencyLimit)
            field = int(event.sender.group) if isinstance(event, GroupMessage) else 0
            supplicant = int(event.sender.id)
            if await UserPerm.get(event.sender) >= bypass_level:
                if show_log:
                    logger.info(f"[Frequency] {field}: {supplicant} 绕过")
                return

            frequency_instance.add_weight(field, supplicant, weight)
            if any(
                [
                    (
                        _supplicant := not frequency_instance.check_supplicant(
                            supplicant
                        )
                    ),
                    (_field := not frequency_instance.check_field(field)),
                    not frequency_instance.check_global(),
                ]
            ):
                if show_log:
                    logger.warning(f"[Frequency] {field}: {supplicant} 请求频率过高")
                target = ""
                if _supplicant:
                    await frequency_instance.blacklist_user(supplicant)
                    target += " [用户] "
                if _field:
                    await frequency_instance.blacklist_field(field)
                    target += " [群] "
                await app.send_message(
                    event.sender.group
                    if isinstance(event, GroupMessage)
                    else event.sender,
                    MessageChain(Plain(f"请求频率过高，临时封禁{target} 1 小时")),
                )
                raise ExecutionStop()

        return Depend(check)
