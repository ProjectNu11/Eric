from datetime import datetime
from pathlib import Path
from typing import Iterable

from creart import it
from graia.saya import Saya
from loguru import logger

from library.model import RequireStatus
from library.model.exception import SkipRequiring
from library.model.module import Module, ModuleMetadata
from library.service.launchable.util_launch_time import add_launch_time
from library.util.misc import inflate
from library.util.module.dependency import install_deps
from library.util.module.get import list_module


def _require_install_deps(
    saya: Saya, module: ModuleMetadata, debug: bool, suppress: bool
):
    start = datetime.now()
    try:
        saya.require(module.pack)
        add_launch_time(
            module, (datetime.now() - start).total_seconds(), RequireStatus.SUCCESS
        )
    except SkipRequiring as e:
        logger.warning(f"skipping {module.pack}: {e}")
        add_launch_time(
            module, (datetime.now() - start).total_seconds(), RequireStatus.SKIPPED
        )
    except ModuleNotFoundError:
        logger.warning(f"缺少模块 {module.pack} 的依赖，正在安装...")
        install_deps(module)
        try:
            saya.require(module.pack)
            add_launch_time(
                module, (datetime.now() - start).total_seconds(), RequireStatus.SUCCESS
            )
        except ModuleNotFoundError as e:
            logger.error(e.with_traceback(e.__traceback__))
            logger.error(f"模块 {module.pack} 的依赖安装失败，请检查依赖列表")
            add_launch_time(
                module,
                (datetime.now() - start).total_seconds(),
                RequireStatus.MISSING_DEPENDENCY,
            )
    except Exception as e:
        add_launch_time(
            module, (datetime.now() - start).total_seconds(), RequireStatus.ERROR
        )
        if debug:
            logger.exception(e.with_traceback(e.__traceback__))
        elif suppress:
            logger.error(e)
        else:
            raise


def require_by_dir(base_dir: Path, *, debug: bool = False, suppress: bool = True):
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in list_module(base_dir):
            _require_install_deps(saya, module, debug, suppress)


def require_by_metadata(
    *metadata: ModuleMetadata | Iterable[ModuleMetadata],
    debug: bool = False,
    suppress: bool = True,
):
    modules: list[ModuleMetadata] = inflate(metadata)
    saya: Saya = it(Saya)
    with saya.module_context():
        for module in modules:
            _require_install_deps(saya, module, debug, suppress)


def require(
    *modules: Module | Iterable[Module], debug: bool = False, suppress: bool = True
):
    require_by_metadata(
        [module for module in inflate(modules) if module.loaded],
        debug=debug,
        suppress=suppress,
    )
