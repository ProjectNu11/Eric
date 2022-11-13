from typing import Literal

from graiax.text2img.playwright.builtin import MarkdownToImg
from graiax.text2img.playwright.types import PageParams, ScreenshotParams


async def render_md(
    md: str,
    width: int = 840,
    height: int = 10,
    factor: float = 1.5,
    image_type: Literal["jpeg", "png"] = "jpeg",
    quality: int = 80,
):
    return await MarkdownToImg().render(
        md,
        page_params=PageParams(
            viewport={"width": width, "height": height}, device_scale_factor=factor
        ),
        screenshot_params=ScreenshotParams(
            type=image_type, quality=quality, scale="device"
        ),
    )
