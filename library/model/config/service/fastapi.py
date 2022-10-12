from pydantic import BaseModel


class FastAPIConfig(BaseModel):
    """FastAPI 配置"""

    host: str = "127.0.0.1"
    """ FastAPI 服务器地址 """

    port: int = 8000
    """ FastAPI 服务器端口 """

    docs_url: str | None = None
    """ FastAPI 文档地址 """
