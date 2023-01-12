import ast
import sys
from _ast import Import, ImportFrom
from pathlib import Path
from typing import Any

from creart import it
from graia.saya import Saya
from loguru import logger

from library.model.module import Module
from library.util.file import invalidate_pycache


class ReloadVisitor(ast.NodeVisitor):
    """重载模块，不应被手动调用"""

    pack: str
    show_log: bool
    reload: set[str]

    def __init__(self, pack: str, show_log: bool = True):
        self.pack = pack
        self.show_log = show_log
        self.reload = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for name in self.reload:
            if name in sys.modules:
                logger.debug(f"[{self.__class__.__name__}] Unload {name}")
                del sys.modules[name]
                continue
            logger.warning(f"[{self.__class__.__name__}] {name} not in sys.modules")

    def add_and_visit(self, file: Path):
        name = ".".join(file.with_suffix("").parts)
        self.reload.add(name)
        with file.open("r", encoding="utf-8") as f:
            node = ast.parse(f.read())
        self.visit(node)

    def _add_queue(self, name: str):
        if not name.startswith(self.pack) or name in self.reload or name == self.pack:
            return
        self.reload.add(name)

    def _resolve_dot(self, node: ImportFrom) -> str:
        level = node.level
        if level == 0:
            return node.module
        elif level == 1:
            return f"{self.pack}.{node.module}"
        return f"{'.'.join(self.pack.split('.')[:level])}.{node.module}"

    def visit_Import(self, node: Import) -> Any:
        for alias in node.names:
            self._add_queue(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        package = self._resolve_dot(node)
        self._add_queue(package)
        self.generic_visit(node)


def reload_module(module: Module):
    """
    重载模块，不应被手动调用

    Args:
        module: 模块
    """
    module_path = Path(module.pack.replace(".", "/"))
    invalidate_pycache(module_path)
    saya = it(Saya)
    channel = saya.channels.get(module.pack)
    with saya.module_context():
        with ReloadVisitor(module.pack) as reload_visitor:
            for file in module_path.rglob("*.py"):
                if file == module_path / "__init__.py":
                    continue
                reload_visitor.add_and_visit(file)
        saya.reload_channel(channel)
