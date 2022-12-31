from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import (
    BotInvitedJoinGroupRequestEvent,
    MemberJoinRequestEvent,
    NewFriendRequestEvent,
)
from loguru import logger

from library.module.event_listener.util import _get_cfg, _pickle_request, _send_message
from library.util.message import broadcast_to_owners


# bot_invited_join_group_request_event
async def bot_invited_join_group_request_event(
    app: Ariadne, event: BotInvitedJoinGroupRequestEvent
):
    uuid = await _pickle_request(app.account, event)
    request_id = event.request_id
    supplicant = event.supplicant
    nickname = event.nickname
    message = event.message
    source_group = event.source_group
    group_name = event.group_name
    msg, owner_msg = _get_cfg(
        0,
        event,
        uuid=uuid,
        request_id=request_id,
        supplicant=supplicant,
        nickname=nickname,
        message=message,
        source_group=source_group,
        group_name=group_name,
    )
    text = "[EventListener] 收到入群邀请"
    text += f"\n{'UUID':<8}: {uuid}"
    text += f"\n{'事件 ID':<8}: {request_id}"
    text += f"\n{'邀请人':<8}: {supplicant}"
    text += f"\n{'邀请人昵称':<8}: {nickname}"
    text += f"\n{'邀请人留言':<8}: {message}"
    text += f"\n{'邀请群':<8}: {source_group}"
    text += f"\n{'邀请群名称':<8}: {group_name}"
    logger.info(text)
    await broadcast_to_owners(owner_msg, app.account)


# member_join_request_event
async def member_join_request_event(app: Ariadne, event: MemberJoinRequestEvent):
    uuid = await _pickle_request(app.account, event)
    request_id = event.request_id
    supplicant = event.supplicant
    nickname = event.nickname
    message = event.message
    source_group = event.source_group
    group_name = event.group_name
    msg, owner_msg = _get_cfg(
        source_group,
        event,
        uuid=uuid,
        request_id=request_id,
        supplicant=supplicant,
        nickname=nickname,
        message=message,
        source_group=source_group,
        group_name=group_name,
    )
    text = "[EventListener] 收到入群申请"
    text += f"\n{'UUID':<8}: {uuid}"
    text += f"\n{'事件 ID':<8}: {request_id}"
    text += f"\n{'申请人':<8}: {supplicant}"
    text += f"\n{'申请人昵称':<8}: {nickname}"
    text += f"\n{'申请人留言':<8}: {message}"
    text += f"\n{'申请群':<8}: {source_group}"
    text += f"\n{'申请群名称':<8}: {group_name}"
    logger.info(text)
    await _send_message(source_group, msg, app.account, event, is_group=True)
    await broadcast_to_owners(owner_msg, app.account)


# new_friend_request_event
async def new_friend_request_event(app: Ariadne, event: NewFriendRequestEvent):
    uuid = await _pickle_request(app.account, event)
    request_id = event.request_id
    supplicant = event.supplicant
    nickname = event.nickname
    message = event.message
    source_group = event.source_group
    msg, owner_msg = _get_cfg(
        0,
        event,
        uuid=uuid,
        request_id=request_id,
        supplicant=supplicant,
        nickname=nickname,
        message=message,
        source_group=source_group,
    )
    text = "[EventListener] 收到好友申请"
    text += f"\n{'UUID':<8}: {uuid}"
    text += f"\n{'事件 ID':<8}: {request_id}"
    text += f"\n{'申请人':<8}: {supplicant}"
    text += f"\n{'申请人昵称':<8}: {nickname}"
    text += f"\n{'申请人留言':<8}: {message}"
    text += f"\n{'来源群':<8}: {source_group}" if source_group else ""
    logger.info(text)
    await broadcast_to_owners(owner_msg, app.account)
