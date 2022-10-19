from abc import ABC
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module
from fastapi import FastAPI
from kayaku import create

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
