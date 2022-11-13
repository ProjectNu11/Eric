from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.model import Group, Member
from graia.broadcast import Force
from graia.broadcast.interrupt import Waiter

from library.decorator.distribute import Distribution
from library.util.misc import inflate


class GroupConfirmWaiter(Waiter.create([GroupMessage])):
    def __init__(
        self, group: Group | int, member: Member | int, *confirm_words: list[str] | str
    ):
        self.confirm_words = inflate(confirm_words) or ["是", "y", "yes", "确认"]
        self.group_id = int(group)
        self.member_id = int(member)

    async def detected_event(
        self,
        app: Ariadne,
        group: Group,
        member: Member,
        message: MessageChain,
        event: GroupMessage,
    ):
        await Distribution.judge(app, event, event.source)
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

    async def detected_event(
        self,
        app: Ariadne,
        group: Group,
        member: Member,
        message: MessageChain,
        event: GroupMessage,
    ):
        await Distribution.judge(app, event, event.source)
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

    async def detected_event(
        self, app: Ariadne, group: Group, member: Member, event: GroupMessage
    ):
        await Distribution.judge(app, event, event.source)
        if int(group) == self.group_id and int(member) == self.member_id:
            return event


class GroupImageWaiter(Waiter.create([GroupMessage])):
    def __init__(self, group: Group | int, member: Member | int, force: bool = False):
        self.group_id = int(group)
        self.member_id = int(member)
        self.force = force

    async def detected_event(
        self,
        app: Ariadne,
        group: Group,
        member: Member,
        message: MessageChain,
        event: GroupMessage,
    ):
        await Distribution.judge(app, event, event.source)
        if int(group) == self.group_id and int(member) == self.member_id:
            if image := message.get(Image):
                return image[0]
            elif self.force:
                return Force(None)
