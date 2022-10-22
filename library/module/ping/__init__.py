from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ElementMatch,
    ElementResult,
)
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graiax.fastapi import RouteSchema
from loguru import logger

from library.depend.distribute import Distribution
from library.model.response import GeneralResponse
from library.util.dispatcher import PrefixMatch

channel = Channel.current()


@channel.use(RouteSchema("/ping", methods=["GET"], response_model=GeneralResponse))
async def ping_web():
    logger.success("[Ping] 收到来自 Web 的 Ping 请求")
    return {"code": 200, "message": "pong"}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                ElementMatch(At, optional=True) @ "at", PrefixMatch(), FullMatch("ping")
            )
        ],
    )
)
async def ping_message(app: Ariadne, event: MessageEvent, at: ElementResult):
    if at.matched and at.result.target != app.account:
        return
    if Distribution.self_trigger(event.sender.id):
        logger.warning(f"[Ping] 由已登录账号 {event.sender.id} 触发，停止执行")
        return
    await app.send_message(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(Plain("pong")),
    )