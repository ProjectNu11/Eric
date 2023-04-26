from importlib import metadata
from pathlib import Path

from git import Repo


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
