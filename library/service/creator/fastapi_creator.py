from abc import ABC
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module
from fastapi import FastAPI
from kayaku import create
from kayaku.backend.types import JWrapper

from library.model.config.service.fastapi import FastAPIConfig


class FastAPICreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("fastapi.applications", "FastAPI"),)

    @staticmethod
    def available() -> bool:
        return exists_module("fastapi.applications")

    @staticmethod
    def create(_create_type: Type[FastAPI]) -> FastAPI:
        config: FastAPIConfig = create(FastAPIConfig)
        return FastAPI(
            **{
                k: v.value if isinstance(v, JWrapper) else v
                for k, v in config.__dict__.get("params", {}).items()
            }
        )
