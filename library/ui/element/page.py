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

    elements: list[Element]
    """ 页面元素 """

    max_width: int
    """ 页面最大宽度 """

    dark: bool
    """ 是否为暗色模式 """

    border_radius: int
    """ 页面圆角 """

    title: str
    """ 页面标题 """

    fetch_on_render: bool
    """ 是否在渲染时获取图片 """

    local: bool
    """ 是否使用本地字体，如果为 True 则将无法在公网上正常显示 """

    additional_css: str
    """ 附加 CSS """

    auto_footer: bool
    """ 是否自动添加页脚 """

    @property
    def _css(self):
        return f"""
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

    _schema: ColorSchema | Literal["auto"] | None
    _cached_schema: ColorSchema | None

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
        if dark is None:
            dark = is_dark()
        if schema is None:
            schema = it(Color).current()
        self._schema = schema
        self._cached_schema = None
        self.dark = dark
        self.max_width = max_width
        self.border_radius = border_radius
        self.title = title
        self.fetch_on_render = fetch_on_render
        self.local = local
        self.additional_css = css
        self.auto_footer = auto_footer
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

    def body(self, schema: ColorSchema, dark: bool):
        elements = self.elements
        if self.auto_footer and not isinstance(elements[-2], Footer):
            elements.append(Footer("Generated by", create(EricConfig).name))
        return builder.BODY(
            *(element.to_e(schema=schema, dark=dark) for element in elements),
            CLASS("color-background-bg auto-width"),
            style="margin: 0 auto",
        )

    def to_e(self, *_args, schema: ColorSchema, dark: bool, **_kwargs):
        return builder.HTML(
            self.head(),
            self.body(schema, dark),
        )

    def to_html(self, *_args, **_kwargs) -> str:
        return tostring(
            self.to_e(schema=self.schema, dark=self.dark),
            encoding="unicode",
            pretty_print=True,
        )

    async def render(
        self,
        width: int = 720,
        height: int = 10,
        device_scale_factor: float = 1.0,
        local: bool = False,
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
