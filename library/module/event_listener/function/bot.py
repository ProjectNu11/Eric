from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import (
    BotGroupPermissionChangeEvent,
    BotJoinGroupEvent,
    BotLeaveEventActive,
    BotLeaveEventDisband,
    BotLeaveEventKick,
    BotMuteEvent,
    BotOfflineEventActive,
    BotOfflineEventDropped,
    BotOfflineEventForce,
    BotOnlineEvent,
    BotReloginEvent,
    BotUnmuteEvent,
)
from kayaku import create
from loguru import logger

from library.model.config import EricConfig
from library.model.permission import PERMISSION_MAPPING
from library.module.event_listener.util import _get_cfg, _send_message
from library.util.message import broadcast_to_owners
from library.util.misc import seconds_to_string
from library.util.multi_account.public_group import PublicGroup

_eric_cfg: EricConfig = create(EricConfig)
_p_group = it(PublicGroup)


# bot_group_permission_change_event
async def bot_group_permission_change_event(
    app: Ariadne, event: BotGroupPermissionChangeEvent
):
    group = event.group
    current = event.current
    current_repr = PERMISSION_MAPPING.get(current, "未知")
    origin = event.origin
    origin_repr = PERMISSION_MAPPING.get(origin, "未知")
    logger.info(
        f"[EventListener] Bot {app.account} 在群组 {group} 的权限由 {origin} 变更为 {current}"
    )
    msg, owner_msg = _get_cfg(
        int(group),
        event,
        app=app,
        group=group,
        current=current,
        current_repr=current_repr,
        origin=origin,
        origin_repr=origin_repr,
    )
    await _send_message(group, msg, app.account, event)
    await broadcast_to_owners(owner_msg, app.account)


# bot_join_group_event
async def bot_join_group_event(app: Ariadne, event: BotJoinGroupEvent):
    group = event.group
    logger.info(
        f"[EventListener] Bot {app.account} 加入群组 {group.name} ({int(group)})"
    )
    msg, owner_msg = _get_cfg(int(group), event, app=app, group=group)
    await _send_message(group, msg, app.account, event)
    await broadcast_to_owners(owner_msg, app.account)
    it(PublicGroup).add_group(group, app.account)


# bot_leave_event_active
async def bot_leave_event_active(app: Ariadne, event: BotLeaveEventActive):
    group = event.group
    logger.info(
        f"[EventListener] Bot {app.account} 离开群组 {group.name} ({int(group)})"
    )
    msg, owner_msg = _get_cfg(int(group), event, app=app, group=group)
    await _send_message(group, msg, app.account, event)
    await broadcast_to_owners(owner_msg, app.account)
    it(PublicGroup).remove_group(group, app.account)


# bot_leave_event_disband
async def bot_leave_event_disband(app: Ariadne, event: BotLeaveEventDisband):
    group = event.group
    logger.info(
        f"[EventListener] Bot {app.account} 所在群组 {group.name} ({int(group)}) 被解散"
    )
    msg, owner_msg = _get_cfg(int(group), event, app=app, group=group)
    await _send_message(group, msg, app.account, event)
    await broadcast_to_owners(owner_msg, app.account)
    it(PublicGroup).remove_group(group, app.account)


# bot_leave_event_kick
async def bot_leave_event_kick(app: Ariadne, event: BotLeaveEventKick):
    group = event.group
    logger.info(
        f"[EventListener] Bot {app.account} 被踢出群组 {group.name} ({int(group)})"
    )
    msg, owner_msg = _get_cfg(int(group), event, app=app, group=group)
    await _send_message(group, msg, app.account, event)
    await broadcast_to_owners(owner_msg, app.account)
    it(PublicGroup).remove_group(group, app.account)


# bot_mute_event
async def bot_mute_event(app: Ariadne, event: BotMuteEvent):
    operator = event.operator
    group = operator.group
    duration = event.duration
    duration_repr = seconds_to_string(duration)
    logger.info(
        f"[EventListener] Bot {app.account} 在群组 {group.name} ({int(group)}) "
        f"被 {operator.name} ({int(operator)}) 禁言 {duration_repr}"
    )
    msg, owner_msg = _get_cfg(
        int(group),
        event,
        app=app,
        operator=operator,
        group=group,
        duration=duration,
        duration_repr=duration_repr,
    )
    await broadcast_to_owners(owner_msg, app.account)


# bot_offline_event_active
async def bot_offline_event_active(app: Ariadne, event: BotOfflineEventActive):
    qq = event.qq
    logger.info(f"[EventListener] Bot {qq} 主动离线")
    await _p_group.remove_account(qq)
    msg, owner_msg = _get_cfg(0, event, qq=qq)
    await broadcast_to_owners(owner_msg, app.account)


# bot_offline_event_dropped
async def bot_offline_event_dropped(app: Ariadne, event: BotOfflineEventDropped):
    qq = event.qq
    logger.info(f"[EventListener] Bot {qq} 断开服务器连接")
    await _p_group.remove_account(qq)
    msg, owner_msg = _get_cfg(0, event, qq=qq)
    await broadcast_to_owners(owner_msg, app.account)


# bot_offline_event_force
async def bot_offline_event_force(app: Ariadne, event: BotOfflineEventForce):
    qq = event.qq
    logger.info(f"[EventListener] Bot {qq} 被服务器强制下线")
    await _p_group.remove_account(qq)
    msg, owner_msg = _get_cfg(0, event, qq=qq)
    await broadcast_to_owners(owner_msg, app.account)


# bot_online_event
async def bot_online_event(app: Ariadne, event: BotOnlineEvent):
    qq = event.qq
    logger.info(f"[EventListener] Bot {qq} 上线")
    if qq not in _eric_cfg.accounts:
        return
    await _p_group.init_account(qq)
    msg, owner_msg = _get_cfg(0, event, qq=qq)
    await broadcast_to_owners(owner_msg, app.account)


# bot_relogin_event
async def bot_relogin_event(app: Ariadne, event: BotReloginEvent):
    qq = event.qq
    logger.info(f"[EventListener] Bot {qq} 重新登录")
    if qq not in _eric_cfg.accounts:
        return
    await _p_group.init_account(qq)
    msg, owner_msg = _get_cfg(0, event, qq=qq)
    await broadcast_to_owners(owner_msg, app.account)


# bot_unmute_event
async def bot_unmute_event(app: Ariadne, event: BotUnmuteEvent):
    operator = event.operator
    group = operator.group
    logger.info(
        f"[EventListener] Bot {app.account} 在群组 {group.name} ({int(group)}) "
        f"被 {operator.name} ({int(operator)}) 解除禁言"
    )
    msg, owner_msg = _get_cfg(
        int(group), event, app=app, operator=operator, group=group
    )
    await _send_message(group, msg, app.account, event)
    await broadcast_to_owners(owner_msg, app.account)
