from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.parser.twilight import FullMatch, Twilight
from graia.saya import Channel
from graiax.shortcut import decorate, dispatch, listen

from library.decorator import Blacklist, Distribution, FunctionCall, Switch
from library.module.usage_report.util import get_report
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
