from library.util.misc import inflate


class SkipRequiring(Exception):
    """跳过导入"""


class RequirementResolveFailed(ModuleNotFoundError):
    """依赖解析失败"""

    def __init__(self, *modules):
        self.modules = inflate(modules)
