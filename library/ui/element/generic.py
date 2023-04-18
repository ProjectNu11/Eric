import base64

from lxml import etree
from lxml.html import builder
from lxml.html.builder import CLASS
from typing_extensions import Self

from library.ui.color import ColorSchema
from library.ui.element.base import Element
from library.ui.util import wrap_text


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

    @property
    def style(self) -> str:
        if self.highlight and self.is_desc:
            return "color-highlight"
        return "color-description" if self.is_desc else "color-text"

    def to_e(self, *args, **kwargs):
        return builder.DIV(
            *wrap_text(self.text),
            CLASS(self.style),
            style=f"font-size: {self.size}px; word-wrap: break-word",
        )


class GenericBoxItem(Element):
    TEXT_SIZE: int = 35
    DESCRIPTION_SIZE: int = 25
    IMAGE_SIZE: int = 100

    text: _GenericBoxText | None
    description: _GenericBoxText | None
    image: bytes | None

    def __init__(
        self,
        text: str | None,
        description: str | None = None,
        _switch: bool | None = None,
        highlight: bool = False,
        image: bytes | None = None,
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
        self.image = image

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

    def _get_parts(self, *, schema: ColorSchema, dark: bool) -> list[str]:
        return [
            self.text.to_e(schema=schema, dark=dark) if self.text else None,
            self.description.to_e(schema=schema, dark=dark)
            if self.description
            else None,
        ]

    def _to_e_no_img(self, *, schema: ColorSchema, dark: bool, **_kwargs) -> str:
        parts = self._get_parts(schema=schema, dark=dark)
        return builder.DIV(
            *[part for part in parts if part is not None],
            CLASS("color-foreground-bg tb-padding"),
            style="display: flex; flex-direction: column",
        )

    def _to_e_img(self, *, schema: ColorSchema, dark: bool, **_kwargs) -> str:
        img_b64 = base64.b64encode(self.image).decode("utf-8")
        parts = self._get_parts(schema=schema, dark=dark)
        return builder.DIV(
            builder.DIV(
                *[part for part in parts if part is not None],
                CLASS("color-foreground-bg tb-padding"),
                style="display: flex; flex-direction: column",
            ),
            etree.XML(
                f'<img src="data:image/png;base64,{img_b64}" '
                f'style="width: {self.IMAGE_SIZE}px; '
                f'height: {self.IMAGE_SIZE}px; border-radius: 50%;"/>'
            ),
            style="display: flex; justify-content: space-between; align-items: center",
        )

    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        return (
            self._to_e_img(schema=schema, dark=dark)
            if self.image
            else self._to_e_no_img(schema=schema, dark=dark)
        )


class GenericBox(Element):
    items: list[GenericBoxItem]
    boarder: int

    def __init__(self, *items: GenericBoxItem, boarder: int = 40):
        self.items = []
        self.boarder = boarder
        self.add(*items)

    def add(self, *items: GenericBoxItem) -> Self:
        for item in items:
            if self.items:
                self.items.append(self._divider)
            self.items.append(item)
        return self

    @property
    def _divider(self):
        return builder.DIV(CLASS("color-line-bg"), style="height: 3px")

    def to_e(self, *args, schema: ColorSchema, dark: bool, **_kwargs):
        return builder.DIV(
            *[
                item.to_e(schema=schema, dark=dark)
                if isinstance(item, GenericBoxItem)
                else item
                for item in self.items
            ],
            CLASS("color-foreground-bg round-corner lr-padding"),
        )
