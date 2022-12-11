from lxml.html.builder import CLASS, E
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

    def __hash__(self):
        return hash(f"_VideoBox:{self.url}:{self.loop}:{self.controls}")

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return set()

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(url=url)

    def to_e(self, *_args, **_kwargs):
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
