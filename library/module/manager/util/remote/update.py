import json

import aiofiles
from aiohttp import ClientSession
from creart import it
from graia.saya import Channel

from library.model.repo import GenericPluginRepo
from library.module.manager.model.module import RemoteModule
from library.module.manager.util.remote.context import repositories, remote_modules
from library.util.module import Modules

channel = Channel.current()
mgr_module = it(Modules).get(channel.module)


async def _update_single(
    repo: GenericPluginRepo, file: str = "metadata.json"
) -> list[RemoteModule]:
    async with ClientSession() as s:
        data = json.loads((await repo.get_file(s, file)).decode("utf-8"))
        return [RemoteModule(**module, repo=repo) for module in data]


async def _update_cache(*modules: RemoteModule):
    async with aiofiles.open(
        mgr_module.data_path / "repo_cache.json", "w", encoding="utf-8"
    ) as f:
        await f.write(
            json.dumps([m.dict() for m in modules], indent=4, ensure_ascii=False)
        )


async def update() -> list[RemoteModule]:
    result: list[RemoteModule] = []
    for repo in repositories.get():
        result.extend(await _update_single(repo))
    result = sorted(list(set(result)), key=lambda m: m.name)
    remote_modules.set(result)
    await _update_cache(*result)
    return result
