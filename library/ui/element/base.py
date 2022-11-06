from abc import abstractmethod

from library.ui.color import ColorSchema


class Style(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))


class Element:
    @abstractmethod
    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        """生成 lxml.html.builder.E 对象"""
        pass

    @abstractmethod
    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        pass

    def style_keys(self, schema: ColorSchema, dark: bool) -> set[str]:
        return {key for style in self.style(schema, dark) for key in style.keys()}
