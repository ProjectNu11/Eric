from lxml.html import builder
from typing_extensions import Self

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style
from library.util.misc import inflate


class _GenericBoxText(Element):

    size: int
    text: str

    def __init__(self, text: str, size: int):
        self.text = text
        self.size = size

    @property
    def style_color(self) -> str:
        return f"color: {self.schema.DESCRIPTION.rgb(self.dark)}"

    @property
    def style(self) -> set[Style[str, str]]:
        return {Style({"color-description": self.style_color})}

    def to_e(self, *, schema: ColorSchema, dark: bool, **_kwargs) -> str:
        self.schema = schema
        self.dark = dark
        return builder.DIV(
            self.text,
            {
                "class": " ".join(self.style_keys),
                "style": f"font-size: {self.size}px; word-wrap: break-word",
            },
        )


class GenericBoxItem(Element):

    TEXT_SIZE: int = 35
    DESCRIPTION_SIZE: int = 25

    text: _GenericBoxText
    description: _GenericBoxText

    def __init__(self, text: str, description: str):
        self.text = _GenericBoxText(text, self.TEXT_SIZE)
        self.description = _GenericBoxText(description, self.DESCRIPTION_SIZE)

    @property
    def style(self) -> set[Style[str, str]]:
        return (
            self.text.style
            | self.description.style
            | {
                Style(
                    {
                        "color-foreground": f"background-color: "
                        f"{self.schema.FOREGROUND.rgb(self.dark)}"
                    }
                ),
            }
        )

    def set_text(self, text: str) -> Self:
        self.text.text = text
        return self

    def set_description(self, description: str) -> Self:
        self.description.text = description
        return self

    def to_e(self, *, boarder: int = 40, **_kwargs) -> str:
        return builder.DIV(
            self.text.to_e(schema=self.schema, dark=self.dark),
            self.description.to_e(schema=self.schema, dark=self.dark),
            {
                "class": " ".join({*self.style_keys, "auto-width"}),
                "style": "display: flex; "
                f"border-radius: {boarder}px; "
                "margin: 0 auto;"
                "padding: 40px;"
                "flex-direction: column",
            },
        )
