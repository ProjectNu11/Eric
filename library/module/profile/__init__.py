import asyncio.exceptions
from contextlib import suppress

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import FullMatch, Twilight
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Channel
from graiax.shortcut import dispatch, listen

from library.model import UserProfileNotFound
from library.ui import Banner, GenericBox, GenericBoxItem, Page
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.typ import Message, Sender
from library.util.user_profile import UserRegistry
from library.util.waiter import message_waiter

channel = Channel.current()


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        PrefixMatch(),
        FullMatch("个人配置"),
    )
)
# @decorate()
async def get_profile(app: Ariadne, event: Message, sender: Sender):
    try:
        profile = await UserRegistry.get_profile(sender)
        return await send_message(
            event,
            MessageChain(
                Image(
                    data_bytes=await Page(
                        Banner("个人配置"),
                        GenericBox(
                            GenericBoxItem(
                                sender.name,
                                str(int(sender)),
                                image=await sender.get_avatar(),
                            ),
                        ),
                        GenericBox(
                            GenericBoxItem("昵称", profile.name),
                            GenericBoxItem(
                                "权限",
                                "\n".join(
                                    [
                                        profile.permission.value[-1],
                                        *[fg.id for fg in profile.fg_permission],
                                    ]
                                ),
                            ),
                        ),
                    ).render()
                )
            ),
            app.account,
        )
    except UserProfileNotFound:
        return await send_message(
            event,
            MessageChain(f'无法找到您的个人配置，请先发送 "{PrefixMatch.get_prefix()[0]}创建配置"。'),
            app.account,
        )


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        PrefixMatch(),
        FullMatch("创建配置"),
    )
)
async def create_profile(app: Ariadne, event: Message, sender: Sender):
    try:
        await UserRegistry.get_profile(sender)
    except UserProfileNotFound:
        pass
    else:
        return await send_message(event, MessageChain("您已创建过个人配置"), app.account)
    profile = await UserRegistry.create_profile(sender)
    await send_message(event, MessageChain("请在 30 秒内发送您的昵称，否则将使用当前用户名"), app.account)
    with suppress(asyncio.exceptions.TimeoutError):
        profile.name = (
            await it(InterruptControl).wait(message_waiter(event))
        ).message_chain.display
        await UserRegistry.update_profile(profile)
    await send_message(event, MessageChain("已创建个人配置"), app.account)
