from pathlib import Path

import kayaku
from creart import it
from kayaku import create
from launart import Launart, Launchable
from loguru import logger

from library.model.config.path import PathConfig
from library.model.core import EricCore
from library.util.module.get_all import list_all
from library.util.module.require import require_by_metadata
from library.util.multi_account.public_group import PublicGroup
from library.util.orm import db_init


class EricService(Launchable):
    id = "eric.core/service"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, _mgr: Launart):
        _path_config: PathConfig = create(PathConfig)
        _lib_module_path = Path("library/module")
        _lib_modules = list_all(_lib_module_path)
        _user_modules = list_all(Path(_path_config.module))
        logger.success(
            f"[EricService] 已校验 {len(_lib_modules) + len(_user_modules)} 个模块"
        )
        require_by_metadata(_lib_modules)
        require_by_metadata(_user_modules)

        async with self.stage("preparing"):
            await db_init()
            logger.success("[EricService] 数据库初始化完成")

        async with self.stage("blocking"):
            await it(PublicGroup).data_init()
            logger.success("[EricService] 公共群数据初始化完成")
            it(EricCore).finish_init()
            logger.success("[EricService] Eric 核心初始化完成")

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.info("[EricService] 已保存配置文件")
