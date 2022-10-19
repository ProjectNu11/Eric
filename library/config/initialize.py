import kayaku
from kayaku import create
from loguru import logger

from library.model.config.database import DatabaseConfig, MySQLConfig
from library.model.config.eric import EricConfig
from library.model.config.function import FunctionConfig, FrequencyLimitConfig
from library.model.config.path import PathConfig, DataPathConfig
from library.model.config.service.fastapi import FastAPIConfig
from library.model.config.service.manager import ManagerConfig


def initialize_config():
    create(MySQLConfig)
    create(DatabaseConfig)
    create(FrequencyLimitConfig)
    create(FunctionConfig)
    create(DataPathConfig)
    create(PathConfig)
    create(FastAPIConfig)
    create(ManagerConfig)
    create(EricConfig)
    kayaku.bootstrap()
    kayaku.save_all()
    logger.success("配置初始化完成")
