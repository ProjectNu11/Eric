from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.element import Blank, Element
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

    def _description(self) -> str:
        if self.description is None:
            return ""
        return builder.DIV(
            *wrap_text(self.description),
            CLASS("color-description"),
            style=f"font-size: {self.description_size}px; word-wrap: break-word; padding-top: 10px",
        )

    def to_e(self, *args, **kwargs):
        return builder.DIV(
            Blank(self.blank_height).to_e(),
            builder.DIV(
                *wrap_text(self.title),
                CLASS("color-colored-text"),
                style=f"font-size: {self.title_size}px; word-wrap: break-word",
            ),
            self._description(),
            style="text-align: center",
        )
