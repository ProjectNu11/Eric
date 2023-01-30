from creart import it
from graia.ariadne import Ariadne
from graiax.playwright import PlaywrightBrowser
from kayaku import create
from loguru import logger
from lxml.html import builder, tostring
from lxml.html.builder import CLASS
from typing_extensions import Self

from library.model.config import FastAPIConfig
from library.ui.color import Color, ColorSchema, is_dark
from library.ui.element.base import Element, Style
from library.ui.element.blank import Blank
from library.util.misc import inflate

HARMONY_FONT_URL = (
    f"{create(FastAPIConfig).link}/assets/library/fonts/HarmonyOSHans.ttf"
)


class Page(Element):

    elements: list[Element]
    max_width: int
    schema: ColorSchema
    dark: bool
    styles: set[Style[str, str]]
    border_radius: int
    title: str

    def __init__(
        self,
        *elements: Element | list[Element] | tuple[Element],
        schema: ColorSchema = None,
        dark: bool = None,
        max_width: int = 1000,
        border_radius: int = 50,
        title: str = "Page",
    ):
        if dark is None:
            dark = is_dark()
        if schema is None:
            schema = it(Color).current()
        self.schema = schema
        self.dark = dark
        self.max_width = max_width
        self.border_radius = border_radius
        self.title = title
        self.elements = []
        self.add(*elements)

    def __hash__(self):
        return hash(
            f"_Page:{':' .join(str(hash(element)) for element in self.elements)}"
        )

    def set_schema(self, schema: ColorSchema | None = None) -> Self:
        self.schema = schema or it(Color).current()
        return self

    def add(self, *elements: Element | list[Element] | tuple[Element]) -> Self:
        for element in elements:
            self.elements.append(element)
            self.elements.append(Blank(self.border_radius))
        return self

    def style(self, *_) -> set[Style[str, str]]:
        return {
            Style(
                {
                    "color-background": f"background-color: {self.schema.BACKGROUND.rgb(self.dark)}",
                    "auto-width": "width: 100%; "
                    f"max-width: {self.max_width - self.border_radius * 2}px",
                    "round-corner": f"border-radius: {self.border_radius}px",
                }
            ),
        }

    def styles(self, schema: ColorSchema, dark: bool):
        return builder.E.style(
            " ".join(
                f".{key} {{ {value.get(key, '')} }}"
                for value in self.style().union(
                    inflate(element.style(schema, dark) for element in self.elements)  # type: ignore
                )
                for key in value
            )
            # Add font
            + " @font-face {font-family: homo; "
            f"src: url('{HARMONY_FONT_URL}') format('truetype')}}"  # noqa
            # Apply font to body
            + " body {font-family: 'homo'}"
            # Apply color to a
            + f" a {{ color: {self.schema.HYPERLINK.rgb(dark)}; "
            "text-decoration: none }"
        )

    def head(self, schema: ColorSchema, dark: bool):
        return builder.HEAD(
            builder.TITLE(self.title),
            builder.META(charset="utf-8"),
            self.styles(schema, dark),
        )

    def body(self, schema: ColorSchema, dark: bool):
        return builder.BODY(
            *(element.to_e(schema=schema, dark=dark) for element in self.elements),
            CLASS("color-background auto-width"),
            style="margin: 0 auto",
        )

    def to_e(self, *_args, schema: ColorSchema, dark: bool, **_kwargs):
        return builder.HTML(
            self.head(schema, dark),
            self.body(schema, dark),
        )

    def to_html(self, *_args, **_kwargs) -> str:
        return tostring(
            self.to_e(schema=self.schema, dark=self.dark),
            encoding="unicode",
            pretty_print=True,
        )

    async def render(
        self, width: int = 720, height: int = 10, device_scale_factor: float = 1.0
    ) -> bytes:
        browser = Ariadne.launch_manager.get_interface(PlaywrightBrowser)
        async with browser.page(
            viewport={"width": width, "height": height},
            device_scale_factor=device_scale_factor,
        ) as page:
            logger.info(f"[{self.title}] Setting content...")
            await page.set_content(self.to_html())
            logger.info(f"[{self.title}] Getting screenshot...")
            img = await page.screenshot(
                type="jpeg", quality=80, full_page=True, scale="device"
            )
            logger.success(f"[{self.title}] Done.")
            return img
