import kayaku
from creart import it
from launart import Launart, Launchable
from loguru import logger

from library.model.config.group_config import GroupConfig
from library.util.group_config import module_save_all
from library.util.orm import db_init


class EricCoreData(Launchable):
    id = "eric.core.data"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, _mgr: Launart):
        async with self.stage("preparing"):
            await db_init()
            logger.success("[EricService] 数据库初始化完成")
            kayaku.bootstrap()
            kayaku.save_all()
            it(GroupConfig).save()
            logger.success("[EricService] 已保存配置文件")

        async with self.stage("cleanup"):
            kayaku.save_all()
            it(GroupConfig).save()
            module_save_all()
            logger.success("[EricService] 已保存配置文件")
