from creart import it
from launart import Launart, Launchable

from library.util.session_container import SessionContainer


class EricUtilSession(Launchable):
    id = "eric.util.session"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, _mgr: Launart):
        async with self.stage("preparing"):
            container = it(SessionContainer)
            await container.get()
        async with self.stage("cleanup"):
            await container.close_all()
