import asyncio

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import AccountLaunch
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    ElementMatch,
    FullMatch,
    UnionMatch,
    WildcardMatch,
    RegexResult,
)
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Channel
from loguru import logger

from library.decorator.distribute import Distribution
from library.decorator.mention import MentionMeOptional
from library.decorator.permission import Permission
from library.model.core import EricCore
from library.model.permission import UserPerm
from library.module.manager.util.module.state import change_state
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.multi_account.public_group import PublicGroup

channel = Channel.current()


@listen(GroupMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True) @ "at",
        PrefixMatch(optional=True),
        UnionMatch("打开", "关闭") @ "action",
        FullMatch("插件"),
        WildcardMatch() @ "content",
    )
)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.ADMINISTRATOR),
)
async def manager_change_group_module_state(
    app: Ariadne, event: MessageEvent, action: RegexResult, content: RegexResult
):
    action: str = action.result.display
    content: str = content.result.display
    field: int = int(event.sender.group) if isinstance(event, GroupMessage) else 0
    msg: MessageChain = change_state(content, field, action == "打开")
    await send_message(event.sender.group, msg, app.account)


@listen(AccountLaunch)
async def manager_account_launch(event: AccountLaunch):
    await asyncio.sleep(1)
    await it(PublicGroup).init_account(account := event.app.account)
    logger.success(f"[EricService] {account}: 公共群数据初始化完成")
    if not (core := it(EricCore)).initialized:
        core.finish_init()
        logger.success("[EricService] Eric 核心初始化完成")
