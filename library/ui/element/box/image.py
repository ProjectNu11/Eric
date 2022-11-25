from base64 import b64encode
from io import BytesIO
from pathlib import Path

from PIL import Image
from lxml import etree
from lxml.html import builder
from lxml.html.builder import CLASS
from typing_extensions import Self

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style


class ImageBox(Element):
    img: bytes = None
    url: str = None
    base64: str = None

    def __init__(
        self,
        *,
        img: Image.Image | bytes | Path = None,
        url: str = None,
        base64: str = None,
    ):
        assert img or url or base64, "ImageBox must have img or url or base64"
        if url:
            self.url = url
        elif base64:
            self.base64 = base64
        else:
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

    def __hash__(self):
        return hash(f"_ImageBox:{self.img}:{self.url}:{self.base64}")

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return set()

    @classmethod
    def from_file(cls, path: Path | str) -> Self:
        return cls(img=Image.open(path))

    @classmethod
    def from_base64(cls, data: str) -> Self:
        return cls(base64=data)

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        return cls(img=data)

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(url=url)

    def _to_e_bytes(self):
        data = self.base64 or b64encode(self.img).decode("utf-8")
        # 使用 lxml.etree 防止转义
        return etree.XML(
            f'<img src="data:image/png;base64,{data}" '
            f'class="round-corner" style="width: 100%" />'
        )

    def _to_e_url(self):
        return builder.IMG(CLASS("round-corner"), src=self.url, style="width: 100%")

    def to_e(self, *_args, **_kwargs):
        return self._to_e_bytes() if self.img or self.base64 else self._to_e_url()
