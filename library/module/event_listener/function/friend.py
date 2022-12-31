from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import (
    FriendInputStatusChangedEvent,
    FriendNickChangedEvent,
)
from loguru import logger


# friend_input_status_changed_event
async def friend_input_status_changed_event(
    app: Ariadne, event: FriendInputStatusChangedEvent
):
    friend = event.friend
    inputting = event.inputting
    logger.info(
        f"[EventListener] {friend.nickname} ({int(friend)}) {'正在' if inputting else '取消'}输入"
    )


# friend_nick_changed_event
async def friend_nick_changed_event(app: Ariadne, event: FriendNickChangedEvent):
    friend = event.friend
    from_name = event.from_name
    to_name = event.to_name
    logger.info(
        f"[EventListener] {friend.nickname} ({int(friend)}) 修改了昵称 {from_name} -> {to_name}"
    )
