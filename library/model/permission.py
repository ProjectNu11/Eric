from enum import Enum

from graia.ariadne.model import MemberPerm
from typing_extensions import Self


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
