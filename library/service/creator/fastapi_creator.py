from abc import ABC
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kayaku import create

from library.model.config import FastAPIConfig


class FastAPICreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("fastapi.applications", "FastAPI"),)

    @staticmethod
    def available() -> bool:
        return exists_module("fastapi.applications")

    @staticmethod
    def create(_create_type: Type[FastAPI]) -> FastAPI:
        config: FastAPIConfig = create(FastAPIConfig)
        app = FastAPI(**config.params)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        return app
