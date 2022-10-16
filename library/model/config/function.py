from pydantic import BaseModel


class FrequencyLimitConfig(BaseModel):
    """频率限制配置"""

    flush: int = 10
    """ 刷新间隔（秒） """

    user_max: int = 10
    """ 单用户最大请求权重，为 0 时不限制 """

    field_max: int = 0
    """ 单区域最大请求权重，为 0 时不限制 """

    global_max: int = 0
    """ 全局最大请求权重，为 0 时不限制 """


class FunctionConfig(BaseModel):
    """功能配置"""

    default: bool = False
    """ 是否默认启用 """

    allow_bot: bool = False
    """ 是否允许机器人使用 """

    allow_anonymous: bool = False
    """ 是否允许匿名使用 """

    frequency_limit: FrequencyLimitConfig = FrequencyLimitConfig()
    """ 频率限制配置 """
