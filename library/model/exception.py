from graia.ariadne.message import Source
from graia.ariadne.model import Friend, Group, Member

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


class UserProfileNotFound(Exception):
    """用户资料未找到"""


class RebuildMessageFailed(Exception):
    """重构消息失败"""

    def __init__(self, source: Source | int, target: Group | Friend | Member | int):
        self.source = source
        self.target = target

    def __str__(self):
        return f"重构消息失败：<source={self.source}, target={self.target}>"


class InvalidPermission(Exception):
    """无效权限（细粒度）"""


class OpenAIException(Exception):
    """OpenAI 异常"""


class OpenAIKeyNotConfigured(OpenAIException):
    """OpenAI API Key 未配置"""


class OpenAIInsufficientQuota(OpenAIException):
    """OpenAI 余额不足"""


class ChatCompletionException(OpenAIException):
    """ChatCompletion 异常"""


class ChatEntryNotFound(ChatCompletionException):
    """ChatCompletion 聊天记录未找到"""


class ChatEntryTooLong(ChatCompletionException):
    """ChatCompletion 聊天记录过长"""


class ChatSessionLocked(ChatCompletionException):
    """ChatCompletion 会话已锁定"""
