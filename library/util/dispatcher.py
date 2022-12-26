from graia.ariadne.message.parser.twilight import UnionMatch
from kayaku import create

from library.model.config import FunctionConfig


class PrefixMatch(UnionMatch):
    """前缀匹配"""

    def __init__(self, *prefixes: str, optional: bool = False):
        config: FunctionConfig = create(FunctionConfig)
        super().__init__(
            *{str(p) for p in [*config.prefix, *prefixes]}, optional=optional
        )
