import json
import os
from hashlib import md5
from importlib import metadata
from json import JSONDecodeError
from pathlib import Path
from typing import TypedDict

from git import Repo
from loguru import logger
from packaging.version import Version


def get_version(raw: bool = False) -> str:
    _BASE_VERSION = "0.1.4"

    try:
        package_version = metadata.version("eric")
    except metadata.PackageNotFoundError:
        package_version = _BASE_VERSION

    if raw:
        return package_version

    if not ((git_path := Path.cwd() / ".git").exists() and git_path.is_dir()):
        return package_version
    if commit := next(Repo(Path.cwd()).iter_commits(), None):
        return f"{package_version}-{commit.hexsha[:7]}"
    return package_version


__version__: str = get_version()


class _EricLock(TypedDict):
    pdm_hash: str
    pyproject_hash: str
    eric_ver: str


def _pdm_lock(previous: str) -> str:
    lock = Path.cwd() / "pdm.lock"
    now = md5(lock.read_text().encode()).hexdigest()
    if previous != now:
        logger.warning("依赖锁已被修改，正在重新安装")
        os.system("pdm install")
        return now


def _pyproject_lock(previous: str) -> str:
    lock = Path.cwd() / "pyproject.toml"
    now = md5(lock.read_text().encode()).hexdigest()
    if previous != now:
        logger.warning("项目锁已被修改或不存在，正在重新安装")
        os.system("pdm install")
        return now


def _run_migrator():
    from library.migrate import run_migrators

    run_migrators(Version(get_version(raw=True)))


def _eric_lock():
    lock = Path.cwd() / ".eric-lock"
    try:
        old = json.loads(lock.read_text())
    except (FileNotFoundError, JSONDecodeError):
        old = {"pdm_hash": "", "pyproject_hash": "", "eric_ver": "0.1.0"}
    new: _EricLock = {
        "pdm_hash": _pdm_lock(old["pdm_hash"]),
        "pyproject_hash": _pyproject_lock(old["pyproject_hash"]),
        "eric_ver": get_version(raw=True),
    }
    _run_migrator()
    lock.write_text(json.dumps(new))


if __name__ == "library":  # 仅在被导入时执行
    _eric_lock()
