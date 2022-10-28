import sys
from contextvars import ContextVar
from pathlib import Path

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


FIRST_RUN = ContextVar("FIRST_RUN", default=False)


def first_run_check():
    with (Path("config") / "config.jsonc").open("r", encoding="utf-8") as f:
        FIRST_RUN.set(f.read() == "")


def initialize_config():
    first_run_check()
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
    if FIRST_RUN.get():
        kayaku.bootstrap()
        kayaku.save_all()
        logger.success("已写入默认配置文件，请修改后重启")
        sys.exit(1)
    validate_config()
    kayaku.bootstrap()
    kayaku.save_all()
    logger.success("配置初始化完成")
