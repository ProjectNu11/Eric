from creart import add_creator

from library.ui.color import ColorCreator
from library.ui.color.schema import ColorPair, ColorSchema, ColorSingle
from library.ui.element.page import Page

add_creator(ColorCreator)

__all__ = ["ColorSchema", "ColorPair", "ColorSingle", "Page"]
