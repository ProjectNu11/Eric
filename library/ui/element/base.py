from abc import abstractmethod

from library.ui.color import ColorSchema


class Style(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))


class Element:
    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"{' '.join(f'{k}={v}' for k, v in self.__dict__.items())}>"
        )

    def __hash__(self):
        return hash(self.__repr__())

    @abstractmethod
    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        """生成 lxml.html.builder.E 对象"""
        pass

    @abstractmethod
    def style(self, schema: ColorSchema, dark: bool) -> set[Style[str, str]]:
        pass

    def style_keys(self, schema: ColorSchema, dark: bool) -> set[str]:
        return {key for style in self.style(schema, dark) for key in style.keys()}
