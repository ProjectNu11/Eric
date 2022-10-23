from pathlib import Path
from typing import Iterable

from creart import it
from graia.saya import Saya
from loguru import logger

from library.model.module import ModuleMetadata, Module
from library.util.misc import inflate
from library.util.module.dependency import install_dependency
from library.util.module.get import list_module


def _require_install_deps(saya: Saya, module: ModuleMetadata):
    try:
        saya.require(module.pack)
    except ModuleNotFoundError:
        logger.warning(f"缺少模块 {module.pack} 的依赖，正在安装...")
        install_dependency(module)
        try:
            saya.require(module.pack)
        except ModuleNotFoundError as e:
            logger.error(e.with_traceback(e.__traceback__))
            logger.error(f"模块 {module.pack} 的依赖安装失败，请检查依赖列表")


def require_by_dir(base_dir: Path):
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in list_module(base_dir):
            _require_install_deps(saya, module)


def require_by_metadata(*metadata: ModuleMetadata | Iterable[ModuleMetadata]):
    modules: list[ModuleMetadata] = inflate(metadata)
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in modules:
            _require_install_deps(saya, module)


def require(*modules: Module | Iterable[Module]):
    require_by_metadata([module for module in inflate(modules) if module.loaded])
