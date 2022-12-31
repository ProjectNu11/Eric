import asyncio
from difflib import get_close_matches

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.lifecycle import AccountLaunch
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import (
    ArgResult,
    ElementMatch,
    FullMatch,
    RegexMatch,
    RegexResult,
    SpacePolicy,
    Twilight,
)
from graia.broadcast import PropagationCancelled
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graiax.shortcut import decorate, dispatch, listen
from graiax.shortcut.saya import every, priority
from kayaku import create
from loguru import logger

from library.decorator import Distribution, MentionMeOptional, Permission
from library.model.config import ManagerConfig
from library.model.core import EricCore
from library.model.permission import UserPerm
from library.module.manager.match import (
    CHANGE_GROUP_MODULE_STATE_CH,
    CHANGE_GROUP_MODULE_STATE_EN,
    GET_CONFIG_EN,
    INSTALL_EN,
    LIST_CONFIG_EN,
    REGISTER_REPOSITORY_EN,
    SUBCOMMANDS,
    UNLOAD_EN,
    UPDATE_CONFIG_EN,
    UPDATE_EN,
    UPGRADE_EN,
)
from library.module.manager.model.module import RemoteModule
from library.module.manager.util.config.get import mgr_get_module_config
from library.module.manager.util.config.list import mgr_list_module_configs
from library.module.manager.util.config.set import mgr_set_module_config
from library.module.manager.util.lock import lock
from library.module.manager.util.module.install import install
from library.module.manager.util.module.state import change_state
from library.module.manager.util.module.unload import perform_unload
from library.module.manager.util.remote.install import install as remote_install
from library.module.manager.util.remote.update import update_gen_img, update_gen_msg
from library.module.manager.util.remote.version import check_update
from library.module.manager.util.repository.register import wait_and_register
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.multi_account.public_group import PublicGroup
from library.util.waiter.friend import FriendConfirmWaiter
from library.util.waiter.group import GroupConfirmWaiter

channel = Channel.current()
inc = it(InterruptControl)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                ElementMatch(At, optional=True),
                PrefixMatch(optional=True),
                CHANGE_GROUP_MODULE_STATE_CH,
            )
        ],
        decorators=[
            MentionMeOptional.check(),
            Distribution.distribute(),
            Permission.require(UserPerm.ADMINISTRATOR),
        ],
        priority=0,
    )
)
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                ElementMatch(At, optional=True),
                PrefixMatch(),
                CHANGE_GROUP_MODULE_STATE_EN,
            )
        ],
        decorators=[
            MentionMeOptional.check(),
            Distribution.distribute(),
            Permission.require(UserPerm.ADMINISTRATOR),
        ],
        priority=0,
    )
)
@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                PrefixMatch(optional=True),
                CHANGE_GROUP_MODULE_STATE_CH,
            )
        ],
        decorators=[Permission.require(UserPerm.BOT_OWNER)],
        priority=0,
    )
)
@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight(PrefixMatch(), CHANGE_GROUP_MODULE_STATE_EN)],
        decorators=[Permission.require(UserPerm.BOT_OWNER)],
        priority=0,
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
    raise PropagationCancelled()


@listen(AccountLaunch)
async def manager_account_launch(event: AccountLaunch):
    await asyncio.sleep(1)
    await it(PublicGroup).init_account(event.app.account)
    if not (core := it(EricCore)).initialized:
        core.finish_init()
        logger.success("[EricService] Eric 核心初始化完成")


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(ElementMatch(At, optional=True), PrefixMatch(), REGISTER_REPOSITORY_EN)
)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
@priority(0)
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
    finally:
        raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(ElementMatch(At, optional=True), PrefixMatch(), UPDATE_EN))
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
@priority(0)
async def manager_update(app: Ariadne, event: MessageEvent):
    try:
        assert not lock.locked(), "未能取得管理器锁，请检查是否正在其他操作"
        async with lock:
            await send_message(event, MessageChain("正在拉取仓库更新中..."), app.account)
            await send_message(
                event,
                MessageChain(Image(data_bytes=await update_gen_img())),
                app.account,
            )
    except AssertionError as e:
        await send_message(event, MessageChain(e.args[0]), app.account)
    finally:
        raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(ElementMatch(At, optional=True), PrefixMatch(), UPGRADE_EN))
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
@priority(0)
async def manager_upgrade(app: Ariadne, event: MessageEvent, yes: ArgResult):
    yes: bool = yes.result
    if not (updates := check_update()):
        await send_message(event, MessageChain("无可用更新"), app.account)
        raise PropagationCancelled()
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
                await send_message(event, MessageChain("已取消更新"), app.account)
                raise PropagationCancelled()
        except TimeoutError as e:
            await send_message(event, MessageChain("等待超时"), app.account)
            raise PropagationCancelled() from e
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
            await send_message(
                event,
                MessageChain(msg),
                app.account,
            )
            raise PropagationCancelled() from e
    msg = f"已更新 {len(success)} 个模块"
    for _suc in success:
        msg += f"\n - {_suc.name} ({_suc.clean_name}) {_suc.version}"
    await send_message(
        event,
        MessageChain(msg),
        app.account,
    )
    raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(ElementMatch(At, optional=True), PrefixMatch(), INSTALL_EN))
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
@priority(0)
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
    finally:
        raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(ElementMatch(At, optional=True), PrefixMatch(), UNLOAD_EN))
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.BOT_OWNER),
)
@priority(0)
async def manager_unload(app: Ariadne, event: MessageEvent, content: RegexResult):
    content: str = content.result.display
    try:
        assert not lock.locked(), "未能取得管理器锁，请检查是否正在其他操作"
        async with lock:
            await send_message(event, perform_unload(content), app.account)
    except AssertionError as e:
        await send_message(event, MessageChain(e.args[0]), app.account)
    finally:
        raise PropagationCancelled()


@every(1, mode="hour")
async def auto_update():
    mgr_cfg: ManagerConfig = create(ManagerConfig, flush=True)
    if not mgr_cfg.plugin_auto_update:
        return
    try:
        assert not lock.locked()
        async with lock:
            logger.info("[Manager] 正在拉取仓库更新中...")
            logger.info(await update_gen_msg())
    except AssertionError:
        logger.warning("[Manager] 未能取得管理器锁，跳过自动更新")


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(PrefixMatch(), GET_CONFIG_EN))
@decorate(Distribution.distribute(), Permission.require(UserPerm.ADMINISTRATOR))
@priority(0)
async def manager_get_config(
    app: Ariadne, event: MessageEvent, group: ArgResult, content: RegexResult
):
    if group.matched:
        if not await Permission.check(event.sender, UserPerm.BOT_ADMIN):
            await send_message(event, MessageChain("Permission denied."), app.account)
            raise PropagationCancelled()
        group = group.result
    else:
        group = event.sender.group.id if isinstance(event, GroupMessage) else 0
    content = content.result.display
    result = mgr_get_module_config(group, content)
    await send_message(event, MessageChain(result), app.account)
    raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(PrefixMatch(), UPDATE_CONFIG_EN))
@decorate(Distribution.distribute(), Permission.require(UserPerm.ADMINISTRATOR))
@priority(0)
async def manager_set_config(
    app: Ariadne,
    event: MessageEvent,
    group: ArgResult,
    mod: RegexResult,
    key: RegexResult,
    value: RegexResult,
):
    if group.matched:
        if not await Permission.check(event.sender, UserPerm.BOT_ADMIN):
            await send_message(event, MessageChain("Permission denied."), app.account)
            raise PropagationCancelled()
        group = group.result
    else:
        group = event.sender.group.id if isinstance(event, GroupMessage) else 0
    mod = mod.result.display
    key = key.result.display
    value = value.result.display
    result = mgr_set_module_config(group, mod, **{key: value})
    await send_message(event, MessageChain(result), app.account)
    raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(PrefixMatch(), LIST_CONFIG_EN))
@decorate(Distribution.distribute(), Permission.require(UserPerm.ADMINISTRATOR))
@priority(0)
async def manager_list_config(app: Ariadne, event: MessageEvent):
    result = mgr_list_module_configs()
    await send_message(event, MessageChain(result), app.account)
    raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        PrefixMatch(),
        FullMatch("manager").space(SpacePolicy.FORCE),
        RegexMatch(r".+") @ "content",
    )
)
@decorate(Distribution.distribute())
@priority(1)
async def manager_fuzzy_fallback(
    app: Ariadne, event: MessageEvent, content: RegexResult
):
    word: str = content.result.display
    if matches := get_close_matches(word, SUBCOMMANDS.keys()):
        await send_message(
            event, MessageChain(f"未找到指令 {word}，您是不是想输入 {matches[0]}?"), app.account
        )
    raise PropagationCancelled()


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(PrefixMatch(), FullMatch("manager")))
@decorate(Distribution.distribute())
@priority(1)
async def manager_greetings(app: Ariadne, event: MessageEvent):
    text = "欢迎使用 Eric Manager，您可以使用以下指令进行管理："
    for subcommand, description in SUBCOMMANDS.items():
        text += f"\n - {subcommand}: {description}"
    await send_message(event, MessageChain(text), app.account)
    raise PropagationCancelled()
