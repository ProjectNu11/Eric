from datetime import datetime

from launart import Launart, Launchable
from loguru import logger

from library import __launch_time__
from library.util.misc import seconds_to_string


class EricCoreMisc(Launchable):
    id = "eric.core.misc"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, _mgr: Launart):
        async with self.stage("blocking"):
            launch_time = seconds_to_string(
                (datetime.now() - __launch_time__).total_seconds()
            )
            logger.success(f"[EricCore] 启动总耗时 {launch_time}")
