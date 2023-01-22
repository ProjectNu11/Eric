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
from graiax.shortcut import listen, priority
from loguru import logger

from library.module.recorder.table import MessageRecord
from library.util.orm import orm


@listen(ActiveGroupMessage, ActiveFriendMessage, GroupSyncMessage, FriendSyncMessage)
@priority(0)
async def active_msg_recorder(app: Ariadne, event: ActiveMessage | SyncMessage):
    if isinstance(event, (ActiveGroupMessage, GroupSyncMessage)):
        target = event.subject.id
        target_name = event.subject.name
    else:
        target = -event.subject.id
        target_name = "私聊"
    try:
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
            content=event.message_chain.display,
            message_chain=event.message_chain.json(ensure_ascii=False),
        )
    except Exception as e:
        logger.error(f"[Recorder] Failed to record message: {e}")


@listen(GroupMessage, FriendMessage)
@priority(0)
async def msg_recorder(event: MessageEvent):
    if isinstance(event, GroupMessage):
        target = event.sender.group.id
        target_name = event.sender.group.name
    else:
        target = -event.sender.id
        target_name = "私聊"
    try:
        await orm.insert_or_ignore(
            MessageRecord,
            [MessageRecord.msg_id == event.source.id, MessageRecord.target == target],
            time=event.source.time,
            msg_id=event.source.id,
            target=target,
            target_name=target_name,
            sender=event.sender.id,
            sender_name=getattr(event.sender, "name", "")
            or getattr(event.sender, "nickname", "未知"),
            content=event.message_chain.display,
            message_chain=event.message_chain.json(ensure_ascii=False),
        )
    except Exception as e:
        logger.error(f"[Recorder] Failed to record message: {e}")
