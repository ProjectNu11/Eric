from pathlib import Path

from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui import ColorSchema
from library.ui.element.base import Element
from library.ui.element.script import ScriptBox


class QRCodeBox(Element):
    content: str
    size: int

    def __init__(self, content: str, size: int = 80):
        self.content = content
        self.size = size

    @property
    def require(self):
        return {
            ScriptBox.from_file(Path.cwd() / "library" / "assets" / "js" / "qrcode.js")
        }

    def to_e(self, *, schema: ColorSchema, dark: bool, **_kwargs):
        return builder.DIV(
            builder.DIV(
                CLASS("color-foreground-bg tb-padding round-corner"),
                style="display: flex; justify-content: center; align-items: center",
                id=str(self.__hash__()),
            ),
            ScriptBox(
                script=f"""
                    new QRCode("{self.__hash__()}", {{
                        text: "{self.content}",
                        width: {self.size},
                        height: {self.size},
                        colorDark : "{schema.COLORED_TEXT.hex(dark=dark)}",
                        colorLight : "{schema.FOREGROUND.hex(dark=dark)}",
                        correctLevel : QRCode.CorrectLevel.H
                    }});
                    """
            ).to_e(),
        )
