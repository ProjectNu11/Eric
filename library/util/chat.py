from datetime import datetime

from creart import it
from graia.ariadne.event.message import ActiveMessage
from graia.ariadne.message.chain import Quote
from sqlalchemy import select

from library.model.exception import ChatEntryNotFound
from library.model.openai import (
    ChatCompletion,
    ChatEntry,
    ChatNode,
    ChatResponseUsage,
    ChatReturn,
)
from library.util.locksmith import LockSmith
from library.util.orm import orm
from library.util.orm.table import ChatCompletionHistory, ChatCompletionTable
from library.util.typ import Message


class ChatSession:
    __field: int

    instance: ChatCompletion
    """ChatCompletion 实例"""

    mapping: dict[int, str]
    """消息引用映射"""

    __mapping_updated: bool
    __ctx_uuids: list[str]

    def __init__(self, field: int):
        self.__field = field
        self.instance = ChatCompletion()
        self.mapping = {}
        self.__mapping_updated = False
        self.__ctx_uuids = []

    def __enter__(self):
        self.__mapping_updated = False
        self.__ctx_uuids = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__mapping_updated:
            return
        for uuid in self.__ctx_uuids:
            self.instance.remove(uuid)

    def remove(self, quote: Quote | int):
        """
        从会话中移除一条消息

        Args:
            quote (Quote | int): 消息引用

        Raises:
            ChatEntryNotFound: 消息不存在
        """
        quote = quote.id if isinstance(quote, Quote) else quote
        if quote in self.mapping:
            self.instance.remove(self.mapping[quote])
            del self.mapping[quote]
        raise ChatEntryNotFound(quote)

    def revoke(self, quote: Quote | int, count: int):
        """
        从会话中撤回一条消息

        Args:
            quote (Quote | int): 消息引用
            count (int): 撤回数量

        Raises:
            ChatEntryNotFound: 消息不存在
        """
        quote = quote.id if isinstance(quote, Quote) else quote
        if quote in self.mapping:
            self.instance.revoke(count, self.mapping[quote])
        raise ChatEntryNotFound(quote)

    async def send(self, content: str, quote: Quote | int | None = None) -> ChatReturn:
        """
        发送一条消息

        Args:
            content (str): 消息内容
            quote (Quote | int | None, optional): 消息引用. Defaults to None.

        Returns:
            ChatReturn: 消息返回值

        Raises:
            OpenAIKeyNotConfigured: OpenAI Key 未配置
            OpenAIInsufficientQuota: OpenAI 余额不足
            ChatEntryTooLong: 消息过长
            ChatSessionLocked: 会话已锁定
        """
        quote = quote.id if isinstance(quote, Quote) else quote
        data = await self.instance.send(
            content, self.mapping.get(quote) if quote is not None else quote
        )
        self.__mapping_updated = False
        self.__ctx_uuids.append(data["input_uuid"])
        self.__ctx_uuids.append(data["reply_uuid"])
        return data

    async def to_orm(self, node: ChatNode, msg_id: int, time: datetime):
        lock = it(LockSmith).get(f"library.util/chat:{self.__field}")
        async with lock:
            await orm.insert_or_update(
                ChatCompletionHistory,
                [ChatCompletionHistory.uuid == node["id"]],
                time=time,
                field=self.__field,
                role=node["entry"]["role"],
                uuid=node["id"],
                previous_node=node["previous"],
                msg_id=msg_id,
                content=node["entry"]["content"],
            )

    async def update_usage(self, usage: ChatResponseUsage):
        lock = it(LockSmith).get(f"library.util/chat:{self.__field}")
        async with lock:
            old = await orm.first(
                select(
                    ChatCompletionTable.usage,
                    ChatCompletionTable.total_tokens,
                    ChatCompletionTable.system_prompt,
                ).where(
                    ChatCompletionTable.field == self.__field  # noqa
                )
            )
            old = old or (0, 0, "")
            await orm.insert_or_update(
                ChatCompletionTable,
                [ChatCompletionTable.field == self.__field],
                field=self.__field,
                usage=old[0] + 1,
                total_tokens=old[1] + usage["total_tokens"],
                system_prompt=old[2],
            )

    async def from_orm(self, max_length: int = 20):
        system = ""
        if data := await orm.first(
            select(ChatCompletionTable.system_prompt).where(
                ChatCompletionTable.field == self.__field  # noqa
            )
        ):
            system = data[0]
        raw_nodes = await orm.all(
            select(
                ChatCompletionHistory.role,
                ChatCompletionHistory.uuid,
                ChatCompletionHistory.previous_node,
                ChatCompletionHistory.msg_id,
                ChatCompletionHistory.content,
            )
            .where(ChatCompletionHistory.field == self.__field)  # noqa
            .order_by(ChatCompletionHistory.time.desc())  # noqa
            .limit(max_length)
        )
        await self.set_system(system, skip_orm=True)
        for raw_node in raw_nodes:
            node = ChatNode(
                entry=ChatEntry(
                    role=raw_node[0],
                    content=raw_node[4],
                ),
                id=raw_node[1],
                previous=raw_node[2],
            )
            self.instance.history.insert(0, node)
            self.instance.nodes.insert(0, node)
            self.mapping[raw_node[3]] = raw_node[1]

    async def update(
        self,
        result: ChatReturn,
        /,
        user_uuid: str,
        user_event: Message,
        reply_uuid: str,
        reply_event: ActiveMessage,
    ):
        """
        更新消息引用映射，必须在消息发送后调用，否则会导致消息链不完整。
        更新消息引用映射后，会自动插入数据库。

        Args:
            result (ChatReturn): 消息返回值
            user_uuid (str): 用户消息 UUID
            user_event (Message): 用户消息
            reply_uuid (str): 机器人消息 UUID
            reply_event (ActiveMessage): 机器人消息
        """
        if any(
            [
                reply_event.id == -1,
                reply_uuid not in self.__ctx_uuids,
                user_event.id == -1,
                user_uuid not in self.__ctx_uuids,
            ]
        ):
            return
        self.mapping[user_event.id] = user_uuid
        self.mapping[reply_event.id] = reply_uuid
        self.__mapping_updated = True
        self.__ctx_uuids.remove(user_uuid)
        self.__ctx_uuids.remove(reply_uuid)
        await self.to_orm(
            self.instance.node_from_id(user_uuid), user_event.id, user_event.source.time
        )
        await self.to_orm(
            self.instance.node_from_id(reply_uuid), reply_event.id, datetime.now()
        )
        await self.update_usage(result["response_usage"])

    def get_chain(self, quote: Quote | int) -> list[ChatNode]:
        """
        获取一条消息的消息链

        Args:
            quote (Quote | int): 消息引用

        Returns:
            list[ChatNode]: 消息链
        """
        quote = quote.id if isinstance(quote, Quote) else quote
        return self.instance.get_chain(self.mapping.get(quote))

    def flush(self, system: bool):
        """
        刷新会话

        Args:
            system (bool): 是否刷新系统提示
        """
        self.instance.flush(system)
        self.mapping.clear()

    async def set_system(self, system: str, /, skip_orm: bool = False):
        """
        设置系统提示

        Args:
            system (str): 系统提示
            skip_orm (bool, optional): 是否跳过数据库操作. Defaults to False.
        """
        self.instance.system = system
        if skip_orm:
            return
        await orm.insert_or_update(
            ChatCompletionTable,
            [ChatCompletionTable.field == self.__field],
            field=self.__field,
            system_prompt=system,
        )


class ChatSessionContainer:
    session: dict[int, ChatSession] = {}

    @classmethod
    async def get(cls, field: int) -> ChatSession:
        """
        获取一个聊天区域的会话

        Args:
            field (int): 聊天区域
        """
        if field not in cls.session:
            cls.session[field] = ChatSession(field)
            await cls.session[field].from_orm()
        return cls.session[field]
