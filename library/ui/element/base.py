from abc import abstractmethod
from typing import Self

from library.model.misc import Hashable
from library.ui.color import ColorSchema


class Element(Hashable):
    @property
    def require(self) -> set[Self]:
        """返回该元素所依赖的其他元素，将被自动添加到页面中"""
        return set()

    @abstractmethod
    def to_e(self, *args, schema: ColorSchema, dark: bool, **kwargs):
        """
        生成 lxml.html.builder.E 对象

        Args:
            schema: 颜色方案
            dark: 是否为暗色模式
        """
        pass
