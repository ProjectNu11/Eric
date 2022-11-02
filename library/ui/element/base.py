from abc import abstractmethod

from lxml.html import builder

from library.ui.color import ColorSchema


class Style(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))


class Element:

    style: set[Style[str, str]] = set()
    schema: ColorSchema
    dark: bool

    @abstractmethod
    def to_e(self, *args, **kwargs):
        """生成 lxml.html.builder.E 对象"""
        pass

    def init(self, schema: ColorSchema, dark: bool):
        self.schema = schema
        self.dark = dark

    def gen_style(self):
        return builder.E.style(
            " ".join(
                f".{key} {{ {'; '.join(value.values())} }}"
                for value in self.style
                for key in value
            )
        )

    @property
    def style_keys(self) -> set[str]:
        return {key for style in self.style for key in style.keys()}
