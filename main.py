import os
import sys
from pathlib import Path

import kayaku
from graia.ariadne import Ariadne

if __name__ == "__main__":
    os.environ["PYTHONUTF8"] = "1"

    if Path.cwd() != Path(__file__).parent:
        os.chdir(Path(__file__).parent)

    kayaku.initialize({"{**}": "./config/{**}"})
    with_console = "--console" in sys.argv

    from library.service.stage import initialize

    # from library.ui.element.box.image import ImageBox
    # from library.ui.element.banner import Banner
    # from library.ui.element.box.generic import GenericBoxItem, GenericBox
    # from library.ui import Page
    #
    # page = Page(
    #     Banner("Dog X Bloods"),
    #     GenericBox(
    #         GenericBoxItem("注意", "本站点仅提供分流下载，官网请至 https://dogbloods.com/"),
    #     ),
    #     ImageBox.from_url(
    #         "https://static.wixstatic.com/media/aed6de_c14eab80467546ecac75fcdc7ebff8fa~mv2.png"
    #     ),
    #     GenericBox(
    #         GenericBoxItem("0.2.3", "下载链接 [官方] "),
    #         GenericBoxItem("0.2.2", "下载链接 [官方]"),
    #         GenericBoxItem("0.2.1", "下载链接 [官方] [重打包]"),
    #         GenericBoxItem("0.2.0", "下载链接 [官方]"),
    #         GenericBoxItem("0.1.5", "下载链接 [重打包]"),
    #         GenericBoxItem("0.1.0", "下载链接 [官方]"),
    #     ),
    #     GenericBox(
    #         GenericBoxItem(
    #             "注释",
    #             "站点服务由 nullqwertyuiop 提供，内容缓存服务由 Cloudflare 提供，\n\n下载速度受限于 Cloudflare 的带宽。请勿使用迅雷等下载工具下载。",
    #         ),
    #     ),
    # )
    #
    # with open("index.html", "w", encoding="utf-8") as f:
    #     f.write(page.to_html())
    # print(Page(GenericBoxItem("Hello"), schema=ColorSchema()).to_html())
    # print(Page(GenericBoxItem(None, "Hello"), schema=ColorSchema()).to_html())
    # print(Page(GenericBoxItem(None), schema=ColorSchema()).to_html())
    # exit()

    initialize(with_console=with_console)
    Ariadne.launch_blocking()
