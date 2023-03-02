import asyncio

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import (
    ArgResult,
    ArgumentMatch,
    ElementMatch,
    FullMatch,
    Twilight,
)
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Channel
from graiax.shortcut import decorate, dispatch, listen

from library.decorator import Blacklist, Distribution, FunctionCall, Permission, Switch
from library.model.permission import UserPerm
from library.ui import Banner, GenericBox, GenericBoxItem, ImageBox, Page, ProgressBar
from library.ui.color import Color
from library.ui.color.palette import ColorPalette
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.waiter import confirm_waiter, message_waiter

channel = Channel.current()
inc = it(InterruptControl)


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True),
        PrefixMatch(),
        FullMatch("更换配色方案"),
        ArgumentMatch("-s", "--size", type=int, default=10) @ "size",
    )
)
@decorate(
    Switch.check(channel.module),
    Distribution.distribute(),
    Blacklist.check(),
    FunctionCall.record(channel.module),
    Permission.require(UserPerm.BOT_OWNER),
)
async def change_color_schema(
    app: Ariadne, event: GroupMessage | FriendMessage, size: ArgResult
):
    if not (quote := event.quote):
        return await send_message(
            event,
            MessageChain("仅在回复消息时可用"),
            app.account,
        )
    try:
        msg: MessageEvent = await app.get_message_from_id(
            quote.id,
            event.sender.group if isinstance(event, GroupMessage) else event.sender,
        )
    except UnknownTarget:
        return await send_message(event, MessageChain("暂未缓存该消息，可尝试重新发送"), app.account)
    if not (images := msg.message_chain.get(Image)):
        return await send_message(event, MessageChain("仅支持图片"), app.account)
    size: int = size.result
    if size <= 0:
        return await send_message(event, MessageChain("采样数应大于零"), app.account)
    image = images[0]
    image_bytes = await image.get_bytes()
    try:
        schema = ColorPalette.generate_schema(image_bytes, sample_size=size)
    except ValueError:
        return await send_message(
            event, MessageChain("无法生成配色方案，可能是图片颜色过暗或过亮，或采样数过小"), app.account
        )
    page = Page(
        Banner("配色方案预览"),
        GenericBox(
            GenericBoxItem("示例标题", "示例内容"),
        ),
        ProgressBar(0.5, "示例进度", "示例文本"),
        ImageBox.from_bytes(image_bytes),
        schema=schema,
        title="示例页面",
    )
    await send_message(
        event,
        MessageChain(
            Image(data_bytes=await page.render(local=True)), "是否确认更换配色方案？[y/n]"
        ),
        app.account,
    )
    try:
        if not await inc.wait(confirm_waiter(event), timeout=30):
            return await send_message(event, MessageChain("操作已取消"), app.account)
    except asyncio.TimeoutError:
        return await send_message(event, MessageChain("操作超时"), app.account)
    await send_message(event, MessageChain("请命名该配色方案"), app.account)
    try:
        result: MessageEvent = await inc.wait(message_waiter(event), timeout=30)
    except asyncio.TimeoutError:
        return await send_message(event, MessageChain("操作超时"), app.account)
    name = result.message_chain.display
    it(Color).register_schema(name, schema)
    it(Color).set_current(name)
    await send_message(event, MessageChain(f"已更换配色方案为 {name}"), app.account)


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(PrefixMatch(), FullMatch("恢复配色方案")))
@decorate(
    Switch.check(channel.module),
    Distribution.distribute(),
    Blacklist.check(),
    FunctionCall.record(channel.module),
    Permission.require(UserPerm.BOT_OWNER),
)
async def reset_color_schema(app: Ariadne, event: GroupMessage | FriendMessage):
    await send_message(
        event,
        MessageChain("是否确认恢复配色方案？[y/n]"),
        app.account,
    )
    try:
        if not await inc.wait(confirm_waiter(event), timeout=30):
            return await send_message(event, MessageChain("操作已取消"), app.account)
    except asyncio.TimeoutError:
        return await send_message(event, MessageChain("操作超时"), app.account)
    it(Color).set_current()
    await send_message(event, MessageChain("已恢复配色方案"), app.account)
