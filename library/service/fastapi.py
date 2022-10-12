from fastapi import FastAPI
from graia.amnesia.builtins.starlette import StarletteService


class FastAPIService(StarletteService):
    def __init__(self, fastapi: FastAPI | None = None) -> None:
        self.fastapi = fastapi or FastAPI()
        super().__init__(self.fastapi)
