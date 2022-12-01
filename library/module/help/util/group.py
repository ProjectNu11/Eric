from creart import it
from graia.ariadne.model import Group

from library.ui import Page
from library.ui.element import GenericBox, GenericBoxItem
from library.util.module import Modules


def _iter_module():
    return iter(it(Modules).search(lambda module: not module.advanced.hidden))


def _get_header(field: int | Group) -> GenericBox:
    if isinstance(field, Group):
        return GenericBox(GenericBoxItem(field.name, str(field.id)))
    return GenericBox(GenericBoxItem("私聊"))


async def get_field_page(field: int | Group, title: str) -> Page:
    page = Page(title=title)
    page.add(_get_header(field))

    return page
