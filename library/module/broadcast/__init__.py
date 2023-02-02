import asyncio
from contextlib import suppress

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import (
    ArgResult,
    ArgumentMatch,
    FullMatch,
    Twilight,
)
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Channel
from graiax.shortcut import decorate, dispatch, listen

from library.decorator import Blacklist, Distribution, FunctionCall, Permission, Switch
from library.model.permission import UserPerm
from library.ui import GenericBox, GenericBoxItem, ImageBox, Page, Title
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.module import Modules
from library.util.multi_account.public_group import PublicGroup
from library.util.waiter import confirm_waiter, message_waiter

channel = Channel.current()
inc = it(InterruptControl)


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        PrefixMatch(),
        FullMatch("公告"),
        ArgumentMatch("-m", "--module", type=str, default="") @ "module",
    )
)
@decorate(
    Switch.check(channel.module),
    Distribution.distribute(),
    Blacklist.check(),
    FunctionCall.record(channel.module),
    Permission.require(UserPerm.BOT_OWNER),
)
async def broadcast(
    app: Ariadne, event: GroupMessage | FriendMessage, module: ArgResult
):
    p_group = it(PublicGroup)
    groups = set().union(*p_group.data.values())
    module: str = module.result
    if module and not it(Modules).get(module):
        return await send_message(event, MessageChain(f"无法找到模块 {module}"), app.account)
    await send_message(event, MessageChain("请发送公告内容"), app.account)
    try:
        result: MessageEvent = await inc.wait(message_waiter(event), timeout=30)
    except asyncio.TimeoutError:
        return await send_message(event, MessageChain("操作超时"), app.account)
    page = Page(
        Title("公告"),
        GenericBox(
            GenericBoxItem(
                event.sender.name
                if isinstance(event, GroupMessage)
                else event.sender.nickname,
                "发送人",
                image=await event.sender.get_avatar(),
            )
        ),
    )
    for element in result.message_chain:
        if isinstance(element, Image):
            page.add(ImageBox(img=await element.get_bytes()))
            continue
        page.add(GenericBox(GenericBoxItem(None, str(element))))
    await send_message(
        event,
        MessageChain(
            Image(data_bytes=(page_bytes := await page.render())), "请确认是否发送公告[y/n]"
        ),
        app.account,
    )
    try:
        if not await inc.wait(confirm_waiter(event), timeout=30):
            return await send_message(event, MessageChain("操作已取消"), app.account)
    except asyncio.TimeoutError:
        return await send_message(event, MessageChain("操作超时"), app.account)
    failed = set()
    skipped = set()
    while groups:
        with suppress(Exception):
            group = groups.pop()
            if not Switch.get(channel.module, group):
                skipped.add(group)
                continue
            if module and not Switch.get(module, group):
                skipped.add(group)
                continue
            accounts = list(p_group.get_accounts(group))
            if not await send_message(
                group,
                MessageChain(Image(data_bytes=page_bytes)),
                accounts[0],
                is_group=True,
            ):
                failed.add(group)
                continue
    await send_message(
        event,
        MessageChain(
            f"已发送公告至 {len(p_group.data) - len(skipped) - len(failed)} 个群组"
            + f"\n跳过 {len(skipped)} 个群组"
            if skipped
            else f"\n失败 {len(failed)} 个群组"
            if failed
            else ""
        ),
        app.account,
    )
