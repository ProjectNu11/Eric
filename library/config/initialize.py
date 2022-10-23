import kayaku
from kayaku import create
from loguru import logger

from library.config.validate import validate_config
from library.model.config.database import DatabaseConfig, MySQLConfig
from library.model.config.eric import EricConfig
from library.model.config.function import FunctionConfig, FrequencyLimitConfig
from library.model.config.path import PathConfig, DataPathConfig
from library.model.config.service.fastapi import FastAPIConfig
from library.model.config.service.manager import ManagerConfig
from library.model.config.state import ModuleState


def initialize_config():
    create(MySQLConfig)
    create(DatabaseConfig)
    create(FrequencyLimitConfig)
    create(FunctionConfig)
    create(DataPathConfig)
    create(PathConfig)
    create(ModuleState)
    create(FastAPIConfig)
    create(ManagerConfig)
    create(EricConfig)
    validate_config()
    kayaku.bootstrap()
    kayaku.save_all()
    logger.success("配置初始化完成")
