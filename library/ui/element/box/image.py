from base64 import b64encode
from io import BytesIO
from pathlib import Path

from PIL import Image
from lxml.html import builder
from typing_extensions import Self

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style


class ImageBox(Element):
    img: bytes

    def __init__(self, img: Image.Image | bytes | Path):
        if isinstance(img, Path):
            img = Image.open(img)
        if isinstance(img, Image.Image):
            output = BytesIO()
            img.save(output, "JPEG" if img.mode == "RGB" else "PNG")
            img = output.getvalue()
        if isinstance(img, bytes):
            self.img = img
        else:
            raise TypeError

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return set()

    @classmethod
    def from_file(cls, path: Path | str) -> Self:
        return cls(img=Image.open(path))

    def to_e(self, *_args, **_kwargs):
        data = b64encode(self.img).decode("utf-8")
        return builder.IMG(
            {
                "src": f"data:image/png;base64,{data}",
                "class": "round-corner",
                "style": "width: 100%",
            }
        )
