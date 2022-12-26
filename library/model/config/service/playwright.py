from typing import Literal

from kayaku import config


@config("library.service.playwright")
class PlaywrightConfig:
    """Playwright 配置"""

    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    """ Playwright 的浏览器类型 """

    auto_download_browser: bool = True
    """ 是否自动下载浏览器 """
