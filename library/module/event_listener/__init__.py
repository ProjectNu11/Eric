import sys
from datetime import datetime
from typing import Union

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event import MiraiEvent
from graia.ariadne.event.message import (
    ActiveMessage,
    FriendMessage,
    GroupMessage,
    MessageEvent,
    SyncMessage,
)
from graia.ariadne.event.mirai import (
    BotInvitedJoinGroupRequestEvent,
    MemberJoinRequestEvent,
    NewFriendRequestEvent,
)
from graia.ariadne.exception import InvalidSession
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import (
    FullMatch,
    RegexMatch,
    RegexResult,
    Twilight,
    UnionMatch,
)
from graia.ariadne.util import gen_subclass
from graia.broadcast import run_always_await
from graia.saya import Channel
from graiax.shortcut import listen
from graiax.shortcut.saya import decorate, dispatch, every

from library.decorator import Blacklist, FunctionCall
from library.module.event_listener.util import _unpickle_request
from library.util.message import send_message
from library.util.misc import camel_to_snake
from library.util.module import Modules

# Use __import__ or flake8 will report an error
__import__(f"{__name__}.function")

channel = Channel.current()
_module = it(Modules).get(channel.module)
_data_path = _module.data_path

_functions = sys.modules[f"{__name__}.function"].__dict__
_listening_events = (
    set(gen_subclass(MiraiEvent))
    - set(gen_subclass(MessageEvent))
    - set(gen_subclass(SyncMessage))
    - set(gen_subclass(ActiveMessage))
)

_Request = Union[
    BotInvitedJoinGroupRequestEvent, MemberJoinRequestEvent, NewFriendRequestEvent
]


@listen(*_listening_events)
async def event_listener(app: Ariadne, event: MiraiEvent):
    key = camel_to_snake(event.__class__.__name__)
    if (func := _functions.get(key)) and callable(func):
        await run_always_await(func, app=app, event=event)


@every(1, mode="hour")
async def invalidate_outdated_pickle():
    for file in _data_path.iterdir():
        if file.suffix != ".pkl":
            continue
        if (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days > 3:
            file.unlink()


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        FullMatch("#"),
        UnionMatch("通过", "拒绝") @ "action",
        RegexMatch(
            r"[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-"
            r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}"
        )
        @ "request_id",
    )
)
@decorate(
    Blacklist(),
    FunctionCall(channel.module),
)
async def request_handler(
    app: Ariadne, event: MessageEvent, action: RegexResult, request_id: RegexResult
):
    action: str = action.result.display
    request_id: str = request_id.result.display
    path = _data_path / str(app.account)
    if not (pickle_path := path / f"{request_id}.pkl").is_file():
        return await send_message(event, MessageChain("无法找到该请求"), app.account)
    request: _Request = await _unpickle_request(app.account, request_id)
    try:
        if action == "通过":
            await request.accept()
            await send_message(event, MessageChain("已通过"), app.account)
        else:
            await request.reject()
            await send_message(event, MessageChain("已拒绝"), app.account)
    except LookupError:
        return await send_message(event, MessageChain("上下文错误"), app.account)
    except InvalidSession:
        return await send_message(event, MessageChain("会话已失效"), app.account)
    except PermissionError:
        return await send_message(event, MessageChain("权限不足"), app.account)
    except Exception as e:
        return await send_message(event, MessageChain(f"未知错误: {e}"), app.account)
    else:
        pickle_path.unlink()
