import functools

from loguru import logger


def timer(*_, **__):
    def wrapper(func):
        """记录函数运行时间的装饰器"""

        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            logger.warning("[Deprecated] timer 装饰器已被弃用")
            value = func(*args, **kwargs)
            return value

        return wrapper_timer

    return wrapper
