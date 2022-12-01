from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.color import ColorSchema
from library.ui.element import Element, Blank
from library.ui.element.base import Style
from library.ui.util import wrap_text


class Title(Element):
    title: str
    description: str
    title_size: int
    description_size: int

    blank_height: int

    def __init__(
        self,
        title: str,
        description: str = "",
        *,
        title_size: int = 50,
        description_size: int = 25,
        blank_height: int = 90,
    ):
        self.title = title
        self.description = description
        self.title_size = title_size
        self.description_size = description_size
        self.blank_height = blank_height

    def __hash__(self):
        return hash(
            f"_Title:{self.title}:{self.description}:{self.title_size}:{self.description_size}"
        )

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return {
            Style(
                {
                    "color-text": f"color: {schema.TEXT.rgb(dark)}",
                    "color-description": f"color: {schema.DESCRIPTION.rgb(dark)}",
                }
            )
        }

    def _description(self) -> str:
        if self.description is None:
            return ""
        return builder.DIV(
            *wrap_text(self.description),
            CLASS("color-description"),
            style=f"font-size: {self.description_size}px; word-wrap: break-word; padding-top: 10px",
        )

    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        return builder.DIV(
            Blank(self.blank_height).to_e(),
            builder.DIV(
                *wrap_text(self.title),
                CLASS("color-text"),
                style=f"font-size: {self.title_size}px; word-wrap: break-word",
            ),
            self._description(),
            CLASS(" ".join(self.style_keys(schema, dark))),
            style="text-align: center",
        )
