from abc import abstractmethod

from library.model.misc import Hashable
from library.ui.color import ColorSchema


class Element(Hashable):
    @abstractmethod
    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        """生成 lxml.html.builder.E 对象"""
        pass
