from graia.ariadne.message.parser.twilight import UnionMatch
from kayaku import create

from library.model.config.function import FunctionConfig


class PrefixMatch(UnionMatch):
    """前缀匹配"""

    def __init__(self, optional: bool = False, *prefixes: str):
        config: FunctionConfig = create(FunctionConfig)
        super().__init__(
            *list({str(p) for p in [*config.prefix, *prefixes]}), optional=optional
        )
