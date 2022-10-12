from pydantic import BaseModel

from library.model.config.service.fastapi import FastAPIConfig


class ServiceConfig(BaseModel):
    """服务配置"""

    fastapi: FastAPIConfig = FastAPIConfig()
    """ FastAPI 配置 """
