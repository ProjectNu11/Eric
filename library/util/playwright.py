import re
from pathlib import Path

from creart import it
from kayaku import create
from loguru import logger
from playwright.async_api import Page, Request, Route
from yarl import URL

from library.model.config import FastAPIConfig
from library.ui.util import FONT_MIME_MAP, FONT_PATH
from library.util.module import Modules

BASE_LINK = create(FastAPIConfig).link
LIB_ASSETS_BASE = f"{BASE_LINK}/assets/library"
LIB_FONT_BASE = f"{LIB_ASSETS_BASE}/fonts"
HARMONY_FONT_URL = f"{LIB_FONT_BASE}/HarmonyOSHans.ttf"
MODULE_ASSETS_BASE = f"{BASE_LINK}/assets/([a-zA-Z0-9_.]+)"


async def fulfill_font(route: Route, request: Request):
    url = URL(request.url)
    if (FONT_PATH / url.name).exists():
        logger.debug(f"Fulfilling font {url}...")
        await route.fulfill(
            path=FONT_PATH / url.name,
            content_type=FONT_MIME_MAP.get(url.suffix, None),
        )
        return
    await route.fallback()


async def fulfill_module_assets(route: Route, request: Request):
    pattern = re.compile(f"{MODULE_ASSETS_BASE}/(.*)")
    if not (group := pattern.search(request.url)):
        await route.fallback()
        return
    module, file = group.groups()
    if not it(Modules).get(module):
        await route.fallback()
        return
    path = Path(*module.split("."), "assets", file)
    if not path.is_file():
        await route.fallback()
        return
    logger.debug(f"Fulfilling module assets {request.url}...")
    await route.fulfill(path=path)


async def route_fulfill(page: Page):
    """
    实现路由拦截，用于替换字体和模块资源

    Args:
        page (Page): Playwright 页面，并非 `library.ui.Page` 实例
    """
    await page.route(re.compile(rf"^{LIB_FONT_BASE}/(.*)$"), fulfill_font)
    await page.route(re.compile(rf"^{MODULE_ASSETS_BASE}/(.*)$"), fulfill_module_assets)
