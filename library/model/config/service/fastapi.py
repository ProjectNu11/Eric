from dataclasses import field
from typing import Any, Union

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

    https: bool = True
    """ FastAPI 服务器是否使用 HTTPS """

    show_port: bool = True
    """ 是否在发送消息时显示端口 """

    params: dict[str, Union[None, Any]] = field(default_factory=dict)
    """ FastAPI 服务器参数，将在启动时传入 """

    @property
    def link(self) -> str:
        """FastAPI 服务器链接"""
        protocol = "https" if self.https else "http"
        address = self.domain or self.host
        port = f":{self.port}" if self.show_port else ""
        return f"{protocol}://{address}{port}"
