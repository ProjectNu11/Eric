from abc import ABC
from datetime import datetime
from json import JSONDecodeError
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module, it, add_creator
from graia.saya import Channel
from loguru import logger
from pydantic import BaseModel, ValidationError

from library.model.module import ModuleMetadata
from library.model.repo import GithubPluginRepo, HTTPPluginRepo
from library.module.manager.util.remote import parse_repo
from library.util.module import Modules

channel = Channel.current()


class RemoteModule(ModuleMetadata):
    size: int = -1
    """模块大小"""

    files: list[str] = []
    """模块文件列表"""

    repo: GithubPluginRepo | HTTPPluginRepo
    """模块仓库"""


class RemoteModuleCache(BaseModel):
    last_update: datetime = datetime.fromtimestamp(0)
    """最后更新时间"""

    modules: list[RemoteModule] = []
    """模块列表"""


class RemoteCacheCreator(AbstractCreator, ABC):
    targets = (
        CreateTargetInfo("library.module.manager.model.module", "RemoteModuleCache"),
    )

    @staticmethod
    def available() -> bool:
        return exists_module("library.module.manager.model.module")

    @staticmethod
    def create(_create_type: Type[RemoteModuleCache]) -> RemoteModuleCache:
        parse_repo()
        cache = it(Modules).get(channel.module).data_path / "repo_cache.json"
        try:
            _cache = RemoteModuleCache.parse_file(cache)
            logger.success("[Manager] 远端模块缓存加载成功")
        except (FileNotFoundError, ValidationError, JSONDecodeError):
            logger.warning("[Manager] 无法加载远端模块缓存，将写入空白缓存")
            with cache.open("w", encoding="utf-8") as f:
                _cache = RemoteModuleCache(last_update=datetime.now())
                f.write(_cache.json(indent=4, ensure_ascii=False))
        return _cache


add_creator(RemoteCacheCreator)
