from lxml.html import builder

from library.ui.element.base import Element, Style


class Blank(Element):

    height: int

    def __init__(self, height: int):
        self.height = height

    def __hash__(self):
        return hash(f"_Blank:{self.height}")

    def style(self, *_args, **_kwargs) -> set[Style[str, str]]:
        return set()

    def to_e(self, *_args, **_kwargs) -> str:
        return builder.DIV(style=f"height: {self.height}px;")
