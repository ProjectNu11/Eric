from contextvars import ContextVar

from library.model.repo import GenericPluginRepo
from library.module.manager.model.module import RemoteModule

repositories: ContextVar[list[GenericPluginRepo]] = ContextVar(
    "repositories", default=[]
)
remote_modules: ContextVar[list[RemoteModule]] = ContextVar(
    "remote_modules", default=[]
)
