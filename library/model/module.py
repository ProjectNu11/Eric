import re
from pathlib import Path

from kayaku import create
from pydantic import BaseModel, validator

from library.model.config import DataPathConfig, FunctionConfig, PathConfig


class ModuleAdvancedSetting(BaseModel):
    """模块高级设置"""

    enable_by_default: bool = create(FunctionConfig).default
    """默认启用"""

    allow_disable: bool = True
    """允许禁用"""

    allow_unload: bool = True
    """允许卸载"""

    hidden: bool = False
    """隐藏模块"""


class ModuleMetadata(BaseModel):
    """模块元数据"""

    name: str
    """ 模块名称 """

    version: str = "0.1.0"
    """ 模块版本 """

    pack: str
    """ 模块包名 """

    authors: list[str] = []
    """ 模块作者 """

    required: list[str] = []
    """ 模块依赖 """

    description: str = ""
    """ 模块描述 """

    category: list[str] = []
    """ 模块分类 """

    advanced: ModuleAdvancedSetting = ModuleAdvancedSetting()
    """ 模块高级设置 """

    def __hash__(self):
        return hash(f"_ModuleMetadata:{self.pack}")

    @validator("version")
    def _module_version_validator(cls, version: str):  # noqa
        """模块版本验证器"""
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            raise ValueError("版本号不符合规范")
        return version

    @property
    def clean_name(self) -> str:
        """模块名称（去除前缀）"""
        return self.pack.split(".")[-1]

    @property
    def data_path(self) -> Path:
        """模块数据目录"""
        config: DataPathConfig = create(DataPathConfig)
        _data_path = Path(config.module) / self.pack
        if not _data_path.exists():
            _data_path.mkdir(parents=True)
        return _data_path

    @property
    def config_path(self) -> Path:
        """模块配置文件目录"""
        config: PathConfig = create(PathConfig)
        _config_path = Path(config.config) / "module" / self.pack
        if not _config_path.exists():
            _config_path.mkdir(parents=True)
        return _config_path


class Module(ModuleMetadata):
    """模块"""

    loaded: bool
    """是否已加载"""

    def __hash__(self):
        return hash(f"_Module:{self.pack}")
