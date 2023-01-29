import io
import math
from enum import Enum

from PIL import Image

from library.ui import ColorPair, ColorSchema, ColorSingle
from library.ui.color.schema import ColorType


class _ColorMagicNumbers(Enum):
    """Magic Numbers for Palette Calculations"""

    TOO_DARK: int = 120
    DARK: int = 192
    MEDIUM_LEFT: int = 256
    MEDIUM_RIGHT: int = 512
    LIGHT: int = 3 * 255 - 192
    TOO_LIGHT: int = 3 * 255 - 120
    MONO: int = 16
    SIMILAR: int = 100


class _ColorMagicBase(Enum):
    """Magic Base Definitions for Palette Calculations"""

    BACK_LIGHT: tuple[int, int, int] = (246, 246, 246)
    BACK_DARK: tuple[int, int, int] = (1, 1, 1)

    FORE_LIGHT: tuple[int, int, int] = (252, 252, 252)
    FORE_DARK: tuple[int, int, int] = (23, 23, 23)

    HINT_LIGHT: tuple[int, int, int] = (252, 252, 252)
    HINT_DARK: tuple[int, int, int] = (23, 23, 23)

    HYPERLINK_LIGHT: tuple[int, int, int] = (0, 0, 0)
    HYPERLINK_DARK: tuple[int, int, int] = (0, 0, 0)

    SWITCH_LIGHT: tuple[int, int, int] = (0, 0, 0)
    SWITCH_DARK: tuple[int, int, int] = (0, 0, 0)

    MEDIUM: tuple[int, int, int] = (128, 128, 128)
    SLIGHTLY_LIGHT: tuple[int, int, int] = (192, 192, 192)
    SLIGHTLY_DARK: tuple[int, int, int] = (64, 64, 64)


class _ColorMagicOpacity(Enum):
    """Magic Opacity Definitions for Palette Calculations"""

    BACK: float = 0.1
    FORE: float = 0.05
    HINT: float = 0.5
    COMMON: float = 0.8
    HYPERLINK: float = 1.0
    SWITCH: float = 1.0


class ColorPalette:
    @staticmethod
    def _mix_color_base_non_alpha(base: ColorSingle, front: ColorSingle) -> ColorSingle:
        alpha = front.alpha
        return ColorSingle(
            color=(
                tuple(
                    map(
                        lambda x: int(x[0] * (1 - alpha) + x[1] * alpha),
                        zip(base.color[:3], front.color[:3]),
                    )
                )
            )
        )

    @staticmethod
    def _mix_color_base_alpha(base: ColorSingle, front: ColorSingle) -> ColorSingle:
        a1 = base.alpha
        a2 = front.alpha
        alpha = a1 + a2 * (1 - a1)
        return ColorSingle(
            color=(
                tuple(
                    map(
                        lambda x: int(x[0] * a1 + x[1] * a2 * (1 - a1)),
                        zip(base.color[:3], front.color[:3]),
                    )
                )
                + (alpha,)
            )
        )

    @classmethod
    def mix_color(cls, base: ColorType, front: ColorType) -> ColorSingle:
        base = base if isinstance(base, ColorSingle) else ColorSingle(color=base)
        front = front if isinstance(front, ColorSingle) else ColorSingle(color=front)
        if base.has_alpha:
            return cls._mix_color_base_alpha(base, front)
        return cls._mix_color_base_non_alpha(base, front)

    @classmethod
    def get_dominant_colors(
        cls, image: Image.Image, size: int = 5
    ) -> list[tuple[int, int, int]]:

        # Snippets from SAGIRI-kawaii/SAGIRI-BOT
        result = image.convert("P", palette=Image.ADAPTIVE, colors=size)

        palette = result.getpalette()
        color_counts = sorted(result.getcolors(), reverse=True)
        colors = []

        for i in range(size):
            palette_index = color_counts[i][1]
            dominant_color = palette[palette_index * 3 : palette_index * 3 + 3]
            colors.append(tuple(dominant_color))

        return colors

    @staticmethod
    def assert_color(color: tuple[int, int, int]):
        assert (
            0 <= sum(color) <= 3 * 255
            and min(color) >= 0
            and max(color) <= 255
            and len(color) == 3
        )

    @classmethod
    def is_too_dark(cls, color: tuple[int, int, int]) -> bool:
        cls.assert_color(color)
        return sum(color) < _ColorMagicNumbers.TOO_DARK.value

    @classmethod
    def is_dark(cls, color: tuple[int, int, int]) -> bool:
        cls.assert_color(color)
        return sum(color) < _ColorMagicNumbers.DARK.value

    @classmethod
    def is_too_light(cls, color: tuple[int, int, int]) -> bool:
        cls.assert_color(color)
        return sum(color) > _ColorMagicNumbers.TOO_LIGHT.value

    @classmethod
    def is_light(cls, color: tuple[int, int, int]) -> bool:
        cls.assert_color(color)
        return sum(color) > _ColorMagicNumbers.LIGHT.value

    @classmethod
    def is_medium(cls, color: tuple[int, int, int]) -> bool:
        cls.assert_color(color)
        return (
            _ColorMagicNumbers.MEDIUM_LEFT.value
            < sum(color)
            < _ColorMagicNumbers.MEDIUM_RIGHT.value
        )

    @classmethod
    def is_too_mono(cls, color: tuple[int, int, int]) -> bool:
        cls.assert_color(color)
        return max(color) - min(color) < _ColorMagicNumbers.MONO.value

    @classmethod
    def is_unique(
        cls, color1: tuple[int, int, int], color2: tuple[int, int, int]
    ) -> bool:
        distance = math.sqrt(
            (color1[0] - color2[0]) ** 2
            + (color1[1] - color2[1]) ** 2
            + (color1[2] - color2[2]) ** 2
        )
        return distance > _ColorMagicNumbers.SIMILAR.value

    @classmethod
    def _parse_dominant(
        cls, img: bytes, sample_size: int
    ) -> tuple[ColorSingle, ColorSingle]:
        img = Image.open(io.BytesIO(img))
        colors = cls.get_dominant_colors(img, sample_size)
        original = colors.copy()
        colors = [
            c for c in original if not cls.is_too_dark(c) and not cls.is_too_light(c)
        ]
        assert colors, "Too few colors"
        dominant = colors[0]
        if len(colors) == 1:
            return ColorSingle(color=dominant), ColorSingle(color=dominant)
        sub_dominant = colors[1]
        deck = colors[2:]
        while deck:
            sub_dominant = deck.pop()
            if cls.is_unique(dominant, sub_dominant):
                break
        return ColorSingle(color=dominant), ColorSingle(color=sub_dominant)

    @classmethod
    def _generate_bg_color_pair(cls, front: ColorSingle) -> ColorPair:
        base_light = _ColorMagicBase.BACK_LIGHT.value
        base_dark = _ColorMagicBase.BACK_DARK.value
        front = front.with_alpha(_ColorMagicOpacity.BACK.value)
        return ColorPair(
            light=cls.mix_color(base_light, front),
            dark=cls.mix_color(base_dark, front),
        )

    @classmethod
    def _generate_fg_color_pair(cls, front: ColorSingle) -> ColorPair:
        base_light = _ColorMagicBase.FORE_LIGHT.value
        base_dark = _ColorMagicBase.FORE_DARK.value
        front = front.with_alpha(_ColorMagicOpacity.FORE.value)
        return ColorPair(
            light=cls.mix_color(base_light, front),
            dark=cls.mix_color(base_dark, front),
        )

    @classmethod
    def _generate_hint_color_pair(cls, front: ColorSingle) -> ColorPair:
        base_light = _ColorMagicBase.HINT_LIGHT.value
        base_dark = _ColorMagicBase.HINT_DARK.value
        front = front.with_alpha(_ColorMagicOpacity.HINT.value)
        return ColorPair(
            light=cls.mix_color(base_light, front),
            dark=cls.mix_color(base_dark, front),
        )

    @classmethod
    def _generate_colored_text_color_pair(cls, front: ColorSingle) -> ColorPair:
        base_light = _ColorMagicBase.FORE_DARK.value
        base_dark = _ColorMagicBase.BACK_LIGHT.value
        front = front.with_alpha(_ColorMagicOpacity.COMMON.value)
        return ColorPair(
            light=cls.mix_color(base_light, front),
            dark=cls.mix_color(base_dark, front),
        )

    @classmethod
    def _generate_hyperlink_color_pair(cls, front: ColorSingle) -> ColorPair:
        base_light = _ColorMagicBase.HYPERLINK_LIGHT.value
        base_dark = _ColorMagicBase.HYPERLINK_DARK.value
        front = front.with_alpha(_ColorMagicOpacity.HYPERLINK.value)
        return ColorPair(
            light=cls.mix_color(base_light, front),
            dark=cls.mix_color(base_dark, front),
        )

    @classmethod
    def _generate_switch_color_pair(cls, front: ColorSingle) -> ColorPair:
        base_light = _ColorMagicBase.SWITCH_LIGHT.value
        base_dark = _ColorMagicBase.SWITCH_DARK.value
        front = front.with_alpha(_ColorMagicOpacity.SWITCH.value)
        return ColorPair(
            light=cls.mix_color(base_light, front),
            dark=cls.mix_color(base_dark, front),
        )

    @classmethod
    def _generate_secondary_highlight_color_pair(cls, front: ColorSingle) -> ColorPair:
        base_light = _ColorMagicBase.SLIGHTLY_LIGHT.value
        base_dark = _ColorMagicBase.SLIGHTLY_DARK.value
        front = front.with_alpha(_ColorMagicOpacity.FORE.value)
        return ColorPair(
            light=cls.mix_color(base_light, front),
            dark=cls.mix_color(base_dark, front),
        )

    @classmethod
    def generate_schema(cls, img: bytes, sample_size: int = 10) -> ColorSchema:
        dominant, sub_dom = cls._parse_dominant(img, sample_size)
        return ColorSchema(
            foreground=cls._generate_fg_color_pair(dominant.copy()),
            background=cls._generate_bg_color_pair(dominant.copy()),
            hint=cls._generate_hint_color_pair(dominant.copy()),
            colored_text=cls._generate_colored_text_color_pair(dominant.copy()),
            highlight=cls._generate_hyperlink_color_pair(sub_dom.copy()),
            hyperlink=cls._generate_hyperlink_color_pair(sub_dom.copy()),
            switch_enable=cls._generate_switch_color_pair(sub_dom.copy()),
            secondary_highlight=cls._generate_secondary_highlight_color_pair(
                sub_dom.copy()
            ),
        )
