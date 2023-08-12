import contextlib
import re

from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.saya import Channel
from graiax.shortcut import decorate, listen

from library.decorator import Blacklist, FunctionCall, Switch
from library.model.message import RebuiltMessage
from library.module.chat.util import (
    get_user,
    identifier_to_path,
    initialize_user,
    triggers,
)
from library.util.chat import ChatSessionContainer
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.misc import backslash_escape

channel = Channel.current()


@listen(FriendMessage)
# 不用 @dispatch()，防止消息链中其他元素干扰正则匹配
@decorate(
    Switch.check(channel.module, show_log=False),
    Blacklist.check(),
)
async def chat_completion_impl_friend(
    app: Ariadne, event: FriendMessage, chain: MessageChain
):
    if re.fullmatch(
        rf"^\s*[#{re.escape(''.join(PrefixMatch.get_prefix()))}]+.*$",
        (text := "".join(plain.display for plain in chain.get(Plain)).strip()),
    ):  # 包含前缀，可能是其他模块触发词，直接 return 掉
        return

    user = await get_user(-int(event.sender))
    if not user:
        await initialize_user(-int(event.sender), event.sender.nickname)
        user = (0, 0)

    session = await ChatSessionContainer.get(-int(event.sender))
    if event.quote and event.quote.id not in session.mapping:
        # 检查回复消息是不是在 ChatChain 里面，不是的话加入上下文
        quote = None
        with contextlib.suppress(Exception):
            rebuilt = await RebuiltMessage.from_orm(event.quote.id, event.sender)
            escaped = backslash_escape(rebuilt.message_chain.safe_display, "[", "]")
            text = f"[Context]{escaped}[/Context]" + "\n" + text
    elif event.quote:
        quote = event.quote
    else:
        quote = None
    with session:
        result = await session.send(text, quote)
        active = await send_message(event, result["reply_content"], app.account)
        await session.update(
            result,
            user_uuid=result["input_uuid"],
            user_event=event,
            reply_uuid=result["reply_uuid"],
            reply_event=active,
        )
        for data in triggers.check(
            user[1], user[1] + result["response_usage"]["total_tokens"]
        ):
            await send_message(event, data, app.account)
    await FunctionCall.add_record(channel.module, 0, int(event.sender))


def _first_run():
    if not (global_system := identifier_to_path("global.default.system")).is_file():
        global_system.parent.mkdir(parents=True, exist_ok=True)
        global_system.touch()


_first_run()
