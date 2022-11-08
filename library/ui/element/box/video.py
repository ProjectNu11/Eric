from lxml.html.builder import E
from typing_extensions import Self

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style


class VideoBox(Element):
    url: str
    loop: bool
    controls: bool

    def __init__(self, *, url: str, loop: bool = False, controls: bool = True):
        self.url = url
        self.loop = loop
        self.controls = controls

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return set()

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(url=url)

    def to_e(self, *_args, **_kwargs):
        return E.VIDEO(
            {
                "src": self.url,
                "class": "round-corner",
                "style": "width: 100%",
            },
            "loop" if self.loop else "",
            "controls" if self.controls else "",
        )
