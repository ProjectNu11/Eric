from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import ElementMatch, FullMatch, Twilight
from graia.saya import Channel
from graiax.shortcut import decorate, dispatch, listen

from library.decorator import Blacklist, Distribution, FunctionCall, Permission, Switch
from library.model.permission import UserPerm
from library.ui import Banner, GenericBox, GenericBoxItem, ImageBox, Page, ProgressBar
from library.ui.color.palette import ColorPalette
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message

channel = Channel.current()


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True),
        PrefixMatch(),
        FullMatch("更换配色方案"),
    )
)
@decorate(
    Switch.check(channel.module),
    Distribution.distribute(),
    Blacklist.check(),
    FunctionCall.record(channel.module),
    Permission.require(UserPerm.BOT_OWNER),
)
async def change_color_schema(app: Ariadne, event: MessageEvent):
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
    image = images[0]
    image_bytes = await image.get_bytes()
    schema = ColorPalette.generate_schema(image_bytes)
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
        event, MessageChain(Image(data_bytes=await page.render())), app.account
    )
