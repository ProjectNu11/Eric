import kayaku
from creart import it
from launart import Launart, Launchable
from loguru import logger

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

        async with self.stage("preparing"):
            logger.info("[EricService] 初始化数据库")
            await db_init()

        async with self.stage("blocking"):
            # TODO Initialize Eric
            await it(PublicGroup).data_init()

        async with self.stage("cleanup"):
            logger.info("[EricService] 保存配置文件")
            kayaku.save_all()
