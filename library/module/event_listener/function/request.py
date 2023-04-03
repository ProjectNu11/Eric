from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import (
    BotInvitedJoinGroupRequestEvent,
    MemberJoinRequestEvent,
    NewFriendRequestEvent,
)
from loguru import logger
from rich.table import Table

from library.module.event_listener.util import _get_cfg, _pickle_request, _send_message
from library.util.ctx import rich_console
from library.util.message import broadcast_to_owners


# bot_invited_join_group_request_event
async def bot_invited_join_group_request_event(
    app: Ariadne, event: BotInvitedJoinGroupRequestEvent
):
    request_id = event.request_id
    supplicant = event.supplicant
    nickname = event.nickname
    message = event.message
    source_group = event.source_group
    group_name = event.group_name
    uuid = await _pickle_request(app.account, 0, event)
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
    table = Table("Item", "Value", show_header=False)
    table.add_row("UUID", uuid)
    table.add_row("事件 ID", str(request_id))
    table.add_row("邀请人", str(supplicant))
    table.add_row("邀请人昵称", nickname)
    table.add_row("邀请人留言", message)
    table.add_row("邀请群", str(source_group))
    table.add_row("邀请群名称", group_name)
    rich_console.get().print(table)
    logger.info("[EventListener] 收到入群邀请")
    await broadcast_to_owners(owner_msg, app.account)


# member_join_request_event
async def member_join_request_event(app: Ariadne, event: MemberJoinRequestEvent):
    request_id = event.request_id
    supplicant = event.supplicant
    nickname = event.nickname
    message = event.message
    source_group = event.source_group
    group_name = event.group_name
    uuid = await _pickle_request(app.account, source_group, event)
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
    table = Table("Item", "Value", show_header=False)
    table.add_row("UUID", uuid)
    table.add_row("事件 ID", str(request_id))
    table.add_row("申请人", str(supplicant))
    table.add_row("申请人昵称", nickname)
    table.add_row("申请人留言", message)
    table.add_row("申请群", str(source_group))
    table.add_row("申请群名称", group_name)
    rich_console.get().print(table)
    logger.info("[EventListener] 收到入群申请")
    await _send_message(source_group, msg, app.account, event, is_group=True)
    await broadcast_to_owners(owner_msg, app.account)


# new_friend_request_event
async def new_friend_request_event(app: Ariadne, event: NewFriendRequestEvent):
    request_id = event.request_id
    supplicant = event.supplicant
    nickname = event.nickname
    message = event.message
    source_group = event.source_group
    uuid = await _pickle_request(app.account, 0, event)
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
    table = Table("Item", "Value", show_header=False)
    table.add_row("UUID", uuid)
    table.add_row("事件 ID", str(request_id))
    table.add_row("申请人", str(supplicant))
    table.add_row("申请人昵称", nickname)
    table.add_row("申请人留言", message)
    table.add_row("来源群", str(source_group)) if source_group else ""
    rich_console().get()
    logger.info("[EventListener] 收到好友申请")
    await broadcast_to_owners(owner_msg, app.account)
