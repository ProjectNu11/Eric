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
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya import GraiaSchedulerBehaviour
from graiax.fastapi import FastAPIBehaviour, FastAPIService
from graiax.playwright import PlaywrightService
from kayaku import create
from loguru import logger
from playwright.async_api import ProxySettings

from library.model.config import EricConfig, FastAPIConfig, PlaywrightConfig
from library.service.launchable import (
    EricCoreBotList,
    EricCoreData,
    EricCoreUpdater,
    EricUtilSession,
    FrequencyLimitService,
    LaunchTimeService,
)
from library.util.config import initialize_config
from library.util.log import setup_logger
from library.util.module.launch import launch_require


def prepare():
    setup_logger()
    initialize_config()


def init_ariadne():
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
        Ariadne.config(default_account=eric_config.accounts[0])


def init_service():
    eric_cfg: EricConfig = create(EricConfig)
    pw_cfg: PlaywrightConfig = create(PlaywrightConfig)
    fastapi_cfg: FastAPIConfig = create(FastAPIConfig)
    Ariadne.launch_manager.add_service(
        PlaywrightService(
            pw_cfg.browser,
            auto_download_browser=pw_cfg.auto_download_browser,
            proxy=ProxySettings({"server": eric_cfg.proxy}) if eric_cfg.proxy else None,
        )
    )
    Ariadne.launch_manager.add_service(FastAPIService(it(FastAPI)))
    Ariadne.launch_manager.add_service(
        UvicornService(host=fastapi_cfg.host, port=fastapi_cfg.port)
    )
    Ariadne.launch_manager.add_service(EricCoreUpdater())
    Ariadne.launch_manager.add_service(EricCoreData())
    Ariadne.launch_manager.add_service(EricCoreBotList())
    Ariadne.launch_manager.add_service(EricUtilSession())
    Ariadne.launch_manager.add_service(FrequencyLimitService())
    Ariadne.launch_manager.add_service(LaunchTimeService())


def init_saya():
    it(GraiaScheduler)
    saya = it(Saya)
    saya.install_behaviours(
        it(BroadcastBehaviour),
        it(GraiaSchedulerBehaviour),
        FastAPIBehaviour(it(FastAPI)),
    )


def initialize():
    prepare()
    init_ariadne()
    init_service()
    init_saya()
    launch_require()
