from pathlib import Path

from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.color.schema import ColorSchema
from library.ui.element._cfg import PageConfig
from library.ui.element.base import Element
from library.ui.element.blank import Blank
from library.ui.element.script import ScriptBox
from library.ui.util import wrap_text


class QRCodeBox(Element):
    content: str
    size: int
    title: str | None
    title_size: int
    title_bold: bool
    description: str | None
    description_size: int
    lr_padding: int | None

    def __init__(
        self,
        content: str,
        size: int = 120,
        *,
        title: str = None,
        title_size: int = 35,
        title_bold: bool = False,
        description: str = None,
        description_size: int = 25,
        lr_padding: int = 40,
    ):
        self.content = content
        self.size = size
        self.title = title
        self.title_size = title_size
        self.title_bold = title_bold
        self.description = description
        self.description_size = description_size
        self.lr_padding = max(40, lr_padding)

    @property
    def require(self):
        return {
            ScriptBox.from_file(Path.cwd() / "library" / "assets" / "js" / "qrcode.js")
        }

    def _title_to_e(self):
        if self.title is None:
            return ""
        return builder.DIV(
            *wrap_text(self.title),
            CLASS("color-text"),
            style=f"font-size: {self.title_size}px; "
            f"font-weight: {'bold' if self.title_bold else 'normal'}; "
            f"word-wrap: break-word; ",
        )

    def _desc_to_e(self):
        if self.description is None:
            return ""
        return builder.DIV(
            *wrap_text(self.description),
            CLASS("color-description"),
            style=f"font-size: {self.description_size}px; " f"word-wrap: break-word; ",
        )

    def to_e(self, *args, schema: ColorSchema, page_cfg: PageConfig, **kwargs):
        padding = (
            "40px" if self.lr_padding is None else f"40px {self.lr_padding}px " * 2
        )
        parts = [self._title_to_e(), self._desc_to_e()]
        if parts[0] != "" or parts[1] != "":
            parts.append(Blank(page_cfg.border_radius // 2).to_e())
        if parts[0] != "" and parts[1] != "":
            parts.insert(1, Blank(10).to_e())
        return builder.DIV(
            builder.DIV(
                *parts,
                builder.DIV(
                    CLASS("color-foreground-light-bg tb-padding"),
                    style=f"display: flex; "
                    f"justify-content: center; "
                    f"align-items: center; "
                    f"border-radius: {page_cfg.border_radius // 2}px;",
                    id=str(self.__hash__()),
                ),
                CLASS("color-foreground-bg round-corner"),
                style=f"padding: {padding}; ",
            ),
            ScriptBox(
                script=f"""
new QRCode("{self.__hash__()}", {{
    text: "{self.content}",
    width: {self.size},
    height: {self.size},
    colorDark : "{schema.COLORED_TEXT.hex(dark=False)}",
    colorLight : "{schema.FOREGROUND.hex(dark=False)}",
    correctLevel : QRCode.CorrectLevel.H
}});
                    """
            ).to_e(),
        )
