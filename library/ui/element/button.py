from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.color import ColorSchema
from library.ui.element import Element
from library.ui.element.base import Style
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

    def __hash__(self):
        return hash(f"_Button:{self.text}:{self.link}:{self.width}:{self.text_size}")

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return {
            Style({"color-button": f"background-color: {schema.FOREGROUND.rgb(dark)}"}),
            Style(
                {
                    "color-button:hover": f"background-color: {schema.SECONDARY_HIGHLIGHT.rgb(dark)}; "
                    f"opacity: 0.8"
                }
            ),
            Style({"color-text": f"color: {schema.TEXT.rgb(dark)}"}),
        }

    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        return builder.DIV(
            builder.A(
                *wrap_text(self.text, hyperlink=False),
                CLASS(
                    " ".join(
                        self.style_keys(schema, dark) | {"round-corner", "color-text"}
                    )
                ),
                href=self.link or "#",
                style=f"font-size: {self.text_size}px; "
                "word-wrap: break-word; "
                "padding: 10px 40px 10px 40px; "
                f"text-align: center; "
                f"cursor: pointer" + (f"; width: {self.width}px" if self.width else ""),
            ),
            style="display: flex; align-items: center; justify-content: center",
        )
