import re
from typing import TypeVar

from lxml.builder import E
from lxml.etree import _Element  # noqa

# type(E.DIV()) == lxml.etree._Element

HYPERLINK_PATTERN = re.compile(r"https?://\S+")
_T = TypeVar("_T")


def wrap_text(
    text: str | list, newline: bool = True, hyperlink: bool = True
) -> list[str | _Element]:
    wrapped = [text] if isinstance(text, str) else text
    if hyperlink:
        wrapped = _add_hyperlink(wrapped)
    if newline:
        wrapped = _newline_to_br(wrapped)
    return wrapped


def _newline_to_br(text: list[_T]) -> list[_T | _Element]:
    wrapped = []
    for part in text:
        if not isinstance(part, str):
            wrapped.append(part)
            continue
        lines = []
        for line in part.splitlines():
            lines.extend((E.br(), line))
        wrapped.extend(lines[1:])
    return wrapped


def _replace_with_hyperlink(text: str, link: str) -> list[str | _Element]:
    wrapped = []
    for piece in text.split(link):
        wrapped.extend((piece, E.a(link, href=link)))
    return wrapped[:-1]


def _add_hyperlink(text: list[_T]) -> list[_T | _Element]:
    # wrapped = []
    # for part in text:
    #     if not isinstance(part, str):
    #         wrapped.append(part)
    #         continue
    #     if not (urls := HYPERLINK_PATTERN.findall(part)):
    #         wrapped.append(part)
    #         continue
    #     parts = []
    #     for url in urls:
    #         parts.extend(_replace_with_hyperlink(part, url))
    #     wrapped.extend(parts)
    # return wrapped

    # Temporarily commented out the above code
    # TODO Re-implement hyperlink functionality
    return text
