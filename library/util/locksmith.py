from asyncio import Lock
from contextlib import asynccontextmanager
from typing import Callable

from loguru import logger


class LockSmith:
    """简易的锁管理器"""

    _lock: dict[str, Lock] = {}

    def get(
        self, name: str, no_assert: bool = True, assert_msg: str = "{name} 已被锁定"
    ) -> Lock:
        """
        获取锁，如果锁不存在则创建一个新的锁

        Args:
            name: 锁的名称，建议使用 `channel.module` 或形如 `channel.module:function` 的形式
            no_assert: 是否禁用断言
            assert_msg: 断言失败时的提示信息，可使用 `{name}` 作为锁名称的占位符

        Returns:
            Lock
        """
        if name not in self._lock:
            logger.info(f"[LockSmith] 创建锁 {name}")
            self._lock[name] = Lock()
        if not no_assert:
            assert not self._lock[name].locked(), assert_msg.format(name=name)
        return self._lock[name]

    async def release(self, name: str, pop: bool = False):
        """
        强制释放锁

        Args:
            name: 锁的名称，建议使用 `channel.module`
            pop: 是否从锁管理器中移除该锁
        """
        if name in self._lock:
            logger.info(f"[LockSmith] 释放锁 {name}")
            self._lock[name].release()
            if pop:
                logger.info(f"[LockSmith] 销毁锁 {name}")
                del self._lock[name]

    async def require(self, name: str, function: str | Callable = ""):
        """
        强制等待锁

        Args:
            name: 锁的名称，建议使用 `channel.module`
            function: 要等待的函数或函数名，用于日志输出
        """
        function = function.__name__ if isinstance(function, Callable) else function
        function = f" {function}" if function else ""
        if name in self._lock:
            logger.info(
                f"[LockSmith] 等待锁 {name}{function}，"
                f"当前锁状态：{self._lock[name].locked()}"
            )
            await self._lock[name].acquire()
            logger.info(
                f"[LockSmith] 获取锁 {name}{function}，"
                f"当前锁状态：{self._lock[name].locked()}"
            )

    @asynccontextmanager
    async def lock(
        self, name: str, no_assert: bool = True, assert_msg: str = "{name} 已被锁定"
    ):
        """
        锁上下文管理器

        Args:
            name: 锁的名称，建议使用 `channel.module`
            no_assert: 是否禁用断言
            assert_msg: 断言失败时的提示信息，可使用 `{name}` 作为锁名称的占位符
        """
        lock = self.get(name, no_assert, assert_msg)
        await lock.acquire()
        logger.info(f"[LockSmith] 获取锁 {name}")
        try:
            yield lock
        finally:
            lock.release()
            logger.info(f"[LockSmith] 释放锁 {name}")
