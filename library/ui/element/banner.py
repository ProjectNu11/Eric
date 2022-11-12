from pathlib import Path

from PIL import Image
from lxml.html import builder

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style
from library.ui.element.blank import Blank
from library.ui.element.icon import Icon


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

    def __hash__(self):
        return hash(f"_Banner:{self.text}:{hash(self.icon)}:{self.blank_height}")

    @staticmethod
    def _get_icon(icon: str | Image.Image | Path) -> Icon:
        if isinstance(icon, Image.Image):
            return Icon(img=icon)
        if isinstance(icon, Path):
            return Icon.from_file(icon)
        return Icon(svg=icon)

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return {Style({"color-text": f"color: {schema.TEXT.rgb(dark)}"})}

    def to_e(self, *_args, schema: ColorSchema, dark: bool, **_kwargs):
        return builder.DIV(
            Blank(self.blank_height).to_e(),
            builder.DIV(
                self.text,
                {
                    "class": " ".join(self.style_keys(schema, dark)),
                    "style": f"padding: 0 40px 0 40px; "
                    f"font-size: {self.font_size}px; word-wrap: break-word",
                },
            ),
        )
