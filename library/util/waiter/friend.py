from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend
from graia.broadcast.interrupt import Waiter

from library.util.misc import inflate


class FriendConfirmWaiter(Waiter.create([FriendMessage])):
    def __init__(self, friend: Friend | int, *confirm_words: list[str] | str):
        self.confirm_words = inflate(confirm_words) or ["是", "y", "yes", "确认"]
        self.friend_id = int(friend)

    async def detected_event(self, friend: Friend, message: MessageChain):
        if int(friend) == self.friend_id:
            return message.display.strip() in self.confirm_words


class FriendSelectWaiter(Waiter.create([FriendMessage])):
    def __init__(self, friend: Friend | int, *selections: list[str] | str):
        if not (selections := inflate(selections)):
            raise ValueError("参数不足")
        self.selections = inflate(selections)
        self.friend_id = int(friend)

    async def detected_event(self, friend: Friend, message: MessageChain):
        if (
            int(friend) == self.friend_id
            and (choice := message.display.strip()) in self.selections
        ):
            return choice


class FriendMessageWaiter(Waiter.create([FriendMessage])):
    def __init__(self, friend: Friend | int):
        self.friend_id = int(friend)

    async def detected_event(self, friend: Friend, event: FriendMessage):
        if int(friend) == self.friend_id:
            return event
