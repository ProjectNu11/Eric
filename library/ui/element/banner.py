from pathlib import Path

from lxml.html import builder
from lxml.html.builder import CLASS
from PIL import Image

from library.ui.element.base import Element
from library.ui.element.blank import Blank
from library.ui.element.icon import Icon
from library.ui.util import wrap_text


class Banner(Element):
    text: str
    icon: Icon | None
    blank_height: int
    font_size: int

    def __init__(
        self,
        text: str,
        icon: str | Image.Image | Path | Icon | None = None,
        *,
        blank_height: int = 90,
        font_size: int = 40,
    ):
        self.text = text
        if isinstance(icon, Icon) or icon is None:
            self.icon = icon
        else:
            self.icon = self._get_icon(icon)
        self.blank_height = blank_height
        self.font_size = font_size

    @staticmethod
    def _get_icon(icon: str | Image.Image | Path) -> Icon:
        if isinstance(icon, Image.Image):
            return Icon(img=icon)
        return Icon.from_file(icon) if isinstance(icon, Path) else Icon(svg=icon)

    def to_e(self, *args, **kwargs):
        return builder.DIV(
            Blank(self.blank_height).to_e(),
            builder.DIV(
                *wrap_text(self.text),
                CLASS("color-colored-text"),
                style=f"padding: 0 40px 0 40px; "
                f"font-size: {self.font_size}px; word-wrap: break-word",
            ),
        )
