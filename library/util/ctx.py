from contextvars import ContextVar

from rich.console import Console

rich_console = ContextVar("rich_console", default=Console())
