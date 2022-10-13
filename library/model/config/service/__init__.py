from pydantic import BaseModel

from library.model.config.service.fastapi import FastAPIConfig
from library.model.config.service.manager import ManagerConfig


class ServiceConfig(BaseModel):
    """服务配置"""

    fastapi: FastAPIConfig = FastAPIConfig()
    """ FastAPI 配置 """

    manager: ManagerConfig = ManagerConfig()
    """ 管理器配置 """
