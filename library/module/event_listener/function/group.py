from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import (
    GroupAllowAnonymousChatEvent,
    GroupAllowConfessTalkEvent,
    GroupAllowMemberInviteEvent,
    GroupEntranceAnnouncementChangeEvent,
    GroupMuteAllEvent,
    GroupNameChangeEvent,
)
from loguru import logger


# group_allow_anonymous_chat_event
async def group_allow_anonymous_chat_event(
    app: Ariadne, event: GroupAllowAnonymousChatEvent
):
    origin = event.origin
    current = event.current
    group = event.group
    operator = event.operator
    operator_repr = f"{operator.name} ({int(operator)})" if operator else "Bot"
    logger.info(
        f"[EventListener] 群组 {group.name} ({int(group)}) "
        f"匿名聊天权限由 {origin} 变更为 {current}，操作者 {operator_repr}"
    )


# group_allow_confess_talk_event
async def group_allow_confess_talk_event(
    app: Ariadne, event: GroupAllowConfessTalkEvent
):
    origin = event.origin
    current = event.current
    group = event.group
    operator = event.operator
    operator_repr = f"{operator.name} ({int(operator)})" if operator else "Bot"
    logger.info(
        f"[EventListener] 群组 {group.name} ({int(group)}) "
        f"坦白说权限由 {origin} 变更为 {current}，操作者 {operator_repr}"
    )


# group_allow_member_invite_event
async def group_allow_member_invite_event(
    app: Ariadne, event: GroupAllowMemberInviteEvent
):
    origin = event.origin
    current = event.current
    group = event.group
    operator = event.operator
    operator_repr = f"{operator.name} ({int(operator)})" if operator else "Bot"
    logger.info(
        f"[EventListener] 群组 {group.name} ({int(group)}) "
        f"允许群员邀请好友加群权限由 {origin} 变更为 {current}，操作者 {operator_repr}"
    )


# group_entrance_announcement_change_event
async def group_entrance_announcement_change_event(
    app: Ariadne, event: GroupEntranceAnnouncementChangeEvent
):
    origin = event.origin
    current = event.current
    group = event.group
    operator = event.operator
    operator_repr = f"{operator.name} ({int(operator)})" if operator else "Bot"
    logger.info(
        f"[EventListener] 群组 {group.name} ({int(group)}) "
        f"入群公告由 {origin} 变更为 {current}，操作者 {operator_repr}"
    )


# group_mute_all_event
async def group_mute_all_event(app: Ariadne, event: GroupMuteAllEvent):
    origin = event.origin
    current = event.current
    group = event.group
    operator = event.operator
    operator_repr = f"{operator.name} ({int(operator)})" if operator else "Bot"
    logger.info(
        f"[EventListener] 群组 {group.name} ({int(group)}) "
        f"全员禁言由 {origin} 变更为 {current}，操作者 {operator_repr}"
    )


# group_name_change_event
async def group_name_change_event(app: Ariadne, event: GroupNameChangeEvent):
    origin = event.origin
    current = event.current
    group = event.group
    operator = event.operator
    operator_repr = f"{operator.name} ({int(operator)})" if operator else "Bot"
    logger.info(
        f"[EventListener] 群组 {group.name} ({int(group)}) "
        f"群名由 {origin} 变更为 {current}，操作者 {operator_repr}"
    )
