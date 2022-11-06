from pathlib import Path

from creart import it
from kayaku import create
from loguru import logger

from library.model.config.eric import EricConfig
from library.model.config.path import PathConfig
from library.model.config.state import ModuleState
from library.util.module import list_module, Modules
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
