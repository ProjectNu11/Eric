from typing import Literal

from graiax.text2img.playwright import (
    HTMLRenderer,
    convert_md,
    PageOption,
    ScreenshotOption,
)


async def render_md(
    md: str,
    width: int = 840,
    height: int = 10,
    factor: float = 1.5,
    image_type: Literal["jpeg", "png"] = "jpeg",
    quality: int = 80,
):
    return await HTMLRenderer().render(
        convert_md(md),
        extra_page_option=PageOption(
            viewport={"width": width, "height": height}, device_scale_factor=factor
        ),
        extra_screenshot_option=ScreenshotOption(
            type=image_type, quality=quality, scale="device"
        ),
    )
