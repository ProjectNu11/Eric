from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.model import Friend, Group, Member

from library.ui import Banner, Page, ProgressBar
from library.util.multi_account.public_group import PublicGroup


async def get_all_members() -> list[Member]:
    public_group: PublicGroup = it(PublicGroup)
    result: list[Member] = []
    for account in public_group.accounts:
        for group in await Ariadne.current(account).get_group_list():
            group: Group
            result.extend(await Ariadne.current(account).get_member_list(group))
    return result


async def get_all_friends() -> list[Friend]:
    public_group: PublicGroup = it(PublicGroup)
    result: list[Friend] = []
    for account in public_group.accounts:
        result.extend(await Ariadne.current(account).get_friend_list())
    return result


def deduplicate(data: list[Member | Friend]) -> set[int]:
    return {int(this) for this in data}


async def get_dedup_members() -> set[int]:
    return deduplicate(await get_all_members())


async def get_dedup_friends() -> set[int]:
    return deduplicate(await get_all_friends())


async def get_all_users() -> list[Member | Friend]:
    members: list[Member] = await get_all_members()
    friends: list[Friend] = await get_all_friends()
    return [*members, *friends]


async def get_dedup_all() -> set[int]:
    members: set[int] = await get_dedup_members()
    friends: set[int] = await get_dedup_friends()
    return members | friends


async def get_page():
    all_members = await get_all_members()
    dedup_members = await get_dedup_members()
    all_friends = await get_all_friends()
    dedup_friends = await get_dedup_friends()
    all_users = await get_all_users()
    dedup_users = await get_dedup_all()

    return Page(
        Banner("用户覆盖率统计"),
        ProgressBar(
            len(dedup_members) / len(all_members),
            "群员",
            f"{len(dedup_members)} 去重复 / {len(all_members)} 总数",
        ),
        ProgressBar(
            len(dedup_friends) / len(all_friends),
            "好友",
            f"{len(dedup_friends)} 去重复 / {len(all_friends)} 总数",
        ),
        ProgressBar(
            len(dedup_users) / len(all_users),
            "总数",
            f"{len(dedup_users)} 去重复 / {len(all_users)} 总数",
        ),
    )
