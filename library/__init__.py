import os
from hashlib import md5
from importlib import metadata
from pathlib import Path

from git import Repo
from loguru import logger


def get_version() -> str:
    _BASE_VERSION = "0.1.0"

    try:
        package_version = metadata.version("eric")
    except metadata.PackageNotFoundError:
        package_version = _BASE_VERSION

    if not ((git_path := Path.cwd() / ".git").exists() and git_path.is_dir()):
        return package_version
    if commit := next(Repo(Path.cwd()).iter_commits(), None):
        return f"{package_version}-{commit.hexsha[:7]}"
    return package_version


__version__: str = get_version()


def compare_lock():
    lock = Path.cwd() / "pdm.lock"
    now = md5(lock.read_text().encode()).hexdigest()
    hashed = Path.cwd() / ".lock-hash"
    if not hashed.exists():
        logger.warning("未找到锁文件哈希，正在重新安装并创建")
        os.system("pdm install")
        hashed.write_text(now)
        return
    elif hashed.read_text() != now:
        logger.warning("锁文件已被修改，正在重新安装")
        os.system("pdm install")
        hashed.write_text(now)
        return


if __name__ == "library":  # 仅在被导入时执行
    compare_lock()
