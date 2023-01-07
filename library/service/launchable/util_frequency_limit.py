import asyncio
from time import time

from _heapq import heappop
from launart import Launart, Service

from library.util.frequency_limit import FrequencyLimitCache


class FrequencyLimitService(Service):
    id = "eric.util.frequency_limit"
    supported_interface_types = {FrequencyLimitCache}

    interval: float
    cache: dict[int, list[tuple[float, int, int]]]
    expire: list[tuple[float, int]]

    def __init__(
        self,
        interval: float = 0.1,
        cache: dict[int, list[tuple[float, int, int]]] = None,
        expire: list[tuple[float, int]] = None,
    ):
        self.interval = interval
        self.cache = cache or {}
        self.expire = expire or []
        super().__init__()

    def get_interface(self, _) -> FrequencyLimitCache:
        return FrequencyLimitCache(self.cache, self.expire)

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, manager: Launart) -> None:
        async with self.stage("blocking"):
            while not manager.status.exiting:
                while self.expire and self.expire[0][0] <= time():
                    _, key = heappop(self.expire)
                    heappop(self.cache[key])
                await asyncio.sleep(self.interval)
