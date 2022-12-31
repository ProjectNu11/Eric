from graia.ariadne import Ariadne
from graia.ariadne.event.mirai import (
    MemberCardChangeEvent,
    MemberHonorChangeEvent,
    MemberJoinEvent,
    MemberLeaveEventKick,
    MemberLeaveEventQuit,
    MemberMuteEvent,
    MemberPermissionChangeEvent,
    MemberSpecialTitleChangeEvent,
    MemberUnmuteEvent,
)


# TODO Implement these.
# member_card_change_event
async def member_card_change_event(app: Ariadne, event: MemberCardChangeEvent):
    ...


# member_honor_change_event
async def member_honor_change_event(app: Ariadne, event: MemberHonorChangeEvent):
    ...


# member_join_event
async def member_join_event(app: Ariadne, event: MemberJoinEvent):
    ...


# member_leave_event_kick
async def member_leave_event_kick(app: Ariadne, event: MemberLeaveEventKick):
    ...


# member_leave_event_quit
async def member_leave_event_quit(app: Ariadne, event: MemberLeaveEventQuit):
    ...


# member_mute_event
async def member_mute_event(app: Ariadne, event: MemberMuteEvent):
    ...


# member_permission_change_event
async def member_permission_change_event(
    app: Ariadne, event: MemberPermissionChangeEvent
):
    ...


# member_special_title_change_event
async def member_special_title_change_event(
    app: Ariadne, event: MemberSpecialTitleChangeEvent
):
    ...


# member_unmute_event
async def member_unmute_event(app: Ariadne, event: MemberUnmuteEvent):
    ...
