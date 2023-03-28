from enum import Enum, auto


class Hashable:
    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"{' '.join(f'{k}={v}' for k, v in self.__dict__.items())}>"
        )

    def __hash__(self):
        return hash(self.__repr__())


class RequireStatus(Enum):
    """模块加载状态"""

    SUCCESS = auto()
    """ 成功加载 """

    SKIPPED = auto()
    """ 跳过加载 """

    MISSING_DEPENDENCY = auto()
    """ 缺少依赖 """

    ERROR = auto()
    """ 意外错误 """
