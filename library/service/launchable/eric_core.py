import asyncio
from pathlib import Path

import kayaku
from creart import it
from kayaku import create
from launart import Launart, Launchable
from loguru import logger

from library.decorator.core import CoreInitCheck
from library.model.config.path import PathConfig
from library.model.config.service.manager import ManagerConfig
from library.model.core import EricCore
from library.service.updater import check_update, perform_update
from library.util.inject import inject, uninject
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

        # Inject CoreInitCheck to all modules, ensure that the core is initialized
        inject(CoreInitCheck())

        async with self.stage("preparing"):
            await db_init()
            logger.success("[EricService] 数据库初始化完成")

        async with self.stage("blocking"):
            await it(PublicGroup).data_init()
            logger.success("[EricService] 公共群数据初始化完成")
            it(EricCore).finish_init()
            logger.success("[EricService] Eric 核心初始化完成")

            # Uninject CoreInitCheck, for better performance
            uninject(CoreInitCheck())

            await self.check_update()

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.info("[EricService] 已保存配置文件")

    @staticmethod
    async def check_update():
        if not (update := await check_update()):
            logger.opt(colors=True).success("<green>[EricService] 当前版本已是最新</green>")
            return
        output = []
        for commit in update:
            sha = commit.get("sha", "")[:7]
            message = commit.get("commit", {}).get("message", "")
            output.append(f"<red>{sha}</red> <yellow>{message}</yellow>")
        history = "\n".join(["", *output, ""])
        logger.opt(colors=True).warning(
            f"<yellow>[EricService] 发现新版本</yellow>\n{history}"
        )
        config: ManagerConfig = create(ManagerConfig)
        if not config.auto_update:
            return
        logger.opt(colors=True).info("<cyan>[EricService] 正在自动更新</cyan>")
        await asyncio.to_thread(perform_update())
        logger.success("[EricService] 更新完成，将在重新启动后生效")
