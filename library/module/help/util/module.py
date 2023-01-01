from contextlib import suppress
from pathlib import Path

from creart import it
from graiax.text2img.playwright import convert_md
from graiax.text2img.playwright.renderer import BuiltinCSS
from kayaku import create

from library.model.config import EricConfig, FunctionConfig
from library.model.module import Module
from library.module.help.vars import (
    CATEGORY_SEARCH_PAGE,
    MODULE_HELP_PAGE,
    MODULE_MARKDOWN_PAGE,
)
from library.ui import Page
from library.ui.element import Button, GenericBox, GenericBoxItem, Title
from library.util.misc import inflate
from library.util.module import Modules

_MARKDOWN_STYLE: str = "\n".join(
    _css.value  # type: ignore
    for _css in (
        BuiltinCSS.reset,
        BuiltinCSS.github,
        BuiltinCSS.one_dark,
        BuiltinCSS.container,
    )
)


def portal_page() -> Page:
    eric_config: EricConfig = create(EricConfig)
    modules = list(it(Modules).__all__.values())
    page = Page(title=f"{eric_config.name} 帮助中心")
    page.add(
        Title(f"{eric_config.name} 帮助中心", f"共 {len(modules)} 个模块"),
    )
    lib_modules = {module for module in modules if module.pack.startswith("library.")}
    user_modules = set(modules) - lib_modules
    for module in sorted(user_modules, key=lambda _mod: _mod.pack) + sorted(
        lib_modules, key=lambda _mod: _mod.pack
    ):
        if module.advanced.hidden:
            continue
        page.add(
            Button(
                module.name,
                MODULE_HELP_PAGE.format(pack=module.pack),
                width=400,
            )
        )
    return page


def get_module_page(module: Module) -> Page:
    module_path: Path = Path(*module.pack.split("."))
    modules = it(Modules)

    page = Page(title=f"{module.name} 详情")
    page.add(
        Title(f"{module.name} 详情", f"版本 {module.version}"),
    )

    if (module_path / "README.md").is_file():
        page.add(
            Button(
                "必读",
                MODULE_MARKDOWN_PAGE.format(
                    pack=module.pack,
                    file="README.md",
                ),
                width=200,
            )
        )
    if (module_path / "USAGE.md").is_file():
        page.add(
            Button(
                "使用方法",
                MODULE_MARKDOWN_PAGE.format(
                    pack=module.pack,
                    file="USAGE.md",
                ),
                width=200,
            )
        )

    page.add(
        GenericBox(
            GenericBoxItem("描述", module.description),
            GenericBoxItem("作者", "\n".join(module.authors)),
            GenericBoxItem("包名", module.pack),
        )
    )
    if categories := module.category:
        page.add(
            GenericBox(
                GenericBoxItem("分类"),
            )
        )
        for category in categories:
            page.add(
                Button(
                    (_cate_part := category.split(":"))[-1],
                    CATEGORY_SEARCH_PAGE.format(
                        category=_cate_part[0],
                    ),
                    width=200,
                )
            )
    if required := module.required:
        page.add(GenericBox(GenericBoxItem("依赖")))
        for req in required:
            req = modules.get(req)
            page.add(
                Button(
                    req.name,
                    MODULE_HELP_PAGE.format(pack=req.pack),
                    width=200,
                )
            )
    return page


def get_module_markdown(module: Module, file: str) -> str:
    eric_config: EricConfig = create(EricConfig)
    function_config: FunctionConfig = create(FunctionConfig)
    md = convert_md(Path(*module.pack.split("."), file).read_text())
    with suppress(Exception):
        md = md.format(name=eric_config.name, prefix=function_config.prefix[0])
    return (
        f'<html><meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f"<head><style>{_MARKDOWN_STYLE}</style></head><body>{md}</body></html>"
    )


def _search(keyword: str, name: str, *criterion) -> Page:
    if not (modules := it(Modules).search(*criterion)):
        page = Page(title="未找到相关模块")
        page.add(
            Title("未找到相关模块"),
            GenericBox(
                GenericBoxItem(name, keyword),
            ),
        )
        return page
    page = Page(title=f"{name}搜索 {keyword}")
    page.add(Title(f"{name}搜索 {keyword}", f"共 {len(modules)} 个结果"))
    for module in sorted(modules, key=lambda _mod: _mod.pack):
        page.add(
            Button(
                module.name,
                MODULE_HELP_PAGE.format(pack=module.pack),
                width=400,
            )
        )
    return page


def search_module(keyword: str) -> Page:
    return _search(
        keyword,
        "关键词",
        lambda _mod: keyword in _mod.name
        or keyword in _mod.description
        or keyword in "".join(_mod.authors)
        or keyword in "".join(_mod.category).replace(":", ""),
    )


def search_category(category: str) -> Page:
    return _search(
        category,
        "分类",
        lambda _mod: category in inflate(_.split(":") for _ in _mod.category),
    )
