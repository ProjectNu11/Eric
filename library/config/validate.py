import re
from pathlib import Path
from typing import Any

from kayaku import create
from loguru import logger

from library.model.config import (
    DatabaseConfig,
    DataPathConfig,
    EricConfig,
    FastAPIConfig,
    ManagerConfig,
    MySQLConfig,
    PathConfig,
)
from library.model.exception import InvalidConfig


def _assert(exceptions: list[AssertionError], condition: Any, msg: str):
    try:
        assert condition, msg
    except AssertionError as e:
        exceptions.append(e)


def _validate_mysql_config() -> list[tuple[type, list[AssertionError]]]:
    exceptions: list[AssertionError] = []
    db_cfg: DatabaseConfig = create(DatabaseConfig)
    if not db_cfg.is_mysql:
        return [(MySQLConfig, exceptions)]
    cfg: MySQLConfig = create(MySQLConfig)
    _assert(
        exceptions,
        not all(
            [
                cfg.pool_size + cfg.max_overflow <= 0,
                not cfg.disable_pooling,
            ]
        ),
        "禁用连接池时，连接池大小和最大溢出数必须大于 0",
    )
    return [(MySQLConfig, exceptions)]


def _validate_database_link() -> list[tuple[type, list[AssertionError]]]:
    exceptions: list[AssertionError] = []
    cfg: DatabaseConfig = create(DatabaseConfig)
    example = (
        "Example:\n"
        "MySQL:\tmysql+aiomysql://user:password@localhost:3306/database\n"
        "SQLite:\tsqlite+aiosqlite:///data/data.db"
    )
    _assert(exceptions, cfg.link, f"数据库链接不能为空\n{example}")
    _assert(
        exceptions,
        any(
            [
                cfg.link.startswith("mysql+aiomysql://"),
                cfg.link.startswith("sqlite+aiosqlite://"),
            ]
        ),
        f"仅支持 MySQL 和 SQLite 数据库\n{example}",
    )
    return [(DatabaseConfig, exceptions)]


def _validate_path() -> list[tuple[type, list[AssertionError]]]:
    exceptions: list[list[AssertionError]] = []
    cfg = [create(PathConfig), create(DataPathConfig)]
    for c in cfg:
        exc = []
        for name, path in c.__dict__.items():
            _assert(exc, path, f"{name} 不能为空")
            if not Path(path).is_dir():
                logger.info(f"创建 {name} 目录 {path}")
                Path(path).mkdir(parents=True)
        exceptions.append(exc)
    return [(PathConfig, exceptions[0]), (DataPathConfig, exceptions[1])]


def _validate_eric_config() -> list[tuple[type, list[AssertionError]]]:
    exceptions: list[AssertionError] = []
    cfg: EricConfig = create(EricConfig)
    _assert(exceptions, cfg.name, "机器人名称不能为空")
    cfg.accounts = sorted(list(set(cfg.accounts)))
    _assert(exceptions, cfg.accounts, "机器人账号不能为空")
    _assert(exceptions, cfg.host, "mirai-api-http 服务器地址不能为空")
    _assert(exceptions, cfg.verify_key, "mirai-api-http 验证密钥不能为空")
    cfg.owners = sorted(list(set(cfg.owners)))
    cfg.dev_groups = sorted(list(set(cfg.dev_groups)))
    _assert(exceptions, cfg.log_rotate, "日志保留天数不能小于 0")
    return [(EricConfig, exceptions)]


def _validate_plugin_repo() -> list[tuple[type, list[AssertionError]]]:
    exceptions: list[AssertionError] = []
    cfg: ManagerConfig = create(ManagerConfig)
    processed = []
    for repo in cfg.plugin_repo:
        _assert(
            exceptions,
            repo.startswith("github") or repo.startswith("http"),
            f"仅支持 GitHub 和 HTTP 协议的模块仓库，不支持 {repo}",
        )
        repo = repo.rstrip(".git") if repo.startswith("github") else repo.rstrip("/")
        processed.append(repo)
    processed = sorted(list(set(processed)))
    cfg.plugin_repo = processed
    return [(ManagerConfig, exceptions)]


def _validate_fastapi_config() -> list[tuple[type, list[AssertionError]]]:
    exceptions: list[AssertionError] = []
    cfg: FastAPIConfig = create(FastAPIConfig)
    _assert(
        exceptions,
        re.match(
            r"^((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$",
            cfg.host,
        ),
        "FastAPI 服务器地址不合法",
    )
    cfg.domain = cfg.domain.rstrip("/")
    return [(FastAPIConfig, exceptions)]


def _build_msg(exceptions: list[tuple[type, list[AssertionError]]]) -> str:
    msg = ""
    for cfg, assertions in exceptions:
        if not assertions:
            continue
        msg += f"\n\n{cfg.__name__}\n"
        msg += "\n".join(f"\t{assertion.args[0]}" for assertion in assertions)
    return msg


def validate_config():
    if msg := _build_msg(
        _validate_mysql_config()
        + _validate_database_link()
        + _validate_path()
        + _validate_eric_config()
        + _validate_plugin_repo()
        + _validate_fastapi_config()
    ):
        raise InvalidConfig(msg)
    logger.success("配置验证通过")
