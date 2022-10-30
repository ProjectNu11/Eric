import json
from datetime import datetime

import aiofiles
from aiohttp import ClientSession, ClientResponseError
from creart import it
from graia.saya import Channel
from loguru import logger

from library.model.repo import GenericPluginRepo
from library.module.manager.util.remote.version import check_update
from library.module.manager.model.module import RemoteModule, RemoteModuleCache
from library.module.manager.model.repository import ParsedRepository
from library.util.module import Modules

channel = Channel.current()
mgr_module = it(Modules).get(channel.module)


async def _update_single(
    repo: GenericPluginRepo, file: str = "metadata.json"
) -> list[RemoteModule]:
    async with ClientSession() as s:
        data = json.loads((await repo.get_file(s, file)).decode("utf-8"))
        return [RemoteModule(**module, repo=repo) for module in data]


async def _update_cache(cache: RemoteModuleCache):
    async with aiofiles.open(
        mgr_module.data_path / "repo_cache.json", "w", encoding="utf-8"
    ) as f:
        await f.write(cache.json(ensure_ascii=False))


async def update() -> tuple[list[RemoteModule], list[GenericPluginRepo]]:
    failed: list[GenericPluginRepo] = []
    result: list[RemoteModule] = []
    for repo in it(ParsedRepository):
        try:
            result.extend(await _update_single(repo))
        except ClientResponseError:
            failed.append(repo)
    result = sorted(list(set(result)), key=lambda m: m.name)
    cache = RemoteModuleCache(last_update=datetime.now(), modules=result)
    _cache = it(RemoteModuleCache)
    _cache.last_update = cache.last_update
    _cache.modules = cache.modules
    await _update_cache(cache)
    logger.success("[Manager] 远端模块缓存更新成功")
    return result, failed


async def update_gen_msg() -> str:
    modules, failed = await update()
    msg = f"成功拉取 {len(modules)} 个模块"
    for module in modules:
        msg += f"\n - {module.name} ({module.clean_name})"
    if failed:
        msg += f"\n\n{len(failed)} 个仓库拉取失败"
        for repo in failed:
            msg += f"\n - {repo.__name__}"
    if updates := check_update():
        msg += f"\n\n{len(updates)} 个模块可更新"
        for local, remote in updates:
            msg += f"\n - {local.name} ({local.clean_name})"
            msg += f"\n   {local.version} -> {remote.version}"
    return msg
