from contextlib import suppress

from aiohttp import ClientSession
from loguru import logger


class SessionContainer:
    session: dict[str, ClientSession] = {}

    async def get(
        self, name: str = "universal", flush: bool = False, **kwargs
    ) -> ClientSession:
        if flush or name not in self.session or self.session[name].closed:
            self.session[name] = ClientSession(**kwargs)
            logger.success(f"[SessionContainer] Created session {name!r}")
        return self.session[name]

    async def close(self, name: str):
        if name in self.session.copy():
            await self.session[name].close()
            del self.session[name]
            logger.success(f"[SessionContainer] Closed session {name!r}")

    async def close_all(self):
        for name in self.session.copy():
            with suppress(Exception):
                await self.close(name)
