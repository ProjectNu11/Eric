from typing import Any

from pydantic import BaseModel, AnyHttpUrl


class FastAPIConfig(BaseModel):
    """FastAPI 配置"""

    host: str = "127.0.0.1"
    """ FastAPI 服务器地址 """

    port: int = 8000
    """ FastAPI 服务器端口 """

    domain: AnyHttpUrl | None = None
    """ FastAPI 服务器域名，仅在发送消息时使用 """

    params: dict[str, Any] = {}
    """ FastAPI 服务器参数 """
