import kayaku
from launart import Launart, Launchable


class EricConfigService(Launchable):
    id = "eric.config/save_all"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"cleanup"}

    async def launch(self, _mgr: Launart):
        async with self.stage("cleanup"):
            kayaku.save_all()
