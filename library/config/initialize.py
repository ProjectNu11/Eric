import sys
from contextvars import ContextVar
from pathlib import Path

import kayaku
from kayaku import create
from loguru import logger

from library.config.validate import validate_config
from library.model.config import (
    DatabaseConfig,
    DataPathConfig,
    EricConfig,
    FastAPIConfig,
    FrequencyLimitConfig,
    FunctionConfig,
    ManagerConfig,
    ModuleState,
    MySQLConfig,
    PathConfig,
)

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
        _bootstrap("已写入默认配置文件，请修改后重启")
        sys.exit(1)
    validate_config()
    _bootstrap("配置初始化完成")


def _bootstrap(msg):
    kayaku.bootstrap()
    kayaku.save_all()
    logger.success(msg)
