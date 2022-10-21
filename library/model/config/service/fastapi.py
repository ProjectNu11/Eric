from dataclasses import field

from kayaku import config


@config("library.service.fastapi")
class FastAPIConfig:
    """FastAPI 配置"""

    host: str = "127.0.0.1"
    """ FastAPI 服务器地址 """

    port: int = 8000
    """ FastAPI 服务器端口 """

    domain: str = ""
    """ FastAPI 服务器域名，仅在发送消息时使用 """

    params: dict = field(default_factory=dict)
    """ FastAPI 服务器参数，将在启动时传入 """
