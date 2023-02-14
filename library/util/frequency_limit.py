from datetime import timedelta
from heapq import heappush
from time import time

from graia.amnesia.transport.common.storage import CacheStorage
from kayaku import create

from library.model.config import FrequencyLimitConfig
from library.model.exception import (
    FrequencyLimitFieldHit,
    FrequencyLimitGlobalHit,
    FrequencyLimitUserHit,
)
from library.util.typ import FieldWide, SenderWide


class FrequencyLimitCache(CacheStorage[int]):
    cache: dict[int, list[tuple[float, int, int]]]
    """{field: [(expire_time, count, user), ...]}"""
    expire: list[tuple[float, int]]
    """[(expire_time, field), ...]"""

    def __init__(
        self,
        cache: dict[int, list[tuple[float, int, int]]],
        expire: list[tuple[float, int]],
    ):
        self.cache = cache
        self.expire = expire

    async def get(self, key: str, default: int = 0) -> int:
        """Not implemented"""
        raise NotImplementedError(
            "Use `user_check`, `field_check` or `global_check` instead."
        )

    def user_check(self, user: int, *, suppress: bool = False) -> int:
        cap = create(FrequencyLimitConfig).user_max
        total = sum(
            sum(
                map(
                    lambda x: x[1],
                    filter(lambda x: x[2] == user, self.cache.get(field, [])),
                )
            )
            for field in self.cache
        )
        if not suppress and cap and total >= cap:
            raise FrequencyLimitUserHit(user=user, weight=total)
        return total

    def field_check(self, field: int, *, suppress: bool = False) -> int:
        cap = create(FrequencyLimitConfig).field_max
        total = sum(map(lambda x: x[1], self.cache.get(field, [])))
        if not suppress and cap and total >= cap:
            raise FrequencyLimitFieldHit(field=field, weight=total)
        return total

    def global_check(self, *, suppress: bool = False) -> int:
        cap = create(FrequencyLimitConfig).global_max
        total = sum(
            sum(map(lambda x: x[1], self.cache.get(field, []))) for field in self.cache
        )
        if not suppress and cap and total >= cap:
            raise FrequencyLimitGlobalHit(weight=total)
        return total

    async def set(
        self,
        key: str,
        value: int,
        expire: timedelta = None,
    ) -> None:
        field, user = key.split(":")
        field = int(field)
        user = int(user)
        self.user_check(user)
        self.field_check(field)
        self.global_check()
        if expire is None:
            expire = timedelta(seconds=create(FrequencyLimitConfig, flush=True).flush)
        expire_time = time() + expire.total_seconds()
        self.cache.setdefault(field, [])
        heappush(self.cache[field], (expire_time, value, user))
        heappush(self.expire, (expire_time, field))

    async def add(self, field: FieldWide, user: SenderWide, weight: int) -> None:
        field = int(field)
        user = int(user)
        await self.set(f"{field}:{user}", weight)

    async def delete(self, key: int, strict: bool = False) -> None:
        if strict or key in self.cache:
            del self.cache[key]

    async def clear(self) -> None:
        self.cache.clear()
        self.expire.clear()

    async def has(self, key: int) -> bool:
        return key in self.cache

    async def keys(self) -> list[int]:
        return list(self.cache.keys())
