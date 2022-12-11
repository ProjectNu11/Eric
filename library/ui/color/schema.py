import re

from pydantic import BaseModel, Field
from typing_extensions import Self


class ColorSingle(BaseModel):
    color: tuple[int, int, int] | tuple[int, int, int, float]

    @property
    def has_alpha(self) -> bool:
        return len(self.color) == 4

    def hex(self) -> str:
        if self.has_alpha:
            return (
                f"#{''.join(f'{int(c * self.color[3]):02X}' for c in self.color[:3])}"
            )
        return f"#{''.join(f'{int(c):02X}' for c in self.color)}"

    def rgb(self) -> str:
        return f"{'rgba' if self.has_alpha else 'rgb'}{self.color}"

    def add_alpha(self, alpha: float) -> Self:
        return ColorSingle(color=self.color[:3] + (alpha,))

    def remove_alpha(self) -> Self:
        return ColorSingle(color=self.color[:3])

    @classmethod
    def from_hex(cls, value: str) -> Self:
        value = value.lstrip("#")
        assert re.match(r"^[\dA-Fa-f]{6}$", value), f"Invalid hex value: {value}"
        return cls(color=(int(value[:2], 16), int(value[2:4], 16), int(value[4:6], 16)))


class ColorPair(BaseModel):
    light: ColorSingle
    dark: ColorSingle

    def get(self, dark: bool, alpha: float = 1.0) -> ColorSingle:
        assert 0.0 <= alpha <= 1.0, "Invalid value for alpha"
        color = self.dark if dark else self.light
        return color if float == 1.0 else color.add_alpha(alpha)

    def hex(self, dark: bool, alpha: float = 1.0) -> str:
        return self.get(dark, alpha).hex()

    def rgb(self, dark: bool, alpha: float = 1.0) -> str:
        return self.get(dark, alpha).rgb()

    class Config:
        allow_mutation = False


class ColorSchema(BaseModel):
    """配色方案"""

    TEXT: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(37, 37, 37))),
            dark=(ColorSingle(color=(250, 250, 250))),
        ),
        alias="text",
    )
    """ 文本颜色 """

    DESCRIPTION: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(140, 140, 140))),
            dark=(ColorSingle(color=(204, 204, 204))),
        ),
        alias="description",
    )
    """ 描述颜色 """

    SECONDARY_DESCRIPTION: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(156, 156, 156))),
            dark=(ColorSingle(color=(99, 99, 99))),
        ),
        alias="secondary_description",
    )
    """ 次要描述颜色 """

    FOREGROUND: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(252, 252, 252))),
            dark=(ColorSingle(color=(23, 23, 23))),
        ),
        alias="foreground",
    )
    """ 前景色 """

    BACKGROUND: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(246, 246, 246))),
            dark=(ColorSingle(color=(1, 1, 1))),
        ),
        alias="background",
    )
    """ 背景色 """

    LINE: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(232, 232, 232))),
            dark=(ColorSingle(color=(58, 58, 58))),
        ),
        alias="line",
    )
    """ 分割线颜色 """

    HINT: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(231, 238, 244))),
            dark=(ColorSingle(color=(0, 43, 78))),
        ),
        alias="hint",
    )
    """ 提示颜色 """

    HIGHLIGHT: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(0, 114, 221))),
            dark=(ColorSingle(color=(67, 144, 245))),
        ),
        alias="highlight",
    )
    """ 高亮颜色 """

    SECONDARY_HIGHLIGHT: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(235, 235, 235))),
            dark=(ColorSingle(color=(59, 59, 59))),
        ),
        alias="secondary_highlight",
    )
    """ 次要高亮颜色 """

    SWITCH_ENABLE: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(4, 129, 255))),
            dark=(ColorSingle(color=(4, 129, 255))),
        ),
        alias="switch_enable",
    )
    """ 开关开启颜色 """

    SWITCH_DISABLE: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(153, 153, 153))),
            dark=(ColorSingle(color=(101, 102, 96))),
        ),
        alias="switch_disable",
    )
    """ 开关关闭颜色 """

    HYPERLINK: ColorPair = Field(
        default=ColorPair(
            light=(ColorSingle(color=(0, 114, 221))),
            dark=(ColorSingle(color=(67, 144, 245))),
        ),
        alias="hyperlink",
    )
    """ 超链接颜色 """
