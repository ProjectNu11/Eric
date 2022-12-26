from lxml.html import builder
from lxml.html.builder import CLASS
from typing_extensions import Self

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style
from library.ui.util import wrap_text
from library.util.misc import inflate


class _GenericBoxText(Element):
    size: int
    text: str
    is_desc: bool
    highlight: bool

    def __init__(self, text: str, size: int, is_desc: bool, highlight: bool):
        self.text = text
        self.size = size
        self.is_desc = is_desc
        self.highlight = highlight

    def __hash__(self):
        return hash(
            f"_GenericBoxText:{self.text}:{self.size}:{self.is_desc}:{self.highlight}"
        )

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        if not self.is_desc:
            return {Style({"color-text": f"color: {schema.TEXT.rgb(dark)}"})}
        return (
            {Style({"color-description": f"color: {schema.DESCRIPTION.rgb(dark)}"})}
            if self.is_desc
            else {Style({"color-text": f"color: {schema.TEXT.rgb(dark)}"})}
        )

    def to_e(self, *, schema: ColorSchema, dark: bool, **_kwargs) -> str:
        return builder.DIV(
            *wrap_text(self.text),
            CLASS(" ".join(self.style_keys(schema, dark))),
            style=f"font-size: {self.size}px; word-wrap: break-word",
        )


class GenericBoxItem(Element):
    TEXT_SIZE: int = 35
    DESCRIPTION_SIZE: int = 25

    text: _GenericBoxText | None
    description: _GenericBoxText | None

    def __init__(
        self,
        text: str | None,
        description: str | None = None,
        _switch: bool | None = None,
        highlight: bool = False,
    ):
        assert (
            text is not None or description is not None
        ), "text and description cannot be None at the same time"
        self.text = (
            _GenericBoxText(text, self.TEXT_SIZE, False, highlight)
            if text is not None
            else None
        )
        self.description = (
            _GenericBoxText(description, self.DESCRIPTION_SIZE, True, highlight)
            if description is not None
            else None
        )

    def __hash__(self):
        return hash(f"_GenericBoxItem:{hash(self.text)}:{hash(self.description)}")

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return set().union(
            self.text.style(schema, dark) if self.text is not None else set(),
            self.description.style(schema, dark)
            if self.description is not None
            else set(),
            {
                Style(
                    {
                        "color-foreground": f"background-color: "
                        f"{schema.FOREGROUND.rgb(dark)}"
                    }
                ),
            },
        )

    def set_text(self, text: str, highlight: bool = False) -> Self:
        if self.text:
            self.text.text = text
        else:
            self.text = _GenericBoxText(text, self.TEXT_SIZE, False, highlight)
        return self

    def set_description(self, description: str, highlight: bool = False) -> Self:
        if self.description:
            self.description.text = description
        else:
            self.description = _GenericBoxText(
                description, self.DESCRIPTION_SIZE, True, highlight
            )
        return self

    def to_e(self, *, schema: ColorSchema, dark: bool, **_kwargs) -> str:
        parts = [
            self.text.to_e(schema=schema, dark=dark) if self.text else None,
            self.description.to_e(schema=schema, dark=dark)
            if self.description
            else None,
        ]
        return builder.DIV(
            *[part for part in parts if part is not None],
            CLASS(" ".join({*self.style_keys(schema, dark)})),
            style="display: flex; padding: 40px 0 40px 0; flex-direction: column",
        )


class GenericBox(Element):
    items: list[GenericBoxItem]
    boarder: int

    def __init__(self, *items: GenericBoxItem, boarder: int = 40):
        self.items = []
        self.boarder = boarder
        self.add(*items)

    def __hash__(self):
        return hash(f"GenericBox:{':'.join(str(hash(item)) for item in self.items)})")

    def add(self, *items: GenericBoxItem) -> Self:
        for item in items:
            if self.items:
                self.items.append(self._divider)
            self.items.append(item)
        return self

    @property
    def _divider(self):
        return builder.DIV({"class": "color-line", "style": "height: 3px"})

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        return {
            Style({"color-line": f"background-color: {schema.LINE.rgb(dark)}"})
        }.union(
            inflate(  # type: ignore
                [
                    item.style(schema, dark)
                    for item in self.items
                    if isinstance(item, GenericBoxItem)
                ]
            )
        )

    def to_e(self, *, schema: ColorSchema, dark: bool, **_kwargs) -> str:
        return builder.DIV(
            builder.DIV(
                *[
                    item.to_e(schema=schema, dark=dark)
                    if isinstance(item, GenericBoxItem)
                    else item
                    for item in self.items
                ],
                CLASS("color-foreground round-corner"),
                style="padding: 0 40px 0 40px",
            ),
            {},
        )
