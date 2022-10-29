import asyncio

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import AccountLaunch
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    ElementMatch,
    FullMatch,
    UnionMatch,
    WildcardMatch,
    RegexResult,
    SpacePolicy,
    ArgumentMatch,
    ArgResult,
)
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from kayaku import create
from loguru import logger

from library.decorator.distribute import Distribution
from library.decorator.mention import MentionMeOptional
from library.decorator.permission import Permission
from library.model.config.service.manager import ManagerConfig
from library.model.core import EricCore
from library.model.permission import UserPerm
from library.module.manager.model.module import RemoteModule
from library.module.manager.model.repository import ParsedRepository
from library.module.manager.util.module.state import change_state
from library.module.manager.util.module.state import change_state
from library.module.manager.util.remote.install import install
from library.module.manager.util.remote.update import update
from library.module.manager.util.remote.version import check_update
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.multi_account.public_group import PublicGroup
from library.util.waiter.friend import (
    FriendSelectWaiter,
    FriendMessageWaiter,
    FriendConfirmWaiter,
)
from library.util.waiter.group import (
    GroupSelectWaiter,
    GroupMessageWaiter,
    GroupConfirmWaiter,
)

channel = Channel.current()
inc = it(InterruptControl)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                ElementMatch(At, optional=True),
                PrefixMatch(optional=True),
                UnionMatch("打开", "关闭") @ "action",
                FullMatch("模块"),
                WildcardMatch() @ "content",
            )
        ],
        decorators=[
            MentionMeOptional.check(),
            Distribution.distribute(),
            Permission.require(UserPerm.ADMINISTRATOR),
        ],
    )
)
@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                PrefixMatch(optional=True),
                UnionMatch("打开", "关闭") @ "action",
                FullMatch("模块"),
                WildcardMatch() @ "content",
            )
        ],
        decorators=[Permission.require(UserPerm.BOT_OWNER)],
    )
)
async def manager_change_group_module_state(
    app: Ariadne, event: MessageEvent, action: RegexResult, content: RegexResult
):
    action: str = action.result.display
    content: str = content.result.display
    field: int = int(event.sender.group) if isinstance(event, GroupMessage) else 0
    msg: MessageChain = change_state(content, field, action == "打开")
    await send_message(event, msg, app.account)


@listen(AccountLaunch)
async def manager_account_launch(event: AccountLaunch):
    await asyncio.sleep(1)
    await it(PublicGroup).init_account(event.app.account)
    if not (core := it(EricCore)).initialized:
        core.finish_init()
        logger.success("[EricService] Eric 核心初始化完成")


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True),
        PrefixMatch(),
        FullMatch("manager").space(SpacePolicy.FORCE),
        FullMatch("register"),
    )
)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
async def manager_register_repository(app: Ariadne, event: MessageEvent):
    await send_message(
        event, MessageChain("请在一分钟内发送需要注册的仓库类型 (github/http)"), app.account
    )

    try:
        repo_type: str = await inc.wait(
            GroupSelectWaiter(event.sender.group, event.sender, "github", "http")
            if isinstance(event, GroupMessage)
            else FriendSelectWaiter(event.sender, "github", "http"),
            timeout=60,
        )
        if repo_type == "github":
            await send_message(
                event,
                MessageChain(
                    "请在一分钟内发送需要注册的仓库地址\n"
                    "示例：owner/repo\n"
                    "示例：owner/repo:branch\n"
                    '如未填写分支，则将使用默认分支 "modules"'
                ),
                app.account,
            )
        else:
            await send_message(
                event,
                MessageChain("请在一分钟内发送需要注册的仓库地址\n示例：example.com"),
                app.account,
            )
        reply_event: MessageEvent = await inc.wait(
            GroupMessageWaiter(event.sender.group, event.sender)
            if isinstance(event, GroupMessage)
            else FriendMessageWaiter(event.sender),
            timeout=60,
        )
        reply = reply_event.message_chain.display
    except TimeoutError:
        await send_message(event, MessageChain("等待超时"), app.account)
    else:
        mgr_cfg: ManagerConfig = create(ManagerConfig)
        if repo_type == "github":
            owner, repo = reply.split("/")
            branch = ""
            if ":" in repo:
                repo, branch = repo.split(":")
            branch = branch or "modules"
            mgr_cfg.register_repo("github", owner, repo, branch)
            msg = f"已注册仓库 {owner}/{repo}:{branch}"
        else:
            mgr_cfg.register_repo("http", reply)
            msg = f"已注册仓库 {reply}"
        it(ParsedRepository).__init__()
        await send_message(event, MessageChain(msg), app.account)


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True),
        PrefixMatch(),
        FullMatch("manager").space(SpacePolicy.FORCE),
        FullMatch("update"),
    )
)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
async def manager_update(app: Ariadne, event: MessageEvent):
    await send_message(event, MessageChain("正在拉取仓库更新中..."), app.account)
    modules, failed = await update()
    msg = f"成功拉取 {len(modules)} 个模块"
    for module in modules:
        msg += f"\n - {module.name} ({module.clean_name})"
    if failed:
        msg += f"\n\n{len(failed)} 个仓库拉取失败"
        for repo in failed:
            msg += f"\n - {repo.__name__}"
    if updates := check_update():
        msg += f"\n\n{len(updates)} 个模块可更新"
        for local, remote in updates:
            msg += f"\n - {local.name} ({local.clean_name})"
            msg += f"\n   {local.version} -> {remote.version}"
    await send_message(event, MessageChain(msg), app.account)


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True),
        PrefixMatch(),
        FullMatch("manager").space(SpacePolicy.FORCE),
        FullMatch("upgrade"),
        ArgumentMatch("-y", action="store_true") @ "yes",
    )
)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
async def manager_upgrade(app: Ariadne, event: MessageEvent, yes: ArgResult):
    yes: bool = yes.result
    if not (updates := check_update()):
        return await send_message(event, MessageChain("无可用更新"), app.account)
    if not yes:
        msg = f"将更新 {len(updates)} 个模块 (y/n)"
        for local, remote in updates:
            msg += f"\n - {local.name} ({local.clean_name})"
            msg += f"\n   {local.version} -> {remote.version}"
        await send_message(event, MessageChain(msg), app.account)
        try:
            if not await inc.wait(
                GroupConfirmWaiter(event.sender.group, event.sender, "y")
                if isinstance(event, GroupMessage)
                else FriendConfirmWaiter(event.sender, "y"),
                timeout=60,
            ):
                return await send_message(event, MessageChain("已取消更新"), app.account)
        except TimeoutError:
            return await send_message(event, MessageChain("等待超时"), app.account)
    success: list[RemoteModule] = []
    for _, remote in updates:
        try:
            await install(remote)
            success.append(remote)
        except Exception as e:
            logger.error(e.with_traceback(e.__traceback__))
            msg = f"已更新 {len(success)} 个插件"
            for _suc in success:
                msg += f"\n - {_suc.name} ({_suc.clean_name}) {_suc.version}"
            msg += f"更新 {remote.name} ({remote.clean_name}) 时出现错误，已中止更新\n{e}"
            return await send_message(
                event,
                MessageChain(msg),
                app.account,
            )
    msg = f"已更新 {len(success)} 个插件"
    for _suc in success:
        msg += f"\n - {_suc.name} ({_suc.clean_name}) {_suc.version}"
    return await send_message(
        event,
        MessageChain(msg),
        app.account,
    )
