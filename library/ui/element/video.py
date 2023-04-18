from lxml.html.builder import CLASS, E
from typing_extensions import Self

from library.ui.element.base import Element


class VideoBox(Element):
    url: str
    loop: bool
    controls: bool

    def __init__(self, *, url: str, loop: bool = False, controls: bool = True):
        self.url = url
        self.loop = loop
        self.controls = controls

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(url=url)

    def to_e(self, *args, **kwargs):
        properties = [
            {"loop": "1"} if self.loop else {},
            {"controls": "1"} if self.controls else {},
            {"autoplay": "1"},
        ]
        return E.video(
            CLASS("round-corner"),
            src=self.url,
            style="width: 100%",
            *properties,
        )
