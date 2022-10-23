from enum import Enum

from graia.ariadne.model import MemberPerm, Member, Friend
from kayaku import create
from typing_extensions import Self

from library.model.config.eric import EricConfig


class UserPerm(Enum):
    """用户权限"""

    BLOCKED = ("BLOCKED", -1)
    """ 被封禁 """

    BOT = ("BOT", 0)
    """ 机器人 """

    MEMBER = ("MEMBER", 1)
    """ 普通成员 """

    ADMINISTRATOR = ("ADMINISTRATOR", 2)
    """ 管理员 """

    OWNER = ("OWNER", 3)
    """ 群主 """

    BOT_ADMIN = ("BOT_ADMIN", 4)
    """ 机器人管理员 """

    BOT_OWNER = ("BOT_OWNER", 5)
    """ 机器人所有者 """

    INFINITE = ("INFINITE", 999)
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
    async def get(cls, supplicant: int | Member | Friend) -> Self:
        config: EricConfig = create(EricConfig)
        if int(supplicant) in config.owners:
            return cls.BOT_OWNER

        if isinstance(supplicant, Member):
            return cls.from_member_perm(supplicant.permission)

        # TODO Implement UserPerm.BLOCKED
        # TODO Implement UserPerm.BOT
        # TODO Implement UserPerm.BOT_ADMIN

        return cls.MEMBER
