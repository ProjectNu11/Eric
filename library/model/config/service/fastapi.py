from dataclasses import field
from typing import Union, Any

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

    show_port: bool = True
    """ 是否在发送消息时显示端口 """

    params: dict[str, Union[None, Any]] = field(default_factory=dict)
    """ FastAPI 服务器参数，将在启动时传入 """

    @property
    def is_exposed(self) -> bool:
        """是否已暴露"""
        return self.domain or self.host != "127.0.0.1"

    @property
    def link(self) -> str:
        """FastAPI 服务器链接"""
        return (
            f"{self.domain or self.host}:{self.port}"
            if self.show_port
            else self.domain or self.host
        )
