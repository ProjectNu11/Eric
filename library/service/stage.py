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
from graiax.fastapi import FastAPIService
from graiax.playwright import PlaywrightService
from loguru import logger
from playwright.async_api import ProxySettings

from library.config.initialize import initialize_config
from library.model.config.eric import EricConfig
from library.service.kayaku_launart import EricConfigService
from library.util.log import setup_logger


def initialize():
    setup_logger()
    initialize_config()

    cfg = kayaku_create(EricConfig, flush=True)
    ariadne: list[Ariadne] = [
        Ariadne(
            config(
                account,
                str(cfg.verify_key),
                HttpClientConfig(host=cfg.host),
                WebsocketClientConfig(host=cfg.host),
            )
        )
        for account in cfg.accounts
    ]
    if not ariadne:
        logger.error("无可用账号，请检查配置文件")
        sys.exit(1)

    if cfg.default_account:
        Ariadne.config(default_account=cfg.default_account)
    else:
        Ariadne.config(default_account=cfg.accounts.copy().pop())

    Ariadne.launch_manager.add_service(
        PlaywrightService(
            "chromium",
            proxy=ProxySettings(
                {"server": cfg.proxy if cfg.proxy != "proxy" else None}
            ),
        )
    )
    Ariadne.launch_manager.add_service(FastAPIService(create(FastAPI)))
    ariadne[-1].launch_manager.add_service(
        UvicornService(host=cfg.service.fastapi.host, port=cfg.service.fastapi.port)
    )
    Ariadne.launch_manager.add_service(EricConfigService())

    create(GraiaScheduler)
    saya = create(Saya)
    saya.install_behaviours(
        create(BroadcastBehaviour),
        create(GraiaSchedulerBehaviour),
    )
