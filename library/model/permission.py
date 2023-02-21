from enum import Enum

from creart import it
from graia.ariadne.model import Friend, Member, MemberPerm
from kayaku import create
from sqlalchemy import select
from typing_extensions import Self

from library.model.bot_list import BotList
from library.model.config import EricConfig
from library.util.orm import orm
from library.util.orm.table import UserProfileTable


class UserPerm(Enum):
    """用户权限"""

    BLOCKED = ("BLOCKED", -1, "封禁用户")
    """ 被封禁 """

    BOT = ("BOT", 0, "机器人")
    """ 机器人 """

    MEMBER = ("MEMBER", 1, "普通成员")
    """ 普通成员 """

    ADMINISTRATOR = ("ADMINISTRATOR", 2, "群管理员")
    """ 管理员 """

    OWNER = ("OWNER", 3, "群主")
    """ 群主 """

    BOT_ADMIN = ("BOT_ADMIN", 4, "机器人管理员")
    """ 机器人管理员 """

    BOT_OWNER = ("BOT_OWNER", 5, "机器人所有者")
    """ 机器人所有者 """

    INFINITE = ("INFINITE", 999, "测试权限等级")
    """ 无限权限，仅用于测试 """

    def __lt__(self, other: "UserPerm"):
        return self.value[1] < other.value[1]

    def __le__(self, other: "UserPerm"):
        return self.value[1] <= other.value[1]

    def __eq__(self, other: "UserPerm"):
        return self.value[1] == other.value[1]

    def __gt__(self, other: "UserPerm"):
        return self.value[1] > other.value[1]

    def __ge__(self, other: "UserPerm"):
        return self.value[1] >= other.value[1]

    def __repr__(self):
        return self.value[0]

    def __str__(self):
        return self.value[0]

    def __hash__(self):
        return hash(f"_UserPerm:{self.value[0]}")

    @classmethod
    def from_member_perm(cls, perm: MemberPerm) -> Self:
        """
        从 Ariadne 的 MemberPerm 枚举转换为 UserPerm 枚举

        Args:
            perm (MemberPerm): Ariadne 的 MemberPerm 枚举

        Returns:
            UserPerm: UserPerm 枚举，如果无法转换则返回 MEMBER
        """
        return getattr(cls, str(perm), cls.MEMBER)

    @classmethod
    def from_level(cls, level: int) -> Self:
        """
        从权限等级转换为 UserPerm 枚举

        Args:
            level (int): 权限等级

        Returns:
            UserPerm: UserPerm 枚举，如果无法转换则返回 MEMBER
        """
        return next((perm for perm in cls if perm.value[1] == level), cls.MEMBER)

    @classmethod
    def from_name(cls, name: str) -> Self:
        """
        从权限名转换为 UserPerm 枚举

        Args:
            name (str): 权限名

        Returns:
            UserPerm: UserPerm 枚举，如果无法转换则返回 MEMBER
        """
        return getattr(cls, name.upper(), cls.MEMBER)

    @classmethod
    async def get(
        cls,
        supplicant: int | Member | Friend,
        *,
        check_member_perm: bool = True,
        no_query: bool = False,
    ) -> Self:
        config: EricConfig = create(EricConfig)
        if int(supplicant) in config.owners:
            return cls.BOT_OWNER

        if isinstance(supplicant, Member) and check_member_perm:
            return cls.from_member_perm(supplicant.permission)

        if it(BotList).check(supplicant):
            return cls.BOT

        if not no_query and (
            data := await orm.fetchone(
                select(UserProfileTable.permission).where(
                    UserProfileTable.id == int(supplicant)  # type: ignore
                )
            )
        ):
            permission = data[0][0]
            return cls.from_name(permission)

        return cls.MEMBER


PERMISSION_MAPPING: dict[UserPerm | MemberPerm, str] = {
    UserPerm.BLOCKED: UserPerm.BLOCKED.value[-1],
    UserPerm.BOT: UserPerm.BOT.value[-1],
    UserPerm.MEMBER: UserPerm.MEMBER.value[-1],
    UserPerm.ADMINISTRATOR: UserPerm.ADMINISTRATOR.value[-1],
    UserPerm.OWNER: UserPerm.OWNER.value[-1],
    UserPerm.BOT_ADMIN: UserPerm.BOT_ADMIN.value[-1],
    UserPerm.BOT_OWNER: UserPerm.BOT_OWNER.value[-1],
    UserPerm.INFINITE: UserPerm.INFINITE.value[-1],
    MemberPerm.Member: "普通成员",
    MemberPerm.Administrator: "管理员",
    MemberPerm.Owner: "群主",
}
