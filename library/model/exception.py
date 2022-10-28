class SkipRequiring(Exception):
    """跳过导入"""


class RequirementResolveFailed(ModuleNotFoundError):
    """依赖解析失败"""
