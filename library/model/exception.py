from library.util.misc import inflate


class SkipRequiring(Exception):
    """跳过导入"""


class RequirementResolveFailed(ModuleNotFoundError):
    """依赖解析失败"""

    def __init__(self, *modules):
        self.modules = inflate(modules)


class MessageEmpty(Exception):
    """消息为空"""


class FrequencyLimitHit(Exception):
    """频率限制命中"""


class FrequencyLimitUserHit(FrequencyLimitHit):
    """频率限制用户命中"""

    def __init__(self, user: int, weight: int):
        self.user = user
        self.weight = weight

    def __str__(self):
        return f"用户 {self.user} 已达到频率限制 {self.weight}"


class FrequencyLimitFieldHit(FrequencyLimitHit):
    """频率限制聊天区域命中"""

    def __init__(self, field: int, weight: int):
        self.field = field
        self.weight = weight

    def __str__(self):
        return f"聊天区域 {self.field} 已达到频率限制 {self.weight}"


class FrequencyLimitGlobalHit(FrequencyLimitHit):
    """全局频率限制命中"""

    def __init__(self, weight: int):
        self.weight = weight

    def __str__(self):
        return f"全局频率限制已达到 {self.weight}"


class InvalidConfig(Exception):
    """无效配置"""
