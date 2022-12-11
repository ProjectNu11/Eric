import asyncio

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import AccountLaunch
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import ArgResult, RegexResult
from graia.ariadne.util.saya import decorate, dispatch, listen
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger

from library.decorator.distribute import Distribution
from library.decorator.mention import MentionMeOptional
from library.decorator.permission import Permission
from library.model.core import EricCore
from library.model.permission import UserPerm
from library.module.manager.model.module import RemoteModule
from library.module.manager.twilight import (
    CHANGE_GROUP_MODULE_STATE_CH,
    CHANGE_GROUP_MODULE_STATE_EN,
    INSTALL_EN,
    REGISTER_REPOSITORY_EN,
    UNLOAD_EN,
    UPDATE_EN,
    UPGRADE_EN,
)
from library.module.manager.util.lock import lock
from library.module.manager.util.module.install import install
from library.module.manager.util.module.state import change_state
from library.module.manager.util.module.unload import perform_unload
from library.module.manager.util.remote.install import install as remote_install
from library.module.manager.util.remote.update import update_gen_msg
from library.module.manager.util.remote.version import check_update
from library.module.manager.util.repository.register import wait_and_register
from library.util.message import send_message
from library.util.multi_account.public_group import PublicGroup
from library.util.waiter.friend import FriendConfirmWaiter
from library.util.waiter.group import GroupConfirmWaiter

channel = Channel.current()
inc = it(InterruptControl)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[CHANGE_GROUP_MODULE_STATE_CH],
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
        inline_dispatchers=[CHANGE_GROUP_MODULE_STATE_CH],
        decorators=[Permission.require(UserPerm.BOT_OWNER)],
    )
)
@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[CHANGE_GROUP_MODULE_STATE_EN],
        decorators=[Permission.require(UserPerm.BOT_OWNER)],
    )
)
@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[CHANGE_GROUP_MODULE_STATE_EN],
        decorators=[
            MentionMeOptional.check(),
            Distribution.distribute(),
            Permission.require(UserPerm.ADMINISTRATOR),
        ],
    )
)
async def manager_change_group_module_state(
    app: Ariadne, event: MessageEvent, action: RegexResult, content: RegexResult
):
    action: str = action.result.display
    content: str = content.result.display
    field: int = int(event.sender.group) if isinstance(event, GroupMessage) else 0
    msg: MessageChain = change_state(content, field, action in {"打开", "enable"})
    await send_message(event, msg, app.account)


@listen(AccountLaunch)
async def manager_account_launch(event: AccountLaunch):
    await asyncio.sleep(1)
    await it(PublicGroup).init_account(event.app.account)
    if not (core := it(EricCore)).initialized:
        core.finish_init()
        logger.success("[EricService] Eric 核心初始化完成")


@listen(GroupMessage, FriendMessage)
@dispatch(REGISTER_REPOSITORY_EN)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
async def manager_register_repository(app: Ariadne, event: MessageEvent):
    try:
        assert not lock.locked(), "未能取得管理器锁，请检查是否正在其他操作"
        async with lock:
            msg = await wait_and_register(app, event)
    except TimeoutError:
        await send_message(event, MessageChain("等待超时"), app.account)
    except ValueError:
        await send_message(event, MessageChain("数值输入错误，取消注册"), app.account)
    except AssertionError as e:
        await send_message(event, MessageChain(e.args[0]), app.account)
    else:
        await send_message(event, MessageChain(msg), app.account)


@listen(GroupMessage, FriendMessage)
@dispatch(UPDATE_EN)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
async def manager_update(app: Ariadne, event: MessageEvent):
    try:
        assert not lock.locked(), "未能取得管理器锁，请检查是否正在其他操作"
        async with lock:
            await send_message(event, MessageChain("正在拉取仓库更新中..."), app.account)
            await send_message(event, MessageChain(await update_gen_msg()), app.account)
    except AssertionError as e:
        await send_message(event, MessageChain(e.args[0]), app.account)


@listen(GroupMessage, FriendMessage)
@dispatch(UPGRADE_EN)
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
            await remote_install(remote)
            success.append(remote)
        except Exception as e:
            logger.error(e.with_traceback(e.__traceback__))
            msg = f"已更新 {len(success)} 个模块"
            for _suc in success:
                msg += f"\n - {_suc.name} ({_suc.clean_name}) {_suc.version}"
            msg += f"更新 {remote.name} ({remote.clean_name}) 时出现错误，已中止更新\n{e}"
            return await send_message(
                event,
                MessageChain(msg),
                app.account,
            )
    msg = f"已更新 {len(success)} 个模块"
    for _suc in success:
        msg += f"\n - {_suc.name} ({_suc.clean_name}) {_suc.version}"
    return await send_message(
        event,
        MessageChain(msg),
        app.account,
    )


@listen(GroupMessage, FriendMessage)
@dispatch(INSTALL_EN)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
async def manager_install(
    app: Ariadne, event: MessageEvent, yes: ArgResult, content: RegexResult
):
    yes: bool = yes.result
    content: str = content.result.display

    try:
        assert not lock.locked(), "未能取得管理器锁，请检查是否正在其他操作"
        async with lock:
            await send_message(
                event, await install(app, event, content, yes), app.account
            )
    except TimeoutError:
        await send_message(event, MessageChain("等待超时"), app.account)
    except AssertionError as e:
        await send_message(event, MessageChain(e.args[0]), app.account)


@listen(GroupMessage, FriendMessage)
@dispatch(UNLOAD_EN)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
async def manager_unload(app: Ariadne, event: MessageEvent, content: RegexResult):
    content: str = content.result.display
    assert not lock.locked(), "未能取得管理器锁，请检查是否正在其他操作"
    async with lock:
        await send_message(event, perform_unload(content), app.account)
