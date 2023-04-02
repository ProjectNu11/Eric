from pathlib import Path
from typing import Self

from lxml.html import builder

from library.ui.element.base import Element


class ScriptBox(Element):
    script: str
    url: str

    def __init__(self, *, script: str = None, url: str = None):
        self.script = script
        self.url = url

    @classmethod
    def from_file(cls, path: Path) -> Self:
        return cls(script=path.read_text(encoding="utf-8"))

    def to_e(self, *_args, **_kwargs):
        if self.script is not None:
            return builder.SCRIPT(self.script)
        elif self.url is not None:
            return builder.SCRIPT(src=self.url)
        return ""
