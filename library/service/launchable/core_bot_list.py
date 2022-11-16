from creart import it
from launart import Launchable, Launart

from library.model.bot_list import BotList


class EricCoreBotList(Launchable):
    id = "eric.core.bot_list"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, _mgr: Launart):
        async with self.stage("blocking"):
            bot_list: BotList = it(BotList)
            await bot_list.fetch_all()
            bot_list.save()
