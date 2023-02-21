from typing import TYPE_CHECKING

from graia.broadcast import BaseDispatcher, Dispatchable

if TYPE_CHECKING:
    from library.util.user_profile import UserProfile


class UserProfilePendingUpdate(Dispatchable):
    """用户资料待更新事件"""

    profile: "UserProfile"

    def __init__(self, profile: "UserProfile"):
        self.profile = profile

    Dispatcher = BaseDispatcher
