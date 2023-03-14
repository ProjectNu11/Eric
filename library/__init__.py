from datetime import datetime

__launch_time__: datetime = datetime.now()


def get_version() -> str:
    _BASE_VERSION = "0.1.0"
    from importlib import metadata

    try:
        package_version = metadata.version("eric")
    except metadata.PackageNotFoundError:
        package_version = _BASE_VERSION

    from pathlib import Path

    from git import Repo

    if not ((git_path := Path.cwd() / ".git").exists() and git_path.is_dir()):
        return package_version
    if commit := next(Repo(Path.cwd()).iter_commits(), None):
        return f"{package_version}-{commit.hexsha[:7]}"
    return package_version


__version__: str = get_version()
