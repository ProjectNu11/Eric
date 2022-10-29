from contextvars import ContextVar

from library.model.repo import GenericPluginRepo

repositories: ContextVar[list[GenericPluginRepo]] = ContextVar("repositories")
