from script.lock import eric_lock
from script.version import get_version

__version__: str = get_version()

if __name__ == "library":  # 仅在被导入时执行
    eric_lock()
