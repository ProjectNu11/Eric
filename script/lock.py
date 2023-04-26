import json
import os
from hashlib import md5
from json import JSONDecodeError
from pathlib import Path
from typing import TypedDict

from loguru import logger
from packaging.version import Version

from script.migrate import run_migrators
from script.version import get_version


class EricLock(TypedDict):
    pdm_hash: str
    pyproject_hash: str
    eric_ver: str


def pdm_lock(previous: str) -> str:
    lock = Path.cwd() / "pdm.lock"
    now = md5(lock.read_text().encode()).hexdigest()
    if previous != now:
        logger.warning("依赖锁已被修改，正在重新安装")
        os.system("pdm install")
        return now
    return now


def pyproject_lock(previous: str) -> str:
    lock = Path.cwd() / "pyproject.toml"
    now = md5(lock.read_text().encode()).hexdigest()
    if previous != now:
        logger.warning("项目锁已被修改或不存在，正在重新安装")
        os.system("pdm install")
        return now
    return now


def eric_lock():
    lock = Path.cwd() / ".eric-lock"
    try:
        old = json.loads(lock.read_text())
    except (FileNotFoundError, JSONDecodeError):
        old = {"pdm_hash": "", "pyproject_hash": "", "eric_ver": ""}
    new: EricLock = {
        "pdm_hash": pdm_lock(old["pdm_hash"]),
        "pyproject_hash": pyproject_lock(old["pyproject_hash"]),
        "eric_ver": (ver := get_version(raw=True)),
    }
    run_migrators(Version(ver))
    lock.write_text(json.dumps(new))
