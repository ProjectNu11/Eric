import contextlib
import re
from pathlib import Path

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.saya import Channel
from graiax.shortcut import decorate, listen
from sqlalchemy import select

from library.decorator import Blacklist, FunctionCall, Switch
from library.model.message import RebuiltMessage
from library.util.chat import ChatSessionContainer
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.module import Modules
from library.util.orm import orm
from library.util.orm.table import ChatCompletionTable

channel = Channel.current()


def _escape(_text: str) -> str:
    return _text.replace("[", "\\[").replace("]", "\\]")


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
        rf"^\s*[{re.escape(''.join(PrefixMatch.get_prefix()))}]+.*$",
        (text := "".join(plain.display for plain in chain.get(Plain)).strip()),
    ):  # 包含前缀，可能是其他模块触发词，直接 return 掉
        return

    user = await _get_user(-int(event.sender))
    if not user:
        await _initialize_user(-int(event.sender))
        user = (0, 0)

    session = await ChatSessionContainer.get(-int(event.sender))
    if event.quote and event.quote.id not in session.mapping:
        # 检查回复消息是不是在 ChatChain 里面，不是的话加入上下文
        quote = None
        with contextlib.suppress(Exception):
            rebuilt = await RebuiltMessage.from_orm(event.quote.id, event.sender)
            escaped = _escape(rebuilt.message_chain.safe_display)
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
        for data in _conditions.check(
            user[1], user[1] + result["response_usage"]["total_tokens"]
        ):
            await send_message(event, data, app.account)
    await FunctionCall.add_record(channel.module, 0, int(event.sender))


async def _get_user(user: int) -> tuple[int, int]:
    return await orm.first(
        select(ChatCompletionTable.usage, ChatCompletionTable.total_tokens).where(
            ChatCompletionTable.field == user  # noqa
        )
    )


def _identifier_to_path(identifier: str) -> Path:
    return Path(it(Modules).get(channel.module).data_path, *identifier.split("."))


def _get_local_text(identifier: str, fallback: str = "") -> str:
    file = _identifier_to_path(identifier)
    if not file.is_file():
        return fallback
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


async def _initialize_user(user: int):
    await orm.insert_or_update(
        ChatCompletionTable,
        [ChatCompletionTable.field == user],
        field=user,
        system_prompt=_get_local_text("global.system"),
    )


class _Conditions:
    every_token: dict[int, str]

    def __init__(self):
        self.every_token = {}
        self.load_every_token()

    def load_every_token(self):
        base = _identifier_to_path("global.every_token")
        if not base.is_dir():
            return
        for file in base.iterdir():
            self.every_token[int(file.name)] = file.read_text(encoding="utf-8")

    def check(self, before: int, after: int) -> list[str]:
        return [
            data.format(token=after)
            for token, data in self.every_token.items()
            if (after // token) > (before // token)
        ]


_conditions = _Conditions()


def _first_run():
    if not (global_system := _identifier_to_path("global.system")).is_file():
        global_system.parent.mkdir(parents=True, exist_ok=True)
        global_system.touch()


_first_run()
