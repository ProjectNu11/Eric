import sys

from creart import create
from kayaku import create as kayaku_create
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
from graiax.fastapi import FastAPIService, FastAPIBehaviour
from graiax.playwright import PlaywrightService
from loguru import logger
from playwright.async_api import ProxySettings

from library.config.initialize import initialize_config
from library.model.config.eric import EricConfig
from library.model.config.service.fastapi import FastAPIConfig
from library.service.launchable.eric_core import EricService
from library.util.log import setup_logger


def initialize():
    setup_logger()
    initialize_config()

    eric_config: EricConfig = kayaku_create(EricConfig)
    ariadne: list[Ariadne] = [
        Ariadne(
            config(
                account,
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

    Ariadne.launch_manager.add_service(
        PlaywrightService(
            "chromium",
            proxy=ProxySettings({"server": eric_config.proxy})
            if eric_config.proxy
            else None,
        )
    )
    Ariadne.launch_manager.add_service(FastAPIService(create(FastAPI)))

    fastapi_config: FastAPIConfig = kayaku_create(FastAPIConfig)
    Ariadne.launch_manager.add_service(
        UvicornService(host=fastapi_config.host, port=fastapi_config.port)
    )
    Ariadne.launch_manager.add_service(EricService())

    create(GraiaScheduler)
    saya = create(Saya)
    saya.install_behaviours(
        create(BroadcastBehaviour),
        create(GraiaSchedulerBehaviour),
        FastAPIBehaviour(create(FastAPI)),
    )
