from abc import ABC
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module, create, add_creator
from fastapi import FastAPI
from graia.amnesia.builtins.starlette import StarletteService

from library.model.config.eric import EricConfig


class FastAPICreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("fastapi.applications", "FastAPI"),)

    @staticmethod
    def available() -> bool:
        return exists_module("fastapi.applications")

    @staticmethod
    def create(create_type: Type[FastAPI]) -> FastAPI:
        config = create(EricConfig)
        return FastAPI(**config.service.fastapi.params)


add_creator(FastAPICreator)


class FastAPIService(StarletteService):
    def __init__(self, fastapi: FastAPI | None = None) -> None:
        self.fastapi = fastapi or create(FastAPI)
        super().__init__(self.fastapi)
