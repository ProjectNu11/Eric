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
            call_time = datetime.now()
            start_time = time.perf_counter()
            value = func(*args, **kwargs)
            run_time = time.perf_counter() - start_time
            try:
                # Only insert when returning value
                if value:
                    asyncio.get_event_loop().create_task(
                        insert_timing_record(
                            call_time=call_time,
                            module=module_name,
                            function=func.__name__,
                            time_used=run_time,
                        )
                    )
            except SQLAlchemyError as e:
                logger.error(f"插入 {module_name}:{func.__name__} 计时数据时出错: {e}")
            finally:
                return value

        return wrapper_timer

    return wrapper


async def insert_timing_record(
    call_time: datetime, module: str, function: str, time_used: float
):
    await orm.add(
        ProcessTimeStat,
        time=call_time,
        module=module,
        function=function,
        time_used=time_used,
    )
