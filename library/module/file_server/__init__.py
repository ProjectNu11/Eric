import contextlib

from fastapi import HTTPException
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from graiax.fastapi.saya import route
from starlette.responses import FileResponse

from library.module.file_server.util import (
    file_exist,
    DATA_PATH,
    insert,
    cleanup,
    get_filename,
    file_registered,
)
from library.module.file_server.vars import ENTRYPOINT

channel = Channel.current()


@route.get(ENTRYPOINT)
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
