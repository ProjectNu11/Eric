import kayaku
from launart import Launart, Launchable


class EricService(Launchable):
    id = "eric.core/service"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking", "cleanup"}

    async def launch(self, _mgr: Launart):

        async with self.stage("blocking"):
            # TODO Initialize Eric
            pass

        async with self.stage("cleanup"):
            kayaku.save_all()
