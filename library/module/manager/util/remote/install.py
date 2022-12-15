import asyncio
from contextlib import suppress
from pathlib import Path

from creart import it
from kayaku import create
from loguru import logger

from library.model.config.path import PathConfig
from library.model.config.state import ModuleState
from library.model.module import Module
from library.module.manager.model.module import RemoteModule
from library.module.manager.util.module.unload import unload
from library.util.file import remove_recursive
from library.util.module import Modules
from library.util.module.metadata import update_metadata
from library.util.module.require import require
from library.util.module.standardize import standardize_structure


def _pre_check(module: RemoteModule):
    if module.pack.startswith("library.module"):
        raise AssertionError(f"保留地址：{module.pack}")


def _prepare_module_dir(module: RemoteModule) -> tuple[Path, Path]:
    path_cfg: PathConfig = create(PathConfig)
    temp_dir: Path = Path(path_cfg.module) / f"__temp_{module.clean_name}__"
    install_dir: Path = Path(path_cfg.module) / module.clean_name
    if temp_dir.exists():
        logger.warning("临时目录已存在，正在删除")
        remove_recursive(temp_dir)
    temp_dir.mkdir(parents=True)
    logger.success(f"已建立临时目录 {temp_dir}")
    return temp_dir, install_dir


async def _download_files(module: RemoteModule, temp_dir: Path, max_retries: int):
    to_download = module.files.copy()
    retries = 0
    while to_download and max_retries - retries > 0:
        if not (
            to_download := await module.repo.file_to_disk(
                temp_dir, module.clean_name, *to_download
            )
        ):
            return
        output = "\n".join(to_download)
        logger.warning(
            f"{len(to_download)} 个文件下载失败 ({retries}/{max_retries})\n{output}"
        )
        retries += 1
    remove_recursive(temp_dir)
    logger.error(f"下载失败: {module.name} ({module.version})，已删除临时目录")
    raise RuntimeError(f"{len(to_download)} 个文件下载失败，已达到最大重试次数")


def _install(temp_dir: Path, install_dir: Path):
    if install_dir.exists():
        logger.warning("安装目录已存在，正在删除")
        remove_recursive(install_dir)
    temp_dir.rename(install_dir)


async def _post_install(install_dir: Path):
    install_dir = standardize_structure(install_dir)
    metadata = update_metadata(install_dir)
    state: ModuleState = create(ModuleState)
    try:
        if not isinstance(_state := state.loaded.get(metadata.pack, None), bool):
            state.load(metadata.pack)
            _state = True
        module = Module(**{"loaded": _state, **metadata.dict()})
        with suppress(Exception):
            # Unload the module if it is already loaded
            # Suppress any exception because the module may not be loaded
            unload(module, unload_state=False)
        it(Modules).add(module)
        await asyncio.to_thread(require, module, debug=False, suppress=False)
    except Exception as e:
        logger.error(f"安装时出现错误：\n{e.with_traceback(e.__traceback__)}")
        state.unload(metadata.pack)
        raise


async def install(module: RemoteModule, *, max_retries: int = 5):
    _pre_check(module)
    temp_dir, install_dir = _prepare_module_dir(module)
    await _download_files(module, temp_dir, max_retries)
    _install(temp_dir, install_dir)
    await _post_install(install_dir)
