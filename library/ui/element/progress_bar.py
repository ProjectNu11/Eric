from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.color import ColorSchema
from library.ui.element.base import Element, Style
from library.ui.util import wrap_text


class ProgressBar(Element):
    percent: float
    text: str | None
    description: str | None

    height: int
    text_size: int
    description_size: int

    def __init__(
        self,
        percent: float,
        text: str | None = None,
        description: str | None = None,
        height: int = 40,
        text_size: int = 35,
        description_size: int = 25,
    ):
        self.percent = percent * 100
        self.text = text
        self.description = description
        self.height = height
        self.text_size = text_size
        self.description_size = description_size

    def __hash__(self):
        return hash(f"_ProgressBar:{self.percent}:{self.text!r}:{self.description!r}")

    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        styles = {
            Style(
                {
                    "color-progress-bar": f"background-color: {schema.HIGHLIGHT.rgb(dark)}"
                }
            )
        }
        if self.text is not None:
            styles.add(Style({"color-text": f"color: {schema.TEXT.rgb(dark)}"}))
        if self.description is not None:
            styles.add(
                Style({"color-description": f"color: {schema.DESCRIPTION.rgb(dark)}"})
            )
        return styles

    def _build_text(self):
        return (
            builder.DIV(
                *wrap_text(self.text),
                CLASS("color-text"),
                style=f"font-size: {self.text_size}px; "
                f"word-wrap: break-word; "
                f"padding: 0 40px 20px 40px",
            )
            if self.text is not None
            else None
        )

    def _build_description(self):
        return (
            builder.DIV(
                *wrap_text(self.description),
                CLASS("color-description"),
                style=f"font-size: {self.description_size}px; "
                f"word-wrap: break-word; "
                f"padding: 20px 40px 0 40px",
            )
            if self.description is not None
            else None
        )

    def _build_progress_bar(self, schema: ColorSchema, dark: bool):
        return builder.DIV(
            builder.DIV(
                builder.DIV(
                    CLASS("color-progress-bar"),
                    style=f"width: {self.percent}%; height: 100%",
                ),
                style=f"height: {self.height}px; "
                "width: 100%; "
                f"background-color: {schema.SECONDARY_HIGHLIGHT.rgb(dark)}; "
                f"border-radius: {self.height}px; "
                "overflow: hidden",
            ),
            style="padding: 0 40px 0 40px",
        )

    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        parts = [
            self._build_text(),
            self._build_progress_bar(schema, dark),
            self._build_description(),
        ]
        parts = [part for part in parts if part is not None]
        return builder.DIV(
            *parts, style="width: 100%; display: flex; flex-direction: column"
        )
