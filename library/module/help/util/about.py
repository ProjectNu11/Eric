from creart import it
from kayaku import create

from library import __version__
from library.model.config import EricConfig
from library.ui import Page
from library.ui.element import Button, Title
from library.util.module import Modules

_PROJECT_URL = "ProjectNu11/Eric"


def about_page() -> Page:
    eric_config: EricConfig = create(EricConfig)
    modules = list(it(Modules).__all__.values())
    page = Page(title=f"{eric_config.name} 关于")
    page.add(
        Title(eric_config.name, eric_config.description),
        Button(f"版本 {__version__}", width=400),
        Button(f"项目 {_PROJECT_URL}", width=400),
        Button(f"共 {len(modules)} 个模块", width=400),
    )
    return page
