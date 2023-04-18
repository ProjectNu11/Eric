from base64 import b64decode, b64encode
from io import BytesIO
from pathlib import Path

from creart import it
from kayaku import create
from lxml import etree
from lxml.html import builder
from lxml.html.builder import CLASS
from PIL import Image
from typing_extensions import Self

from library.model.config import EricConfig
from library.ui.element.base import Element
from library.util.session_container import SessionContainer


class ImageBox(Element):
    img: bytes = None
    url: str = None
    base64: str = None
    src: str = None

    def __init__(
        self,
        *,
        img: Image.Image | bytes | Path = None,
        url: str = None,
        base64: str = None,
        src: str = None,
    ):
        assert (
            img or url or base64 or src
        ), "ImageBox must have img or url or base64 or src"
        if url:
            self.url = url
        elif base64:
            self.base64 = base64
        elif src:
            self.src = src
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

    @classmethod
    def from_file(cls, path: Path | str) -> Self:
        return cls(img=Image.open(path))

    @classmethod
    def from_base64(cls, data: str) -> Self:
        return cls(base64=data)

    @classmethod
    def from_src(cls, src: str) -> Self:
        return cls(src=src)

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        return cls(img=data)

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(url=url)

    def to_bytes(self) -> bytes:
        if self.img:
            return self.img
        elif self.base64:
            return b64decode(self.base64)
        raise ValueError(f"Cannot extract bytes from {self}")

    async def fetch(self, suppress: bool = True):
        if self.img or self.base64:
            return
        if not self.url:
            if suppress:
                return
            raise ValueError(f"Cannot fetch image from {self}")
        session = await it(SessionContainer).get(self.__class__.__qualname__)
        config: EricConfig = create(EricConfig)
        async with session.get(self.url, proxy=config.proxy) as resp:
            if not suppress:
                resp.raise_for_status()
            self.img = await resp.read()

    def _to_e_bytes(self):
        data = self.base64 or b64encode(self.img).decode("utf-8")
        return etree.XML(
            f'<img src="data:image/png;base64,{data}" '
            f'class="round-corner" style="width: 100%" />'
        )

    def _to_e_src(self):
        return etree.XML(
            f'<img src="{self.src}" ' f'class="round-corner" style="width: 100%" />'
        )

    def _to_e_url(self):
        return builder.IMG(CLASS("round-corner"), src=self.url, style="width: 100%")

    def to_e(self, *args, **kwargs):
        if self.img or self.base64:
            return self._to_e_bytes()
        elif self.url:
            return self._to_e_url()
        return self._to_e_src()
