from pathlib import Path

from pydantic import BaseModel, validator


class DataPathConfig(BaseModel):
    """数据路径配置"""

    data: Path = Path("data")
    """ 数据文件目录 """

    library: Path = data / "library"
    """ 库数据目录 """

    module: Path = data / "module"
    """ 模块数据目录 """

    temp: Path = data / "temp"
    """ 临时文件目录 """

    @validator("data", "library", "module", "temp")
    def _data_path_config_mkdir(cls, path: Path) -> Path:
        if not path.exists():
            path.mkdir(parents=True)
        return path


class PathConfig(BaseModel):
    """路径配置"""

    data: DataPathConfig = DataPathConfig()
    """ 数据目录 """

    log: Path = Path("log")
    """ 日志文件目录 """

    module: Path = Path("module")
    """ 模块文件目录 """

    @validator("log", "module")
    def _path_config_mkdir(cls, path: Path) -> Path:
        if not path.exists():
            path.mkdir(parents=True)
        return path
