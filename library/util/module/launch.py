from pathlib import Path

from creart import it
from kayaku import create
from loguru import logger

from library.model.config import EricConfig, ModuleState, PathConfig
from library.util.module import Modules
from library.util.module.corpse import remove_if_corpse
from library.util.module.get import list_module
from library.util.module.require import require


def launch_require():
    config: EricConfig = create(EricConfig)

    create(ModuleState).initialize()
    lib_modules = list_module(Path("library/module"))
    user_modules = list_module(Path(create(PathConfig).module))

    cleaned = [
        module
        for module in [*lib_modules, *user_modules]
        if not remove_if_corpse(module)
    ]
    modules = it(Modules)
    modules.add(*cleaned)
    logger.success(f"[EricService] 已校验 {len(cleaned)} 个模块")
    require(*modules.ordered, debug=config.debug)
