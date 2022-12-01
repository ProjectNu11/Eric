from pathlib import Path

from creart import it
from fastapi import HTTPException
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import Twilight, UnionMatch, ElementMatch
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Channel
from graiax.fastapi.saya import route
from kayaku import create
from starlette import status
from starlette.responses import HTMLResponse

from library.decorator.distribute import Distribution
from library.decorator.mention import MentionMeOptional
from library.decorator.switch import Switch
from library.model.config.service.fastapi import FastAPIConfig
from library.module.help.util.module import (
    portal_page,
    get_module_page,
    get_module_markdown,
    search_module,
    search_category,
)
from library.module.help.vars import (
    PORTAL_PAGE,
    MODULE_HELP_PAGE,
    MODULE_MARKDOWN_PAGE,
    MODULE_SEARCH_PAGE,
    CATEGORY_SEARCH_PAGE,
)
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.module import Modules

channel = Channel.current()


@route.get(PORTAL_PAGE)
async def help_portal():
    return HTMLResponse(portal_page().to_html(), status_code=status.HTTP_200_OK)


@route.get(MODULE_HELP_PAGE)
async def module_help(pack: str):
    if not (module := it(Modules).get(pack)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Module {pack} not found."
        )
    return HTMLResponse(
        get_module_page(module).to_html(), status_code=status.HTTP_200_OK
    )


@route.get(MODULE_MARKDOWN_PAGE)
async def module_markdown(pack: str, file: str):
    if not file.endswith(".md"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be markdown file.",
        )
    if not (module := it(Modules).get(pack)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Module {pack} not found."
        )
    if not (Path(*module.pack.split(".")) / file).is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"File {file} not found."
        )
    return HTMLResponse(
        get_module_markdown(module, file), status_code=status.HTTP_200_OK
    )


@route.get(MODULE_SEARCH_PAGE)
async def module_search(keyword: str):
    return HTMLResponse(
        search_module(keyword).to_html(), status_code=status.HTTP_200_OK
    )


@route.get(CATEGORY_SEARCH_PAGE)
async def category_search(category: str):
    print(category)
    return HTMLResponse(
        search_category(category).to_html(), status_code=status.HTTP_200_OK
    )


@listen(GroupMessage, FriendMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True),
        PrefixMatch(optional=True),
        UnionMatch("帮助", "help"),
    )
)
@decorate(
    MentionMeOptional.check(), Switch.check(channel.module), Distribution.distribute()
)
async def help_handler(app: Ariadne, event: MessageEvent):
    fastapi_config: FastAPIConfig = create(FastAPIConfig)
    page = await portal_page().render()
    await send_message(event, MessageChain(Image(data_bytes=page)), app.account)
    await send_message(
        event,
        MessageChain(f"您也可以在这里查看详细帮助: {fastapi_config.link}{PORTAL_PAGE}"),
        app.account,
    )
