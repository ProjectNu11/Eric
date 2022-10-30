import uuid
from datetime import datetime, timedelta
from hashlib import md5
from pathlib import Path
from typing import Generator, AsyncGenerator, Any

import aiofiles
from creart import it
from graia.saya import Channel
from kayaku import create
from loguru import logger
from sqlalchemy import select

from library.model.config.service.fastapi import FastAPIConfig
from library.module.file_server.table import FileServer
from library.module.file_server.vars import ENTRYPOINT
from library.util.module import Modules
from library.util.orm import orm

channel = Channel.current()

DATA_PATH = it(Modules).get(channel.module).data_path
DEFAULT_LIFESPAN = 60 * 60 * 24 * 7


async def _serve_file_keep_original(file: Path, file_id: str) -> str:
    logger.debug(f"[FileServer] 正在复制文件 -> {file_id}")
    async with aiofiles.open(file, "rb") as f:
        async with aiofiles.open(Path(DATA_PATH, file_id), "ab") as out:
            while chunk := await f.read(10 * 1024 * 1024):
                await out.write(chunk)
    return file_id


async def _get_hash_by_path(file: Path) -> str:
    async with aiofiles.open(file, "rb") as f:
        return md5(await f.read()).hexdigest()


async def _serve_file_by_path(
    file: Path, file_id: str, keep_original: bool
) -> tuple[str, str]:
    hashed = await _get_hash_by_path(file)
    if f := await compare_hash(hashed):
        raise FileExistsError(f)
    if keep_original:
        return await _serve_file_keep_original(file, file_id), hashed
    logger.debug(f"[FileServer] 正在移动文件 -> {file_id}")
    file.rename(Path(DATA_PATH, file_id))
    return file_id, hashed


async def compare_hash(hashed: str) -> str | None:
    return (
        result[0]
        if (
            result := await orm.fetchone(
                select(FileServer.uuid).where(FileServer.hash == hashed)
            )
        )
        else None
    )


async def _serve_file_by_bytes(
    file: bytes | Generator[bytes, None, None] | AsyncGenerator[bytes, None],
    file_id: str,
) -> tuple[str, str]:
    logger.debug(f"[FileServer] 正在写入文件 -> {file_id}")
    async with aiofiles.open((fp := Path(DATA_PATH, file_id)), "ab") as out:
        if isinstance(file, bytes):
            await out.write(file)
            hashed = md5(file).hexdigest()
        elif isinstance(file, Generator):
            for chunk in file:
                await out.write(chunk)
            hashed = _get_hash_by_path(fp)
        else:
            async for chunk in file:
                await out.write(chunk)
            hashed = _get_hash_by_path(fp)
    return file_id, hashed


async def insert(
    file_id: str, file_name: str, serve_time: datetime, lifespan: int, hash_value: str
):
    await orm.add(
        FileServer,
        time=serve_time,
        uuid=file_id,
        filename=file_name,
        lifespan=lifespan,
        hash=hash_value,
    )


def ensure_unlink(file: Path):
    while file.is_file():
        file.unlink()


async def delete_file(file_id: str):
    file = Path(DATA_PATH, file_id)
    ensure_unlink(file)
    await deactivate_file(file_id)


async def deactivate_file(file_id: str):
    if await file_registered(file_id):
        await orm.insert_or_update(
            FileServer, [FileServer.uuid == file_id], available=False
        )


async def renew_file_lifespan(file_id: str, lifespan: int):
    if await file_registered(file_id):
        await orm.insert_or_update(
            FileServer,
            [FileServer.uuid == file_id],
            time=datetime.now(),
            lifespan=lifespan,
        )


async def _write(
    file: bytes | Generator[bytes, None, None] | AsyncGenerator[bytes, None] | Path,
    file_id: str,
    keep_original: bool,
) -> tuple[str, str]:
    if isinstance(file, Path) and file.is_file():
        return await _serve_file_by_path(file, file_id, keep_original)
    return await _serve_file_by_bytes(file, file_id)


async def get_uuid() -> str:
    file_id = str(uuid.uuid4())
    while file_exist(file_id) or await file_registered(file_id):
        file_id = str(uuid.uuid4())
    return file_id


async def serve_file(
    file: bytes | Generator[bytes, None, None] | AsyncGenerator[bytes, None] | Path,
    file_name: str,
    lifespan: int = DEFAULT_LIFESPAN,
    *,
    keep_original: bool = True,
) -> str | None:
    file_id = await get_uuid()
    try:
        _, hashed = await _write(file, file_id, keep_original)
        await insert(file_id, file_name, datetime.now(), lifespan, hashed)
        return file_id
    except FileExistsError as err:
        logger.warning(f"[FileServer] 文件已存在 -> {err.args[0]}")
        await delete_file(file_id)
        await renew_file_lifespan(err.args[0], lifespan)
        return err.args[0]
    except Exception as err:
        logger.error(f"[FileServer] 保存文件时发生错误 -> {err}")
        await delete_file(file_id)
        logger.debug(f"[FileServer] 已回滚文件 -> {file_id}")
        return


def file_exist(file_id: str) -> bool:
    return Path(DATA_PATH, file_id).is_file()


async def file_registered(file_id: str) -> bool:
    return bool(
        await orm.fetchone(select(FileServer).where(FileServer.uuid == file_id))
    )


async def get_filename(file_id: str) -> str:
    return (
        await orm.fetchone(
            select(FileServer.filename).where(FileServer.uuid == file_id)
        )
    )[0]


async def _cleanup_outdated_files():
    logger.debug("[FileServer] 正在清理过期文件")
    outdated = 0
    if files := await orm.all(
        select(FileServer.uuid, FileServer.time, FileServer.lifespan).where(
            FileServer.available
        )
    ):
        for file in [
            file_id
            for file_id, serve_time, lifespan in files
            if datetime.now() - serve_time > timedelta(seconds=lifespan)
        ]:
            outdated += 1
            await delete_file(file)
    if outdated:
        logger.debug(f"[FileServer] 已清理过期文件 {outdated} 个")


async def _cleanup_invalid_files():
    logger.debug("[FileServer] 正在清理无效文件")
    invalid = 0
    for file in Path(DATA_PATH).iterdir():
        if not file.is_file():
            continue
        if not await orm.fetchone(
            select(FileServer.uuid).where(FileServer.uuid == file.name)
        ):
            ensure_unlink(file)
            invalid += 1
        elif await orm.fetchone(
            select(FileServer.uuid).where(
                not FileServer.available, FileServer.uuid == file.name
            )
        ):
            ensure_unlink(file)
            invalid += 1
    if invalid:
        logger.debug(f"[FileServer] 已清理无效文件 {invalid} 个")


async def cleanup():
    await _cleanup_outdated_files()
    await _cleanup_invalid_files()


def get_link(file_id: str) -> str:
    fastapi_cfg: FastAPIConfig = create(FastAPIConfig)
    return f"{fastapi_cfg.link}{ENTRYPOINT.format(file_id=file_id)}"
