import asyncio
import functools
import time
from datetime import datetime

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from library.util.orm import orm
from library.util.orm.table import ProcessTimeStat


def timer(module_name: str):
    def wrapper(func):
        """记录函数运行时间的装饰器"""

        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            start_time = time.perf_counter()
            value = func(*args, **kwargs)
            run_time = time.perf_counter() - start_time
            try:

                async def _insert():
                    await orm.add(
                        ProcessTimeStat,
                        time=datetime.now(),
                        module=module_name,
                        function=func.__name__,
                        time_used=run_time,
                    )

                loop = asyncio.get_event_loop()
                loop.create_task(_insert())
            except SQLAlchemyError as e:
                logger.error(f"插入 {module_name}:{func.__name__} 计时数据时出错: {e}")
            return value

        return wrapper_timer

    return wrapper
