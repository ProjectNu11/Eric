from contextvars import ContextVar

from library.model.repo import GenericPluginRepo
from library.module.manager.model.module import RemoteModuleCache

repositories: ContextVar[list[GenericPluginRepo]] = ContextVar(
    "repositories", default=[]
)
remote_cache: ContextVar[RemoteModuleCache] = ContextVar(
    "remote_cache", default=RemoteModuleCache()
)
