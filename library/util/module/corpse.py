from pathlib import Path

from loguru import logger

from library.model import Module
from library.util.file import remove_recursive


def is_corpse(module: Module) -> bool:
    """Return True if the module is a corpse, False otherwise."""
    path = Path.cwd() / Path(*module.pack.split("."))
    ignored = ["__pycache__", "metadata.json"]
    ignored_ext = [".pyc", ".pyo"]
    for file in path.iterdir():
        if file.name in ignored:
            continue
        if file.suffix in ignored_ext:
            continue
        return False
    return True


def remove_if_corpse(module: Module) -> bool:
    """Remove the module if it is a corpse, return True if removed, False otherwise."""
    if is_corpse(module):
        logger.warning(f"[Module] 模块 {module.name} 残留文件已被移除")
        path = Path.cwd() / Path(*module.pack.split("."))
        remove_recursive(path)
        return True
    return False
