from pathlib import Path

from creart import it
from kayaku import create
from loguru import logger

from library.model.config import EricConfig, ModuleState, PathConfig
from library.util.module import Modules
from library.util.module.get import list_module
from library.util.module.require import require


def launch_require():
    config: EricConfig = create(EricConfig)

    create(ModuleState).initialize()
    _lib_modules = list_module(Path("library/module"))
    _user_modules = list_module(Path(create(PathConfig).module))
    modules = it(Modules)
    modules.add(*_lib_modules, *_user_modules)
    logger.success(f"[EricService] 已校验 {len(_lib_modules) + len(_user_modules)} 个模块")
    require(*modules.ordered, debug=config.debug)
