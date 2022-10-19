from dataclasses import field

from kayaku import config


@config("config")
class EricConfig:
    """Eric 配置"""

    name: str = "Eric"
    """ 机器人名称 """

    accounts: list[int] = field(default_factory=list)
    """ 机器人账号 """

    default_account: int = 0
    """ 默认账号 """

    description: str = ""
    """ 机器人描述 """

    environment: str = ""
    """ 包管理器 """

    host: str = ""
    """ mirai-api-http 服务器地址 """

    verify_key: str = ""
    """ mirai-api-http 服务器验证密钥 """

    owners: list[int] = field(default_factory=list)
    """ 机器人所有者 """

    dev_groups: list[int] = field(default_factory=list)
    """ 机器人开发者群 """

    debug: bool = False
    """ 是否开启调试模式 """

    proxy: str = None
    """ 代理 """

    log_rotate: int = 7
    """ 日志文件保留天数 """
