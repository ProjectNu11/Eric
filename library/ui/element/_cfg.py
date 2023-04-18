from dataclasses import dataclass


@dataclass
class PageConfig:
    """页面配置"""

    max_width: int
    """ 页面最大宽度 """

    dark: bool
    """ 是否为暗色模式 """

    border_radius: int
    """ 页面圆角 """

    title: str
    """ 页面标题 """

    fetch_on_render: bool
    """ 是否在渲染时获取图片 """

    local: bool
    """ 是否使用本地字体，如果为 True 则将无法在公网上正常显示 """

    additional_css: str
    """ 附加 CSS """

    auto_footer: bool
    """ 是否自动添加页脚 """
