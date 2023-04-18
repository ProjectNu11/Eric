from abc import abstractmethod

from typing_extensions import Self

from library.model.misc import Hashable
from library.ui.color import ColorSchema
from library.ui.element._cfg import PageConfig
from library.ui.element._typ import OutputElement


class Element(Hashable):
    @property
    def require(self) -> set[Self]:
        """返回该元素所依赖的其他元素，将被自动添加到页面中"""
        return set()

    @abstractmethod
    def to_e(
        self, *args, schema: ColorSchema, dark: bool, page_cfg: PageConfig, **kwargs
    ) -> OutputElement:
        """
        生成 lxml.etree._Element 或 str 等可被 lxml.html.tostring() 处理的对象

        Args:
            schema: 颜色方案
            dark: 是否为暗色模式
            page_cfg: 页面配置

        Returns:
            可被 lxml.html.tostring() 处理的对象
        """
        pass
