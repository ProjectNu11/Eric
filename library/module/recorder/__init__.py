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
from graia.ariadne.message.element import Forward, MultimediaElement
from graia.saya import Channel
from graiax.shortcut import listen, priority
from loguru import logger

from library.module.recorder.table import MessageRecord
from library.util.locksmith import LockSmith
from library.util.orm import orm

channel = Channel.current()
smith = it(LockSmith)


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
        target = event.subject.id
        target_name = event.subject.name
    else:
        target = -event.subject.id
        target_name = "私聊"
    try:
        async with smith.get(channel.module):
            await orm.insert_or_ignore(
                MessageRecord,
                [
                    MessageRecord.msg_id == event.source.id,
                    MessageRecord.target == target,
                ],
                time=event.source.time,
                msg_id=event.source.id,
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
        target = event.sender.group.id
        target_name = event.sender.group.name
    else:
        target = -event.sender.id
        target_name = "私聊"
    try:
        async with smith.get(channel.module):
            await orm.insert_or_ignore(
                MessageRecord,
                [
                    MessageRecord.msg_id == event.source.id,
                    MessageRecord.target == target,
                ],
                time=event.source.time,
                msg_id=event.source.id,
                target=target,
                target_name=target_name,
                sender=event.sender.id,
                sender_name=getattr(event.sender, "name", "")
                or getattr(event.sender, "nickname", "未知"),
                content=message_chain.display,
                message_chain=message_chain.json(ensure_ascii=False),
            )
    except Exception as e:
        logger.error(f"[Recorder] Failed to record message: {e}")
