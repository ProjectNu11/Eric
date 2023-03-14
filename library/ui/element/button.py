from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.color import ColorSchema
from library.ui.element import Element
from library.ui.util import wrap_text


class Button(Element):
    text: str
    link: str
    width: int | None
    text_size: int

    def __init__(
        self,
        text: str,
        link: str = "",
        *,
        width: int | None = None,
        text_size: int = 35,
    ):
        self.text = text
        self.link = link
        self.width = width
        self.text_size = text_size

    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        return builder.DIV(
            builder.A(
                *wrap_text(self.text, hyperlink=False),
                CLASS("color-foreground-bg round-corner color-text"),
                href=self.link or "#",
                style=f"font-size: {self.text_size}px; "
                "word-wrap: break-word; "
                "padding: 10px 40px 10px 40px; "
                "text-align: center; "
                "text-decoration: none; "
                "cursor: pointer"
                + (f"; width: {self.width}px;" if self.width else ";"),
            ),
            style="display: flex; align-items: center; justify-content: center;",
        )
