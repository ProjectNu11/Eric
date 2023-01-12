from creart import add_creator

from library.ui.color import ColorCreator
from library.ui.color.schema import ColorPair, ColorSchema, ColorSingle
from library.ui.element import (
    Banner,
    Blank,
    Button,
    Element,
    GenericBox,
    GenericBoxItem,
    Icon,
    ImageBox,
    Page,
    ProgressBar,
    Title,
    VideoBox,
)

add_creator(ColorCreator)

__all__ = [
    "ColorPair",
    "ColorSchema",
    "ColorSingle",
    "Banner",
    "Blank",
    "Button",
    "Element",
    "GenericBox",
    "GenericBoxItem",
    "Icon",
    "ImageBox",
    "Page",
    "ProgressBar",
    "Title",
    "VideoBox",
]
