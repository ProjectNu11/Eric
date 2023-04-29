from graia.ariadne.message.parser.twilight import UnionMatch
from kayaku import create

from library.model.config import FunctionConfig


class PrefixMatch(UnionMatch):
    """前缀匹配"""

    def __init__(self, *prefixes: str, optional: bool = False):
        super().__init__(
            *{str(p) for p in [*self.get_prefix(), *prefixes]}, optional=optional
        )

    @staticmethod
    def get_prefix() -> list[str]:
        """获取前缀列表"""
        return create(FunctionConfig).prefix
