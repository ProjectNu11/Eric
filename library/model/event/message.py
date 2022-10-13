from graia.ariadne.model import Group, Friend
from graia.broadcast import Dispatchable, BaseDispatcher


class AccountMessageBanned(Dispatchable):
    """账号消息被封禁"""

    field: int
    """ 聊天区域，为 0 时表示私信"""

    account: int
    """ 账号 """

    def __init__(self, account: int, field: int | Group | Friend):
        self.account = account
        self.field = 0 if isinstance(field, Friend) else int(field)

    Dispatcher = BaseDispatcher
