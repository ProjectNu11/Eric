from lxml.html import builder
from lxml.html.builder import CLASS

from library.ui.element.base import Element


class Footer(Element):
    upper: str
    middle: str
    lower: str
    upper_size: int
    middle_size: int
    lower_size: int
    upper_bold: bool = False
    middle_bold: bool = True
    lower_bold: bool = False

    def __init__(
        self,
        upper: str = None,
        middle: str = None,
        lower: str = None,
        upper_size: int = 40,
        middle_size: int = 60,
        lower_size: int = 20,
        upper_bold: bool = False,
        middle_bold: bool = True,
        lower_bold: bool = False,
    ):
        self.upper = upper
        self.middle = middle
        self.lower = lower
        self.upper_size = upper_size
        self.middle_size = middle_size
        self.lower_size = lower_size
        self.upper_bold = upper_bold
        self.middle_bold = middle_bold
        self.lower_bold = lower_bold

    def _build_upper(self):
        return (
            builder.P(
                self.upper,
                style=f"font-size: {self.upper_size}px; "
                f"font-weight: {'bold' if self.upper_bold else 'normal'}; "
                f"margin: 0;",
            )
            if self.upper
            else None
        )

    def _build_middle(self):
        return (
            builder.P(
                self.middle,
                style=f"font-size: {self.middle_size}px; "
                f"font-weight: {'bold' if self.middle_bold else 'normal'}; "
                f"margin: 0;",
            )
            if self.middle
            else None
        )

    def _build_lower(self):
        return (
            builder.P(
                self.lower,
                style=f"font-size: {self.lower_size}px; "
                f"font-weight: {'bold' if self.lower_bold else 'normal'}; "
                f"margin: 0;",
            )
            if self.lower
            else None
        )

    def to_e(self, *args, **kwargs):
        parts = [
            self._build_upper(),
            self._build_middle(),
            self._build_lower(),
        ]
        parts = [part for part in parts if part is not None]
        return (
            builder.DIV(
                *parts,
                CLASS("lr-padding color-colored-text"),
                style="opacity: 0.8; text-align: right;",
            )
            if parts
            else ""
        )
