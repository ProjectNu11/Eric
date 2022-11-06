from lxml.html import builder, tostring
from typing_extensions import Self

from library.ui.color import ColorSchema, is_dark
from library.ui.element.base import Element, Style
from library.ui.element.blank import Blank
from library.util.misc import inflate


class Page(Element):

    elements: list[Element]
    max_width: int
    schema: ColorSchema
    dark: bool
    styles: set[Style[str, str]]
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
        for element in elements:
            if self.elements:
                self.elements.append(Blank(self.border_radius))
            self.elements.append(element)
        return self

    def style(self, *_) -> set[Style[str, str]]:
        return {
            Style(
                {
                    "color-background": f"background-color: {self.schema.BACKGROUND.rgb(self.dark)}",
                    "auto-width": "width: 100%; "
                    f"max-width: {self.max_width - self.border_radius * 2}px",
                    "round-corner": f"border-radius: {self.border_radius}px",
                }
            ),
        }

    def styles(self, schema: ColorSchema, dark: bool):
        return builder.E.style(
            " ".join(
                f".{key} {{ {value.get(key, '')} }}"
                for value in self.style().union(
                    inflate(element.style(schema, dark) for element in self.elements)
                )
                for key in value
            )
        )

    def head(self, schema: ColorSchema, dark: bool):
        return builder.HEAD(
            builder.TITLE("Page"),
            builder.META(charset="utf-8"),
            self.styles(schema, dark),
        )

    def body(self, schema: ColorSchema, dark: bool):
        return builder.BODY(
            {
                "class": "color-background auto-width",
                "style": "margin: 0 auto",
            },
            *(element.to_e(schema=schema, dark=dark) for element in self.elements),
        )

    def to_e(self, *_args, schema: ColorSchema, dark: bool, **_kwargs):
        return builder.HTML(
            self.head(schema, dark),
            self.body(schema, dark),
        )

    def to_html(self, *_args, **_kwargs) -> str:
        return tostring(
            self.to_e(schema=self.schema, dark=self.dark), encoding="unicode"
        )
