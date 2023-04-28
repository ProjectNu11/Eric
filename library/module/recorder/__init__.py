import re
from pathlib import Path

import aiofiles
from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import (
    ActiveFriendMessage,
    ActiveGroupMessage,
    ActiveMessage,
    FriendMessage,
    FriendSyncMessage,
    GroupMessage,
    GroupSyncMessage,
    MessageEvent,
    SyncMessage,
)
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    FlashImage,
    Forward,
    Image,
    MultimediaElement,
    Voice,
)
from graia.saya import Channel
from graiax.shortcut import listen, priority
from kayaku import create
from loguru import logger

from library.model import EricConfig
from library.model.config import PathConfig
from library.util.locksmith import LockSmith
from library.util.orm import orm
from library.util.orm.table import MessageRecord

channel = Channel.current()
smith = it(LockSmith)

_CACHE_PATH = Path(create(PathConfig).data) / "cache"


def _remove_binary_fwd(fwd: Forward):
    for node in fwd.node_list:
        _remove_binary(node.message_chain, copy=False)


def _remove_binary(chain: MessageChain, copy: bool = True) -> MessageChain:
    if copy:
        chain = chain.copy()
    for element in chain.content:
        if isinstance(element, MultimediaElement):
            element.base64 = None
        elif isinstance(element, Forward):
            _remove_binary_fwd(element)
    return chain


@listen(ActiveGroupMessage, ActiveFriendMessage, GroupSyncMessage, FriendSyncMessage)
@priority(0)
async def active_msg_recorder(app: Ariadne, event: ActiveMessage | SyncMessage):
    message_chain = _remove_binary(event.message_chain)
    if isinstance(event, (ActiveGroupMessage, GroupSyncMessage)):
        target = int(event.subject)
    else:
        target = -int(event.subject)
    target_name = event.subject.name
    try:
        async with smith.get(channel.module):
            await orm.insert_or_ignore(
                MessageRecord,
                [
                    MessageRecord.msg_id == int(event.source),
                    MessageRecord.target == target,
                ],
                time=event.source.time,
                msg_id=int(event.source),
                target=target,
                target_name=target_name,
                sender=app.account,
                sender_name=str(app.account),
                content=message_chain.display,
                message_chain=message_chain.json(ensure_ascii=False),
            )
    except Exception as e:
        logger.error(f"[Recorder] Failed to record message: {e}")


@listen(GroupMessage, FriendMessage)
@priority(0)
async def msg_recorder(event: MessageEvent):
    message_chain = _remove_binary(event.message_chain)
    if isinstance(event, GroupMessage):
        target = int(event.sender.group)
        target_name = event.sender.group.name
    else:
        target = -int(event.sender)
        target_name = event.sender.name
    try:
        async with smith.get(channel.module):
            await orm.insert_or_ignore(
                MessageRecord,
                [
                    MessageRecord.msg_id == int(event.source),
                    MessageRecord.target == target,
                ],
                time=event.source.time,
                msg_id=int(event.source),
                target=target,
                target_name=target_name,
                sender=int(event.sender),
                sender_name=getattr(event.sender, "name", "")
                or getattr(event.sender, "nickname", "未知"),
                content=message_chain.display,
                message_chain=message_chain.json(ensure_ascii=False),
            )
    except Exception as e:
        logger.error(f"[Recorder] Failed to record message: {e}")


@listen(GroupMessage, FriendMessage)
@priority(1)
async def cache_media(message: MessageChain):
    for element in message.get(MultimediaElement):
        config: EricConfig = create(EricConfig)
        if not config.multimedia_caching:
            return
        if isinstance(element, FlashImage):
            element = element.to_image()
        if isinstance(element, Image):
            ele_id, suffix = re.search(r"{(.+)}\.(.+)", element.id).groups()
        elif isinstance(element, Voice):
            ele_id, suffix = re.search(r"(.+)\.(.+)", element.id).groups()
        else:
            logger.error(
                f"[Recorder] Unsupported element type: {element.__class__.__name__}"
            )
            return
        typ = element.__class__.__name__
        (typ_path := _CACHE_PATH / typ).mkdir(parents=True, exist_ok=True)
        if (file := typ_path / f"{ele_id}.{suffix}").is_file():
            continue
        async with aiofiles.open(file, "wb") as f:
            try:
                await f.write(await element.get_bytes())
            except Exception as e:
                logger.error(f"[Recorder] Failed to cache {typ} {ele_id}.{suffix}: {e}")
