import contextlib

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import (
    ActiveFriendMessage,
    ActiveGroupMessage,
    FriendMessage,
    GroupMessage,
    MessageEvent,
)
from graia.ariadne.exception import AccountMuted, RemoteException, UnknownTarget
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.ariadne.model import Friend, Group
from kayaku import create
from loguru import logger

from library.model.config import EricConfig
from library.model.event.message import AccountMessageBanned
from library.util.multi_account.public_group import PublicGroup


async def _send_group_message(
    target: int | Group,
    message_chain: MessageChain,
    account: int,
    *,
    quote: Source | int | MessageChain | None = None,
) -> ActiveGroupMessage:
    ariadne: Ariadne = Ariadne.current(account)
    return await ariadne.send_group_message(target, message_chain, quote=quote)


async def _send_friend_message(
    target: int | Friend,
    message_chain: MessageChain,
    account: int,
    *,
    quote: Source | int | MessageChain | None = None,
) -> ActiveFriendMessage:
    ariadne: Ariadne = Ariadne.current(account)
    return await ariadne.send_friend_message(target, message_chain, quote=quote)


def _determine_target(
    target: Group | Friend | int | MessageEvent, is_group: bool
) -> Group | Friend | int:
    if isinstance(target, MessageEvent):
        if isinstance(target, GroupMessage):
            target = target.sender.group
        elif isinstance(target, FriendMessage):
            target = target.sender
        else:
            raise NotImplementedError(f"不支持的消息类型：{type(target)}")
    if isinstance(target, int) and is_group is None:
        raise ValueError(f"无法判断 {target} 为群聊或好友")
    return target


async def send_message(
    target: Group | Friend | int | MessageEvent,
    message_chain: MessageChain,
    account: int,
    *,
    is_group: bool = None,
    suppress: bool = True,
    resend: bool = True,
    quote: Source | int | None = None,
    excluded_account: set[int] = None,
) -> ActiveGroupMessage | ActiveFriendMessage | None:
    """
    发送消息

    Args:
        target (Group | Friend | int | MessageEvent): 目标
        message_chain (MessageChain): 消息链
        account (int): 账号
        is_group (bool): 是否为群组
        suppress (bool): 是否抑制异常
        resend (bool): 是否重发
        quote (Source | int | MessageChain | None): 消息引用
        excluded_account (set[int]): 排除账号

    Returns:
        ActiveGroupMessage | ActiveFriendMessage | None: 主动消息

    Raises:
        AccountMuted: 账号被禁言
        UnknownTarget: 目标不存在
        RemoteException: 远程异常
        Exception: 其他异常
    """
    excluded_account = excluded_account or set()
    target = _determine_target(target, is_group)

    try:
        if isinstance(target, Group) if is_group is None else is_group:
            _action = _send_group_message
        else:
            _action = _send_friend_message
        msg = await _action(target, message_chain, account, quote=quote)
        assert msg.id != -1, "消息发送失败"
        return msg

    except Exception as e:
        if isinstance(e, AccountMuted):
            logger.error(f"账号 {account} 在聊天区域 {target} 被禁言")
        elif isinstance(e, UnknownTarget):
            logger.error(f"无法找到对象 {target}")
        elif isinstance(e, AssertionError):
            logger.error(f"消息发送失败：{e.args[0]}")
        elif isinstance(e, RemoteException):
            if "resultType=46" in str(e):
                # 广播事件 AccountMessageBanned 供其他插件处理
                logger.error(f"账号 {account} 发送消息功能被禁用")
                Ariadne.current(account).broadcast.postEvent(
                    AccountMessageBanned(
                        account=account, field=target if is_group else 0
                    )
                )
            else:
                logger.error(f"账号 {account} 发送消息时出现异常: {e}")

        # 错误重发部分，遍历所有账号，直到发送成功
        if resend and is_group:
            if (
                available_account := it(PublicGroup).get_accounts(group=target)
                - excluded_account
            ):
                return await send_message(
                    target,
                    message_chain,
                    available_account.pop(),
                    is_group=is_group,
                    suppress=suppress,
                    resend=resend,
                    quote=quote,
                    excluded_account=excluded_account | {account},
                )
            logger.error("无可用账号发送消息")

        if suppress:
            return None
        raise e


async def broadcast_to_owners(
    message: MessageChain | str, account: int, suppress_on_none: bool = True
):
    assert message or suppress_on_none, "消息不能为空"
    message = MessageChain(message) if isinstance(message, str) else message
    cfg: EricConfig = create(EricConfig)
    for owner in cfg.owners:
        with contextlib.suppress(Exception):
            await send_message(owner, message, account, is_group=False)
