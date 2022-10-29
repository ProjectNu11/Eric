from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import Waiter

from library.util.misc import inflate


class GroupConfirmWaiter(Waiter.create([GroupMessage])):
    def __init__(
        self, group: Group | int, member: Member | int, *confirm_words: list[str] | str
    ):
        self.confirm_words = inflate(confirm_words) or ["是", "y", "yes", "确认"]
        self.group_id = int(group)
        self.member_id = int(member)

    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if int(group) == self.group_id and int(member) == self.member_id:
            return message.display.strip() in self.confirm_words


class GroupSelectWaiter(Waiter.create([GroupMessage])):
    def __init__(
        self, group: Group | int, member: Member | int, *selections: list[str] | str
    ):
        if not (selections := inflate(selections)):
            raise ValueError("参数不足")
        self.selections = inflate(selections)
        self.group_id = int(group)
        self.member_id = int(member)

    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if (
            int(group) == self.group_id
            and int(member) == self.member_id
            and (choice := message.display.strip()) in self.selections
        ):
            return choice


class GroupMessageWaiter(Waiter.create([GroupMessage])):
    def __init__(self, group: Group | int, member: Member | int):
        self.group_id = int(group)
        self.member_id = int(member)

    async def detected_event(self, group: Group, member: Member, event: GroupMessage):
        if int(group) == self.group_id and int(member) == self.member_id:
            return event
