from datetime import datetime

from pydantic import BaseModel

from library.model.module import ModuleMetadata
from library.model.repo import GithubPluginRepo, HTTPPluginRepo


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