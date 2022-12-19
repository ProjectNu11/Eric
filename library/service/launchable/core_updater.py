import asyncio

from kayaku import create
from launart import Launart, Launchable
from loguru import logger

from library.model.config.service.manager import ManagerConfig
from library.service.updater import check_update, perform_update


class EricCoreUpdater(Launchable):
    id = "eric.core.updater"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"blocking", "cleanup"}

    async def launch(self, _mgr: Launart):
        async with self.stage("blocking"):
            await self.check_update()
        async with self.stage("cleanup"):
            await self.check_update()

    @staticmethod
    async def check_update():
        if not (update := await check_update()):
            logger.opt(colors=True).success("<green>[EricService] 当前版本已是最新</green>")
            return
        output = []
        for commit in update:
            sha = commit.get("sha", "")[:7]
            message = commit.get("commit", {}).get("message", "")
            message = message.replace("<", r"\<").splitlines()[0]
            output.append(f"<red>{sha}</red> <yellow>{message}</yellow>")
        history = "\n".join(["", *output, ""])
        logger.opt(colors=True).warning(
            f"<yellow>[EricService] 发现新版本</yellow>\n{history}"
        )
        config: ManagerConfig = create(ManagerConfig)
        if not config.self_auto_update:
            return
        logger.opt(colors=True).info("<cyan>[EricService] 正在自动更新</cyan>")
        await asyncio.to_thread(perform_update)
        logger.success("[EricService] 更新完成，将在重新启动后生效")
