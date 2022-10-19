from kayaku import config


@config("library.mysql")
class MySQLConfig:
    """MySQL 配置"""

    disable_pooling: bool = False
    """ 是否禁用连接池 """

    pool_size: int = 40
    """ 连接池大小 """

    max_overflow: int = 60
    """ 连接池最大溢出 """


@config("library.database")
class DatabaseConfig:
    """数据库配置"""

    link: str = "sqlite+aiosqlite:///data/data.db"
    """ 数据库链接 """

    @property
    def is_mysql(self) -> bool:
        return self.link.startswith("mysql+aiomysql://")
