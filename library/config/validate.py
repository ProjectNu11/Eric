import re
from pathlib import Path

from kayaku import create
from loguru import logger

from library.model.config.database import MySQLConfig, DatabaseConfig
from library.model.config.eric import EricConfig
from library.model.config.path import DataPathConfig, PathConfig
from library.model.config.service.fastapi import FastAPIConfig
from library.model.config.service.manager import ManagerConfig


def _validate_mysql_config():
    db_cfg: DatabaseConfig = create(DatabaseConfig)
    if not db_cfg.is_mysql:
        return
    cfg: MySQLConfig = create(MySQLConfig)
    if all(
        [
            cfg.pool_size + cfg.max_overflow <= 0,
            not cfg.disable_pooling,
        ]
    ):
        raise ValueError("禁用连接池时，连接池大小和最大溢出数必须大于 0")


def _validate_database_link():
    cfg: DatabaseConfig = create(DatabaseConfig)
    example = (
        "Example:\n"
        "MySQL:\tmysql+aiomysql://user:password@localhost:3306/database\n"
        "SQLite:\tsqlite+aiosqlite:///data/data.db"
    )
    if not cfg.link:
        raise ValueError(f"数据库链接不能为空\n{example}")
    if not any(
        [
            cfg.link.startswith("mysql+aiomysql://"),
            cfg.link.startswith("sqlite+aiosqlite://"),
        ]
    ):
        raise NotImplementedError(f"仅支持 MySQL 和 SQLite 数据库\n{example}")


def _validate_path():
    cfg = [create(PathConfig), create(DataPathConfig)]
    for c in cfg:
        for name, path in c.__dict__.items():
            if not path:
                raise ValueError(f"{name} 不能为空")
            if not Path(path).is_dir():
                logger.info(f"创建 {name} 目录 {path}")
                Path(path).mkdir(parents=True)


def _validate_eric_config():
    cfg: EricConfig = create(EricConfig)
    if not cfg.name:
        raise ValueError("机器人名称不能为空")
    cfg.accounts = sorted(list(set(cfg.accounts)))
    if not cfg.accounts:
        raise ValueError("机器人账号不能为空")
    if not cfg.host:
        raise ValueError("mirai-api-http 服务器地址不能为空")
    if not cfg.verify_key:
        raise ValueError("mirai-api-http 验证密钥不能为空")
    cfg.owners = sorted(list(set(cfg.owners)))
    cfg.dev_groups = sorted(list(set(cfg.dev_groups)))
    if cfg.log_rotate < 0:
        raise ValueError("日志保留天数不能小于 0")


def _validate_plugin_repo():
    cfg: ManagerConfig = create(ManagerConfig)
    processed = []
    for repo in cfg.plugin_repo:
        if not repo.startswith("github") or not repo.startswith("http"):
            raise ValueError(f"仅支持 GitHub 和 HTTP 协议的插件仓库，不支持 {repo}")
        repo = repo.rstrip(".git") if repo.startswith("github") else repo.rstrip("/")
        processed.append(repo)
    processed = sorted(list(set(processed)))
    cfg.plugin_repo = processed


def _validate_fastapi_config():
    cfg: FastAPIConfig = create(FastAPIConfig)
    if not re.match(
        r"^((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$",
        cfg.host,
    ):
        raise ValueError("FastAPI 服务器地址不合法")
    cfg.domain = cfg.domain.rstrip("/")


def validate_config():
    _validate_mysql_config()
    _validate_database_link()
    _validate_path()
    _validate_eric_config()
    _validate_plugin_repo()
    _validate_fastapi_config()
    logger.success("配置验证通过")
