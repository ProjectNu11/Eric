from pathlib import Path

from kayaku import config


@config("library.data_path")
class DataPathConfig:
    library: str = str(Path("data") / "library")
    """ 库数据目录 """

    module: str = str(Path("data") / "module")
    """ 模块数据目录 """

    shared: str = str(Path("data") / "shared")
    """ 共享数据目录 """

    temp: str = str(Path("data") / "temp")
    """ 临时文件目录 """


@config("library.path")
class PathConfig:
    """路径配置"""

    log: str = "log"
    """ 日志文件目录 """

    module: str = "module"
    """ 模块文件目录 """

    data: str = "data"
    """ 数据文件目录 """

    config: str = "config"
    """ 模块配置文件目录 """
