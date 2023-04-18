from creart import it
from graia.ariadne import Ariadne
from graiax.playwright import PlaywrightBrowser
from kayaku import create
from loguru import logger
from lxml.html import builder, tostring
from lxml.html.builder import CLASS
from playwright.async_api import Page as PWPage
from typing_extensions import Literal, Self

from library.model import EricConfig
from library.model.config import FastAPIConfig
from library.ui.color import Color, ColorSchema, is_dark
from library.ui.color.palette import ColorPalette
from library.ui.element._cfg import PageConfig
from library.ui.element._typ import OutputElement
from library.ui.element.base import Element
from library.ui.element.blank import Blank
from library.ui.element.footer import Footer
from library.ui.element.image import ImageBox
from library.util.playwright import route_fulfill

BASE_LINK = create(FastAPIConfig).link
LIB_ASSETS_BASE = f"{BASE_LINK}/assets/library"
LIB_FONT_BASE = f"{LIB_ASSETS_BASE}/fonts"
HARMONY_FONT_URL = f"{LIB_FONT_BASE}/HarmonyOSHans.ttf"
MODULE_ASSETS_BASE = f"{BASE_LINK}/assets/([a-zA-Z0-9_.]+)"


class Page(Element):
    """仿 OneUI 的页面布局"""

    _page_config: PageConfig
    _schema: ColorSchema | Literal["auto"] | None
    _cached_schema: ColorSchema | None

    elements: list[Element]
    """ 页面元素 """

    # <editor-fold desc="Backward compatibility">
    max_width: int = property(
        lambda self: self._page_config.max_width,
        lambda self, value: setattr(self._page_config, "max_width", value),
    )
    dark: bool = property(
        lambda self: self._page_config.dark,
        lambda self, value: setattr(self._page_config, "dark", value),
    )
    border_radius: int = property(
        lambda self: self._page_config.border_radius,
        lambda self, value: setattr(self._page_config, "border_radius", value),
    )
    title: str = property(
        lambda self: self._page_config.title,
        lambda self, value: setattr(self._page_config, "title", value),
    )
    fetch_on_render: bool = property(
        lambda self: self._page_config.fetch_on_render,
        lambda self, value: setattr(self._page_config, "fetch_on_render", value),
    )
    local: bool = property(
        lambda self: self._page_config.local,
        lambda self, value: setattr(self._page_config, "local", value),
    )
    additional_css: str = property(
        lambda self: self._page_config.additional_css,
        lambda self, value: setattr(self._page_config, "additional_css", value),
    )
    auto_footer: bool = property(
        lambda self: self._page_config.auto_footer,
        lambda self, value: setattr(self._page_config, "auto_footer", value),
    )
    # </editor-fold>

    @property
    def _css(self):
        return f"""
.full-padding {{ padding: 40px; }}
.lr-padding {{ padding: 0 40px 0 40px; }}
.tb-padding {{ padding: 40px 0 40px 0; }}
.auto-width {{ width: 100%; max-width: {self.max_width - self.border_radius * 2}px; }}
.round-corner {{ border-radius: {self.border_radius}px; }}
@font-face {{ font-family: homo; src: url('{HARMONY_FONT_URL}') format('truetype'); }}
body {{ font-family: homo, serif; }}
a {{ color: {self.schema.HYPERLINK.rgb(self.dark)}; text-decoration: underline; }}
a:hover {{ opacity: 0.8; }}
"""

    @property
    def css(self) -> str:
        return (
            "\n".join(
                (self._css,)
                + ((self.additional_css,) if self.additional_css else ())
                + (self.schema.gen_style(not self.dark),)
            )
            + "\n"
        )

    def __init__(
        self,
        *elements: Element | list[Element] | tuple[Element],
        schema: ColorSchema | Literal["auto"] | None = "auto",
        dark: bool = None,
        max_width: int = 1000,
        border_radius: int = 50,
        title: str = "Page",
        fetch_on_render: bool = True,
        local: bool = False,
        css: str = "",
        auto_footer: bool = True,
    ):
        self._page_config = PageConfig(
            max_width=max_width,
            dark=is_dark() if dark is None else dark,
            border_radius=border_radius,
            title=title,
            fetch_on_render=fetch_on_render,
            local=local,
            additional_css=css,
            auto_footer=auto_footer,
        )
        self._schema = it(Color).current() if schema is None else schema
        self._cached_schema = None
        self.elements = []
        self.add(*elements)

    async def fetch_all(self) -> Self:
        for element in self.elements:
            if isinstance(element, ImageBox):
                await element.fetch()
        return self

    def _auto_schema(self) -> ColorSchema:
        if not (
            images := [
                element for element in self.elements if isinstance(element, ImageBox)
            ]
        ):
            return it(Color).current()
        image: bytes | None = None
        for img in images:
            try:
                image = img.to_bytes()
            except ValueError:
                continue
            else:
                break
        try:
            return ColorPalette.generate_schema(image) if image else it(Color).current()
        except ValueError:
            logger.warning(
                f"[Page:{self.title}] Failed to generate color schema, "
                f"fallback to current"
            )
            return it(Color).current()

    @property
    def schema(self):
        """页面配色方案"""
        if self._cached_schema is not None:
            return self._cached_schema
        if self._schema is None:
            self._cached_schema = it(Color).current()
        elif self._schema == "auto":
            self._cached_schema = self._auto_schema()
        else:
            self._cached_schema = self._schema
        return self._cached_schema

    @schema.setter
    def schema(self, schema: ColorSchema | Literal["auto"] | None = None):
        self._schema = schema
        self._cached_schema = None

    def set_schema(self, schema: ColorSchema | Literal["auto"] | None = None) -> Self:
        self.schema = schema or it(Color).current()
        return self

    @property
    def required_elements(self) -> set[Element]:
        elements = set()
        for element in self.elements:
            elements |= element.require
        return elements

    def add(self, *elements: Element | list[Element] | tuple[Element]) -> Self:
        for element in elements:
            self.elements.append(element)
            self.elements.append(Blank(self.border_radius))
        return self

    def head(self):
        return builder.HEAD(
            builder.TITLE(self.title),
            builder.META(charset="utf-8"),
            builder.STYLE(self.css),
        )

    def body(self, schema: ColorSchema, dark: bool, page_cfg: PageConfig):
        elements = list(self.required_elements) + self.elements
        if self.auto_footer and not isinstance(elements[-2], Footer):
            elements.extend(
                (
                    Footer("Generated by", create(EricConfig).name),
                    Blank(self.border_radius),
                )
            )
        return builder.BODY(
            *(
                element.to_e(schema=schema, dark=dark, page_cfg=page_cfg)
                for element in elements
            ),
            CLASS("color-background-bg auto-width"),
            style="margin: 0 auto",
        )

    def to_e(
        self, *args, schema: ColorSchema, dark: bool, page_cfg: PageConfig, **kwargs
    ) -> OutputElement:
        return builder.HTML(
            self.head(),
            self.body(schema, dark, page_cfg),
        )

    def to_html(
        self,
        *_args,
        schema: ColorSchema = None,
        dark: bool = None,
        page_cfg: PageConfig = None,
        **_kwargs,
    ) -> str:
        """
        将页面转换为 HTML 字符串

        Args:
            schema: 配色方案
            dark: 是否为暗色模式
            page_cfg: 页面配置

        Returns:
            HTML 字符串
        """
        return tostring(
            self.to_e(
                schema=self.schema if schema is None else schema,
                dark=self.dark if dark is None else dark,
                page_cfg=self._page_config if page_cfg is None else page_cfg,
            ),
            encoding="unicode",
            pretty_print=True,
        )

    async def render(
        self,
        width: int = 720,
        height: int = 10,
        device_scale_factor: float = 1.0,
        local: bool = True,
        timeout: float | None = None,
        wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"]
        | None = None,
    ) -> bytes:
        if self.fetch_on_render:
            await self.fetch_all()
        browser = Ariadne.launch_manager.get_interface(PlaywrightBrowser)
        async with browser.page(
            viewport={"width": width, "height": height},
            device_scale_factor=device_scale_factor,
        ) as page:
            page: PWPage

            if local or self.local:
                logger.info(f"[Page:{self.title}] Fulfilling route...")
                await route_fulfill(page)

            logger.info(f"[Page:{self.title}] Setting content...")
            await page.set_content(
                self.to_html(), timeout=timeout, wait_until=wait_until
            )

            logger.info(f"[Page:{self.title}] Getting screenshot...")
            img = await page.screenshot(
                type="jpeg", quality=80, full_page=True, scale="device"
            )

            logger.success(f"[Page:{self.title}] Done.")
            return img
