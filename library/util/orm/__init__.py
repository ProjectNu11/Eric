from asyncio import Lock
from typing import NoReturn

from kayaku import create
from sqlalchemy import Executable, delete, insert, inspect, select, update
from sqlalchemy.engine import Result
from sqlalchemy.exc import InternalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from library.model.config import DatabaseConfig, MySQLConfig

config: DatabaseConfig = create(DatabaseConfig)
mysql_config: MySQLConfig = create(MySQLConfig)

if config.is_mysql:
    db_mutex = None
    if mysql_config.disable_pooling:
        adapter = {"poolclass": NullPool}
    else:
        adapter = {
            "pool_size": mysql_config.pool_size,
            "max_overflow": mysql_config.max_overflow,
        }
else:
    db_mutex = Lock()
    adapter = {}


class AsyncEngine:
    def __init__(self, db_link):
        self.engine = create_async_engine(db_link, **adapter, echo=False)

    async def execute(self, sql: Executable, **kwargs) -> Result:
        """
        执行 SQL 语句

        Args:
            sql: SQL 语句
            **kwargs: 传递给 `execute` 的参数

        Returns:
            Result: 执行结果

        Raises:
            InternalError: 执行失败
        """

        async with AsyncSession(self.engine) as session:
            try:
                if db_mutex:
                    await db_mutex.acquire()
                result = await session.execute(sql, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                if db_mutex:
                    db_mutex.release()

    async def all(self, sql):
        """
        取得所有结果

        Args:
            sql: SQL 语句

        Returns:
            list: 所有结果
        """

        return (await self.execute(sql)).all()

    async def first(self, sql):
        """
        取得第一个结果

        Args:
            sql: SQL 语句

        Returns:
            Any: 第一个结果，如果没有结果则返回 None
        """

        result = await self.execute(sql)
        return one if (one := result.first()) else None

    async def fetchone(self, sql):
        """
        取得第一个结果

        Args:
            sql: SQL 语句

        Returns:
            Any: 第一个结果，如果没有结果则返回 None
        """

        result = await self.execute(sql)
        return one if (one := result.fetchone()) else None

    async def fetchone_dt(self, sql, n: int = 999999):
        """
        以字典生成器的方式取得结果

        Args:
            sql: SQL 语句
            n (int, optional): 最大取得结果数，默认为 999999

        Returns:
            Any: 生成器
        """

        result = await self.execute(sql)
        columns = list(result.keys())
        length = len(columns)
        for _ in range(n):
            if one := result.fetchone():
                yield {columns[i]: one[i] for i in range(length)}


class AsyncORM(AsyncEngine):
    """对象关系映射"""

    def __init__(self, conn):
        super().__init__(conn)
        self.session = AsyncSession(bind=self.engine)
        self.Base = declarative_base()
        self.async_session = async_sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def create_all(self):
        """创建所有表"""

        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    async def drop_all(self):
        """丢弃所有表"""

        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.drop_all)

    async def add(self, table, **dt):
        """
        向表添加数据。

        Args:
            table: 要添加到的表。
            **dt: 数据。
        """

        async with self.async_session() as session:
            async with session.begin():
                session.add(table(**dt), _warn=False)
            await session.commit()

    async def update(self, table, condition, dt):
        """
        更新数据。

        Args:
            table: 表名。
            condition: 条件。
            dt: 数据。

        Returns:
            Result: SQL 结果
        """

        await self.execute(update(table).where(*condition).values(**dt))

    async def insert_or_update(self, table, condition, **dt):
        """
        数据不存在的情况下，插入数据，否则更新数据。

        Args:
            table: 表名。
            condition: 条件。
            **dt: 数据。

        Returns:
            Result: SQL 结果
        """

        if (await self.execute(select(table).where(*condition))).all():
            return await self.execute(update(table).where(*condition).values(**dt))
        return await self.execute(insert(table).values(**dt))

    async def insert_or_ignore(self, table, condition, **dt):
        """
        如不存在的数据果插入或忽略。

        Args:
            table: 表名。
            condition (Iterable): 条件。
            dt (dict): 数据。

        Returns:
            Result: SQL 结果
        """

        if not (await self.execute(select(table).where(*condition))).all():
            return await self.execute(insert(table).values(**dt))

    async def delete(self, table, condition):
        """
        删除数据。

        Args:
            table: 表名。
            condition (list): 条件。

        Returns:
            Result: SQL 结果
        """

        return await self.execute(delete(table).where(*condition))

    async def init_check(self) -> NoReturn:
        """初始化检查"""

        for table in self.Base.__subclasses__():
            if not await self.table_exists(table.__tablename__):
                table.__table__.create(self.engine)
        return None

    @staticmethod
    def use_inspector(conn):
        """
        获取表名

        Args:
            conn (str): 连接

        Returns:
            list: 表名列表
        """

        inspector = inspect(conn)
        return inspector.get_table_names()

    async def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在。

        Args:
            table_name (str): 表名

        Returns:
            bool: 是否存在
        """

        async with self.engine.connect() as conn:
            tables = await conn.run_sync(self.use_inspector)
        return table_name in tables


orm = AsyncORM(config.link)
Base = orm.Base


async def db_init():
    """初始化数据库"""

    try:
        await orm.init_check()
    except (AttributeError, InternalError, ProgrammingError):
        await orm.create_all()
