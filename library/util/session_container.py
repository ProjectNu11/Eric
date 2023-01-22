from contextlib import suppress

from aiohttp import ClientSession
from loguru import logger


class SessionContainer:
    """会话容器"""

    _session: dict[str, ClientSession] = {}

    async def get(
        self,
        name: str = "universal",
        flush: bool = False,
        base_url: str = None,
        /,
        **kwargs,
    ) -> ClientSession:
        """
        获取一个 aiohttp.ClientSession 对象

        Args:
            name: 会话名称
            flush: 是否刷新会话
            base_url: 会话的基础 URL，仅会在创建时生效
            **kwargs: 传递给 aiohttp.ClientSession 的参数

        Returns:
            aiohttp.ClientSession 对象
        """
        if flush or name not in self._session or self._session[name].closed:
            self._session[name] = ClientSession(base_url=base_url, **kwargs)
            logger.success(f"[SessionContainer] Created session {name!r}")
        return self._session[name]

    async def close(self, name: str):
        """
        关闭一个 aiohttp.ClientSession 对象

        Args:
            name: 会话名称
        """
        if name in self._session.copy():
            await self._session[name].close()
            del self._session[name]
            logger.success(f"[SessionContainer] Closed session {name!r}")

    async def close_all(self):
        """关闭所有 aiohttp.ClientSession 对象，不应被手动调用"""
        for name in self._session.copy():
            with suppress(Exception):
                await self.close(name)
