from dataclasses import dataclass
from datetime import datetime

from graia.ariadne.message import Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Group, Member
from sqlalchemy import select
from typing_extensions import Self

from library.model.exception import RebuildMessageFailed
from library.util.misc import rebuild_chain
from library.util.orm import orm
from library.util.orm.table import MessageRecord


@dataclass
class RebuiltMessage:
    time: datetime
    """ 消息时间 """

    id: int
    """ 消息 ID """

    target: int
    """ 目标 ID，正数为群号，负数为私聊 ID """

    target_name: str
    """ 目标名称 """

    sender: int
    """ 发送者 ID """

    sender_name: str
    """ 发送者名称 """

    content: str
    """ 消息内容 """

    message_chain: MessageChain
    """ 消息链 """

    @classmethod
    async def from_orm(
        cls, source: Source | int, target: Group | Friend | Member | int
    ) -> Self:
        if isinstance(source, int) and target is None:
            raise ValueError(
                "source 为 int 时，target 必须为 Group | Friend | Member | int"
            )
        source: int = int(source)
        if isinstance(target, (Friend, Member)):
            target: int = -int(target)
        else:
            target: int = int(target)
        if not (
            raw := await orm.fetchone(
                select(
                    MessageRecord.time,
                    MessageRecord.msg_id,
                    MessageRecord.target,
                    MessageRecord.target_name,
                    MessageRecord.sender,
                    MessageRecord.sender_name,
                    MessageRecord.content,
                    MessageRecord.message_chain,
                ).where(
                    MessageRecord.msg_id == source,  # type: ignore
                    MessageRecord.target == target,  # type: ignore
                )
            )
        ):
            raise RebuildMessageFailed(source, target)
        return cls(
            time=raw[0],
            id=raw[1],
            target=raw[2],
            target_name=raw[3],
            sender=raw[4],
            sender_name=raw[5],
            content=raw[6],
            message_chain=rebuild_chain(raw[7]),
        )
