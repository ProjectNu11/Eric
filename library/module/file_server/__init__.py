import contextlib
from pathlib import Path

from creart import it
from fastapi import HTTPException
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from graiax.fastapi.saya import route
from starlette import status
from starlette.responses import FileResponse

from library.module.file_server.util import (
    file_exist,
    DATA_PATH,
    insert,
    cleanup,
    get_filename,
    file_registered,
)
from library.module.file_server.vars import (
    FILE_ENTRYPOINT,
    LIB_ASSETS_ENTRYPOINT,
    MODULE_ASSETS_ENTRYPOINT,
    LIB_ASSETS_DIR,
)
from library.util.module import Modules

channel = Channel.current()


@route.get(FILE_ENTRYPOINT)
async def get_file(file_id: str):
    if not file_exist(file_id) or not await file_registered(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    filename = await get_filename(file_id)
    if filename.endswith(".html") or filename.endswith(".htm"):
        return FileResponse(DATA_PATH / file_id, media_type="text/html")
    return FileResponse(DATA_PATH / file_id, filename=await get_filename(file_id))


@channel.use(SchedulerSchema(timers.every_minute()))
async def scheduled_cleanup():
    with contextlib.suppress(Exception):
        await cleanup()


@route.get(LIB_ASSETS_ENTRYPOINT)
async def library_assets(file: str):
    if (file := LIB_ASSETS_DIR / file).exists():
        return FileResponse(file)
    raise HTTPException(status_code=404, detail="File not found")


@route.get(MODULE_ASSETS_ENTRYPOINT)
async def module_assets(module: str, file: str):
    if not it(Modules).get(module):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Module {module} not found"
        )
    path = Path(*module.split("."), file)
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {module}/{file} not found",
        )
    return FileResponse(path, filename=path.name)
