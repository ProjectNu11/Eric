from library.ui.element.base import Element

from lxml.html import builder


class Blank(Element):

    height: int

    def __init__(self, height: int):
        self.height = height

    @property
    def style(self) -> set:
        return set()

    def to_e(self) -> str:
        return builder.DIV(style=f"height: {self.height}px;")
