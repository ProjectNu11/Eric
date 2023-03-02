import re
from pathlib import Path
from typing import TypeVar

from lxml.builder import E
from lxml.etree import _Element  # noqa

_T = TypeVar("_T")

HYPERLINK_PATTERN = re.compile(r"https?://\S+")
FONT_PATH = Path.cwd().resolve() / "library" / "assets" / "fonts"
FONT_MIME_MAP = {
    "collection": "font/collection",
    "otf": "font/otf",
    "sfnt": "font/sfnt",
    "ttf": "font/ttf",
    "woff": "font/woff",
    "woff2": "font/woff2",
}


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


def _add_hyperlink(text: list[_T]) -> list[_T | _Element]:
    wrapped = []
    for part in text:
        if not isinstance(part, str):
            wrapped.append(part)
            continue
        if not (urls := HYPERLINK_PATTERN.findall(part)):
            wrapped.append(part)
            continue
        urls = [E.a(link, href=link) for link in urls]
        parts = re.split(HYPERLINK_PATTERN, part)
        for _part, url in zip(parts, urls):
            wrapped.extend((_part, url))
        wrapped.append(parts[-1])
    return wrapped
