from pathlib import Path

from creart import it
from fastapi import HTTPException
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.twilight import ElementMatch, Twilight, UnionMatch
from graia.saya import Channel
from graiax.fastapi.saya import route
from graiax.shortcut import decorate, dispatch, listen
from kayaku import create
from starlette import status
from starlette.responses import HTMLResponse

from library.decorator import Distribution, MentionMeOptional, Switch
from library.model.config import FastAPIConfig
from library.module.help.util.about import about_page
from library.module.help.util.module import (
    get_module_markdown,
    get_module_page,
    portal_page,
    search_category,
    search_module,
)
from library.module.help.vars import (
    CATEGORY_SEARCH_PAGE,
    MODULE_HELP_PAGE,
    MODULE_MARKDOWN_PAGE,
    MODULE_SEARCH_PAGE,
    PORTAL_PAGE,
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
    page = await about_page().render(local=True)
    await send_message(event, MessageChain(Image(data_bytes=page)), app.account)
    await send_message(
        event,
        MessageChain(f"您可以在这里查看详细帮助: {fastapi_config.link}{PORTAL_PAGE}"),
        app.account,
    )
