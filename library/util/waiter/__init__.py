from typing import overload

from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.model import Friend, Group, Member

from library.util.waiter.friend import (
    FriendConfirmWaiter,
    FriendImageWaiter,
    FriendMessageWaiter,
    FriendSelectWaiter,
)
from library.util.waiter.group import (
    GroupConfirmWaiter,
    GroupImageWaiter,
    GroupMessageWaiter,
    GroupSelectWaiter,
)


def _is_friend(*args) -> bool:
    if isinstance(args[0], (GroupMessage, FriendMessage)):
        return isinstance(args[0].sender, Friend)
    return isinstance(args[0], Friend)


def _extract_event(
    event: GroupMessage | FriendMessage,
) -> tuple[Group, Member] | tuple[Friend]:
    if isinstance(event, GroupMessage):
        return event.sender.group, event.sender
    return (event.sender,)


def _process_args(*args) -> tuple:
    if isinstance(args[0], (GroupMessage, FriendMessage)):
        return _extract_event(args[0]) + args[1:]
    return args


@overload
def confirm_waiter(
    _friend: Friend, *confirm_words: list[str] | str
) -> FriendConfirmWaiter:
    pass


@overload
def confirm_waiter(
    _group: Group, _member: Member, *confirm_words: list[str] | str
) -> GroupConfirmWaiter:
    pass


@overload
def confirm_waiter(
    _event: FriendMessage, *confirm_words: list[str] | str
) -> FriendConfirmWaiter:
    pass


@overload
def confirm_waiter(
    _event: GroupMessage, *confirm_words: list[str] | str
) -> GroupConfirmWaiter:
    pass


def confirm_waiter(*args):
    args = _process_args(*args)
    return (
        FriendConfirmWaiter(*args) if _is_friend(*args) else GroupConfirmWaiter(*args)
    )


@overload
def select_waiter(_friend: Friend, *selections: list[str] | str) -> FriendSelectWaiter:
    pass


@overload
def select_waiter(
    _group: Group, _member: Member, *selections: list[str] | str
) -> GroupSelectWaiter:
    pass


@overload
def select_waiter(
    _event: FriendMessage, *selections: list[str] | str
) -> FriendSelectWaiter:
    pass


@overload
def select_waiter(
    _event: GroupMessage, *selections: list[str] | str
) -> GroupSelectWaiter:
    pass


def select_waiter(*args):
    args = _process_args(*args)
    return FriendSelectWaiter(*args) if _is_friend(*args) else GroupSelectWaiter(*args)


@overload
def message_waiter(_friend: Friend) -> FriendMessageWaiter:
    pass


@overload
def message_waiter(_group: Group, _member: Member) -> GroupMessageWaiter:
    pass


@overload
def message_waiter(_event: FriendMessage) -> FriendMessageWaiter:
    pass


@overload
def message_waiter(_event: GroupMessage) -> GroupMessageWaiter:
    pass


def message_waiter(*args):
    args = _process_args(*args)
    return (
        FriendMessageWaiter(*args) if _is_friend(*args) else GroupMessageWaiter(*args)
    )


@overload
def image_waiter(_friend: Friend, *, force: bool = False) -> FriendImageWaiter:
    pass


@overload
def image_waiter(
    _group: Group, _member: Member, *, force: bool = False
) -> GroupImageWaiter:
    pass


@overload
def image_waiter(_event: FriendMessage, *, force: bool = False) -> FriendImageWaiter:
    pass


@overload
def image_waiter(_event: GroupMessage, *, force: bool = False) -> GroupImageWaiter:
    pass


def image_waiter(*args, force: bool = False):
    args = _process_args(*args)
    return (
        FriendImageWaiter(*args, force=force)
        if _is_friend(*args)
        else GroupImageWaiter(*args, force=force)
    )
