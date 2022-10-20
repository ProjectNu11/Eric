from creart import create
from graia.ariadne import Ariadne
from graia.ariadne.event.message import ActiveGroupMessage, ActiveFriendMessage
from graia.ariadne.exception import AccountMuted, UnknownTarget, RemoteException
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Source
from graia.ariadne.model import Group, Friend
from loguru import logger

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


async def send_message(
    target: Group | Friend | int,
    message_chain: MessageChain,
    account: int,
    *,
    is_group: bool = None,
    suppress: bool = True,
    resend: bool = True,
    quote: Source | int | MessageChain | None = None,
    excluded_account: set[int] = None,
) -> ActiveGroupMessage | ActiveFriendMessage | None:
    """
    发送消息

    Args:
        target (Group | Friend | int): 目标
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
    try:
        if isinstance(target, int) and is_group is None:
            raise ValueError(f"无法判断 {target} 为群聊或好友")
        if isinstance(target, Group) if is_group is None else is_group:
            return await _send_group_message(
                target, message_chain, account, quote=quote
            )
        return await _send_friend_message(target, message_chain, account, quote=quote)
    except Exception as e:
        if isinstance(e, AccountMuted):
            logger.error(f"账号 {account} 在聊天区域 {target} 被禁言")
        elif isinstance(e, UnknownTarget):
            logger.error(f"无法找到对象 {target}")
        elif isinstance(e, RemoteException):
            if "resultType=46" in str(e):
                logger.error(f"账号 {account} 发送消息功能被禁用")
                Ariadne.current(account).broadcast.postEvent(
                    AccountMessageBanned(
                        account=account, field=target if is_group else 0
                    )
                )
            else:
                logger.error(f"账号 {account} 发送消息时出现异常: {e}")
        if resend and is_group:
            if (
                available_account := create(PublicGroup).get_accounts(group=target)
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
        if suppress:
            return None
        raise e
