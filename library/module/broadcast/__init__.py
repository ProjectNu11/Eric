import asyncio
import random

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
from loguru import logger

from library.decorator import Blacklist, Distribution, FunctionCall, Permission, Switch
from library.model.permission import UserPerm
from library.module.manager.util.module.search import search_module
from library.ui import GenericBox, GenericBoxItem, ImageBox, Page, Title
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
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
    groups = set(p_group.data.keys())
    g_copy = groups.copy()
    module = module.result
    if module and not (module := search_module(module)):
        return await send_message(event, MessageChain(f"无法找到模块 {module}"), app.account)
    await send_message(event, MessageChain("请在 5 分钟内发送公告内容"), app.account)
    try:
        result: MessageEvent = await inc.wait(message_waiter(event), timeout=300)
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
        local=True,
    )
    for element in result.message_chain:
        if isinstance(element, Image):
            page.add(ImageBox(img=await element.get_bytes()))
            continue
        page.add(GenericBox(GenericBoxItem(None, str(element))))
    page_bytes = await page.render()
    await send_message(
        event,
        MessageChain(Image(data_bytes=page_bytes), "请确认是否发送公告[y/n]"),
        app.account,
    )
    try:
        if not await inc.wait(confirm_waiter(event), timeout=30):
            return await send_message(event, MessageChain("操作已取消"), app.account)
    except asyncio.TimeoutError:
        return await send_message(event, MessageChain("操作超时"), app.account)
    failed = set()
    skipped = set()
    msg = MessageChain(Image(data_bytes=page_bytes))
    while groups:
        group = groups.pop()
        try:
            if not Switch.get(channel.module, group):
                skipped.add(group)
                logger.warning(f"[Broadcast] 跳过 {group}：未启用广播模块")
                continue
            if module and not Switch.get(module, group):
                skipped.add(group)
                logger.warning(f"[Broadcast] 跳过 {group}：已被过滤器过滤 ({module.pack})")
                continue
            await asyncio.sleep(0.5 * random.randint(1, 3))
            accounts = list(p_group.get_accounts(group))
            if not await send_message(
                group,
                msg,
                accounts[0],
                is_group=True,
            ):
                logger.warning(f"[Broadcast] 跳过 {group}：发送失败")
                failed.add(group)
                continue
            logger.success(f"[Broadcast] 已发送公告至 {group}")
        except Exception as e:
            logger.error(f"[Broadcast] 广播至 {group} 时发生错误：{e}")
            failed.add(group)
    await send_message(
        event,
        MessageChain(
            f"已发送公告至 {len(g_copy) - len(skipped) - len(failed)} 个群组"
            + (f"\n跳过 {len(skipped)} 个群组" if skipped else "")
            + (f"\n失败 {len(failed)} 个群组" if failed else "")
        ),
        app.account,
    )
