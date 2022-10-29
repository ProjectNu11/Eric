from abc import abstractmethod
from pathlib import Path

import aiofiles
from aiohttp import ClientSession, ClientResponseError
from kayaku import create
from loguru import logger
from pydantic import BaseModel

from library.model.config.eric import EricConfig


class GenericPluginRepo(BaseModel):
    @property
    def __name__(self):
        return "GenericPluginRepo"

    def __hash__(self):
        return hash(f"_{self.__name__}")

    @abstractmethod
    def get_file_url(self, path: str) -> str:
        pass

    async def get_file(self, session: ClientSession, path: str, **params) -> bytes:
        config: EricConfig = create(EricConfig)
        async with session.get(
            self.get_file_url(path), **{"proxy": config.proxy, **params}
        ) as resp:
            resp.raise_for_status()
            return await resp.read()

    async def file_to_disk(self, base_path: Path, *paths: str, **params) -> list[str]:
        failed: list[str] = []
        async with ClientSession() as session:
            for path in paths:
                write_path = base_path / path
                write_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    data = await self.get_file(session, path, **params)
                    async with aiofiles.open(write_path, "ab") as f:
                        await f.write(data)
                        logger.success(f"[PluginRepo] 下载文件成功: {path}")
                except ClientResponseError as err:
                    logger.error(f"[PluginRepo] 下载文件失败: {err}")
                    failed.append(path)
        return failed


class GithubPluginRepo(GenericPluginRepo):
    owner: str
    repo: str
    branch: str

    @property
    def raw_url(self) -> str:
        return "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

    @property
    def __name__(self) -> str:
        return f"GithubPluginRepo:{self.owner}/{self.repo}@{self.branch}"

    def get_file_url(self, path: str) -> str:
        return self.raw_url.format(
            owner=self.owner, repo=self.repo, branch=self.branch, path=path
        )


class HTTPPluginRepo(GenericPluginRepo):
    url: str

    @property
    def raw_url(self) -> str:
        return "{url}/{path}"

    @property
    def __name__(self) -> str:
        return f"HTTPPluginRepo:{self.url}"

    def get_file_url(self, path: str) -> str:
        return self.raw_url.format(url=self.url, path=path)
