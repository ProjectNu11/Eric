from typing_extensions import Self

from lxml.html import builder, tostring

from library.ui.color import ColorSchema, is_dark
from library.ui.element.base import Element, Style
from library.util.misc import inflate


class Page(Element):

    elements: list[Element]
    max_width: int
    styles: set[Style[str, str]]
    schema: ColorSchema
    dark: bool
    border_radius: int

    def __init__(
        self,
        *elements: Element | list[Element] | tuple[Element],
        schema: ColorSchema,
        dark: bool = None,
        max_width: int = 800,
        border_radius: int = 40,
    ):
        if dark is None:
            dark = is_dark()
        self.schema = schema
        self.dark = dark
        self.max_width = max_width
        self.border_radius = border_radius
        self.elements = []
        self.add(*elements)

    def add(self, *elements: Element | list[Element] | tuple[Element]) -> Self:
        for element in inflate(elements):
            element.init(self.schema, self.dark)
            self.elements.append(element)
        return self

    @property
    def style(self) -> set[Style[str, str]]:
        return {
            Style(
                {
                    "auto-width": f"width: 100%; max-width: {self.max_width}px",
                    "round-corner": f"border-radius: {self.border_radius}px",
                }
            ),
        }

    def styles(self):
        return {self.gen_style()} | {element.gen_style() for element in self.elements}

    def head(self):
        return builder.HEAD(
            builder.TITLE("Page"),
            builder.META(charset="utf-8"),
            *self.styles(),
        )

    def body(self):
        return builder.BODY(*[element.to_e() for element in self.elements])

    def to_e(self):
        return builder.HTML(
            self.head(),
            self.body(),
        )

    def to_html(self, *_args, **_kwargs) -> str:
        return tostring(self.to_e(), encoding="unicode")
