import sys
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


def first_run_check() -> bool:
    cfg_path = Path("config") / "config.jsonc"
    if not cfg_path.exists():
        return True
    with cfg_path.open("r", encoding="utf-8") as f:
        return f.read() == ""


def initialize_config():
    first_run = first_run_check()
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
    if first_run:
        _bootstrap("已写入默认配置文件，请修改后重启")
        sys.exit(1)
    validate_config()
    _bootstrap("配置初始化完成")


def _bootstrap(msg):
    kayaku.bootstrap()
    kayaku.save_all()
    logger.success(msg)
