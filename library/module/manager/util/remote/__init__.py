from json import JSONDecodeError

from creart import it
from graia.saya import Channel
from loguru import logger
from pydantic import ValidationError

from library.module.manager.model.module import RemoteModuleCache
from library.module.manager.util.remote.context import remote_cache
from library.module.manager.util.remote.parse import parse_repo
from library.util.module import Modules

channel = Channel.current()


def initialize():
    parse_repo()
    cache = it(Modules).get(channel.module).data_path / "repo_cache.json"
    try:
        remote_cache.set(RemoteModuleCache.parse_file(cache))
        logger.success("[Manager] 远端模块缓存加载成功")
    except (FileNotFoundError, ValidationError, JSONDecodeError):
        logger.warning("[Manager] 无法加载远端模块缓存，将写入空白缓存")
        with cache.open("w", encoding="utf-8") as f:
            f.write(RemoteModuleCache().json(indent=4, ensure_ascii=False))


initialize()
