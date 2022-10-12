import re
from pathlib import Path

from pydantic import BaseModel, validator

from library.config import config


class ModuleMetadata(BaseModel):
    """模块元数据"""

    name: str
    """ 模块名称 """

    version: str
    """ 模块版本 """

    pack: str
    """ 模块包名 """

    authors: list[str]
    """ 模块作者 """

    description: str
    """ 模块描述 """

    icon: None | str = None
    """ 模块图标 """

    category: list[str] = []
    """ 模块分类 """

    @validator("version")
    def _module_version_validator(cls, version: str):
        """模块版本验证器"""
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            raise ValueError("版本号不符合规范")
        return version

    @property
    def clean_name(self) -> str:
        """模块名称（去除前缀）"""
        return self.name.split(".", maxsplit=1)[-1]

    @property
    def data_path(self) -> Path:
        """模块数据目录"""
        _data_path = config.path.data.module / self.pack
        if not _data_path.exists():
            _data_path.mkdir(parents=True)
        return _data_path

    @property
    def config_path(self) -> Path:
        """模块配置文件目录"""
        return config.path.data.module / self.pack
