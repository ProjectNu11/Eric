from lxml.html import builder

from library.ui.element.base import Element


class Blank(Element):
    height: int

    def __init__(self, height: int):
        self.height = height

    def to_e(self, *_args, **_kwargs) -> str:
        return builder.DIV(style=f"height: {self.height}px;")
