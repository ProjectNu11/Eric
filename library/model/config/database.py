from pydantic import BaseModel, root_validator, validator


class MySQLConfig(BaseModel):
    """MySQL 配置"""

    disable_pooling: bool = False
    """ 是否禁用连接池 """

    pool_size: int = 40
    """ 连接池大小 """

    max_overflow: int = 60
    """ 连接池最大溢出 """

    @root_validator()
    def _mysql_config_check(cls, value: dict):
        assert not all(
            [
                value.get("pool_size", 0) + value.get("max_overflow", 0) <= 0,
                not value.get("disable_pooling"),
            ]
        ), "禁用连接池时，连接池大小和最大溢出数必须大于 0"
        return value


class DatabaseConfig(BaseModel):
    """数据库配置"""

    link: str = "sqlite+aiosqlite:///data/data.db"
    """ 数据库链接 """

    config: None | MySQLConfig = None
    """ 额外配置，仅在使用 MySQL 时有效 """

    @validator("link")
    def check_link(cls, link: str):
        example = (
            "Example:\n"
            "MySQL:\tmysql+aiomysql://user:password@localhost:3306/database\n"
            "SQLite:\tsqlite+aiosqlite:///data/data.db"
        )
        assert link, f"数据库链接不能为空\n{example}"
        assert any(
            [
                link.startswith("mysql+aiomysql://"),
                link.startswith("sqlite+aiosqlite://"),
            ]
        ), f"仅支持 MySQL 和 SQLite 数据库\n{example}"
        return link

    @root_validator()
    def config_check(cls, value: dict):
        if value.get("link", "").startswith("mysql+aiomysql://") and not value.get(
            "config", None
        ):
            value["config"] = MySQLConfig()
        elif value.get("link", "").startswith("sqlite+aiosqlite://") and value.get(
            "config", None
        ):
            value["config"] = None
        return value
