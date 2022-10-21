from dataclasses import field

from kayaku import config


@config("library.frequency_limit")
class FrequencyLimitConfig:
    """频率限制配置"""

    flush: int = 10
    """ 刷新间隔（秒） """

    user_max: int = 10
    """ 单用户最大请求权重，为 0 时不限制 """

    field_max: int = 0
    """ 单区域最大请求权重，为 0 时不限制 """

    global_max: int = 0
    """ 全局最大请求权重，为 0 时不限制 """


@config("library.function")
class FunctionConfig:
    """功能配置"""

    default: bool = False
    """ 是否默认启用 """

    allow_bot: bool = False
    """ 是否允许机器人使用 """

    allow_anonymous: bool = False
    """ 是否允许匿名使用 """

    prefix: list[str] = field(default_factory=lambda: [".", "。"])
    """ 命令前缀 """
