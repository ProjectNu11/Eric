from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import FullMatch, Twilight
from graia.saya import Channel
from graiax.shortcut import decorate, dispatch, listen

from library.decorator import Blacklist, Distribution, FunctionCall, Switch
from library.module.usage_report.coverage import get_page
from library.module.usage_report.stats import get_report
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.typ import Message

channel = Channel.current()


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        PrefixMatch(),
        FullMatch("我的"),
        FullMatch("使用汇报"),
    )
)
@decorate(
    Switch.check(channel.module),
    Distribution.distribute(),
    Blacklist.check(),
    FunctionCall.record(channel.module),
)
async def get_usage_report(app: Ariadne, event: Message):
    await send_message(event, await get_report(app, event.sender), app.account)


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        PrefixMatch(),
        FullMatch("coverage"),
    )
)
@decorate(
    Switch.check(channel.module),
    Distribution.distribute(),
    Blacklist.check(),
    FunctionCall.record(channel.module),
)
async def get_coverrge_report(app: Ariadne, event: Message):
    await send_message(
        event,
        MessageChain(Image(data_bytes=await (await get_page()).render())),
        app.account,
    )
