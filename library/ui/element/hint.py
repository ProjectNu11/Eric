from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.color.schema import ColorSchema
from library.ui.element.base import Element
from library.ui.element.blank import Blank
from library.ui.util import wrap_text


class HintBox(Element):
    title: str
    hints: list[str]
    title_size: int
    hint_size: int
    hint_bold: bool

    def __init__(
        self,
        *hints: str,
        title: str = None,
        title_size: int = 35,
        hint_size: int = 30,
        hint_bold: bool = True,
    ):
        self.title = title
        self.hints = list(hints)
        self.title_size = title_size
        self.hint_size = hint_size
        self.hint_bold = hint_bold

    def _title_to_e(self):
        if self.title is None:
            return ""
        return builder.P(
            *wrap_text(self.title),
            CLASS("color-text"),
            style=f"font-size: {self.title_size}px; word-wrap: break-word; margin: 0;",
        )

    def _hints_to_e(self):
        if not self.hints:
            return ""
        hints = [
            builder.P(
                *wrap_text(hint),
                CLASS("color-highlight"),
                style=f"font-size: {self.hint_size}px; "
                f"font-weight: {'bold' if self.hint_bold else 'normal'}; "
                f"word-wrap: break-word; margin: 0;",
            )
            for hint in self.hints
        ]
        for index in range(len(hints) - 1):
            hints.insert(index * 2 - 1, Blank(5).to_e())
        return builder.DIV(*hints)

    def to_e(self, *, schema: ColorSchema, dark: bool, **_kwargs):
        if not self.title and not self.hints:
            return ""
        parts = [self._title_to_e(), self._hints_to_e()]
        if all(part != "" for part in parts):
            parts.insert(1, Blank(10).to_e())
        return builder.DIV(
            *parts,
            CLASS("full-padding round-corner color-hint-bg"),
        )
