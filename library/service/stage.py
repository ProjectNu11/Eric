import sys

from creart import it
from fastapi import FastAPI
from graia.amnesia.builtins.uvicorn import UvicornService
from graia.ariadne import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya import GraiaSchedulerBehaviour
from graiax.fastapi import FastAPIBehaviour, FastAPIService
from graiax.playwright import PlaywrightService
from kayaku import create
from loguru import logger
from playwright.async_api import ProxySettings

from library.config.initialize import initialize_config
from library.model.config import EricConfig, FastAPIConfig, PlaywrightConfig
from library.service.launchable import (
    EricCoreBotList,
    EricCoreData,
    EricCoreMisc,
    EricCoreUpdater,
    EricUtilSession,
    FrequencyLimitService,
)
from library.util.log import setup_logger
from library.util.module.launch import launch_require


def initialize(*, with_console: bool):
    setup_logger()
    initialize_config()

    eric_config: EricConfig = create(EricConfig)
    ariadne: list[Ariadne] = [
        Ariadne(
            config(
                int(account),
                str(eric_config.verify_key),
                HttpClientConfig(host=eric_config.host),
                WebsocketClientConfig(host=eric_config.host),
            )
        )
        for account in eric_config.accounts
    ]
    if not ariadne:
        logger.error("无可用账号，请检查配置文件")
        sys.exit(1)

    if eric_config.default_account:
        Ariadne.config(default_account=eric_config.default_account)
    else:
        Ariadne.config(default_account=eric_config.accounts.copy().pop())

    pw_cfg: PlaywrightConfig = create(PlaywrightConfig)
    Ariadne.launch_manager.add_service(
        PlaywrightService(
            pw_cfg.browser,
            auto_download_browser=pw_cfg.auto_download_browser,
            proxy=ProxySettings({"server": eric_config.proxy})
            if eric_config.proxy
            else None,
        )
    )
    Ariadne.launch_manager.add_service(FastAPIService(it(FastAPI)))

    fastapi_config: FastAPIConfig = create(FastAPIConfig)
    Ariadne.launch_manager.add_service(
        UvicornService(host=fastapi_config.host, port=fastapi_config.port)
    )

    Ariadne.launch_manager.add_service(EricCoreUpdater())
    Ariadne.launch_manager.add_service(EricCoreData())
    Ariadne.launch_manager.add_service(EricCoreMisc())
    Ariadne.launch_manager.add_service(EricCoreBotList())
    Ariadne.launch_manager.add_service(EricUtilSession())
    Ariadne.launch_manager.add_service(FrequencyLimitService())

    it(GraiaScheduler)

    saya = it(Saya)
    saya.install_behaviours(
        it(BroadcastBehaviour),
        it(GraiaSchedulerBehaviour),
        FastAPIBehaviour(it(FastAPI)),
    )
    if with_console:
        saya.install_behaviours(
            ConsoleBehaviour(
                Console(broadcast=it(Broadcast), prompt=f"{eric_config.name}> ")
            )
        )

    launch_require()
