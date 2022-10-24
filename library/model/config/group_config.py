from abc import ABC
from json import JSONDecodeError
from pathlib import Path
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module, it
from kayaku import create
from pydantic import BaseModel, ValidationError
from typing_extensions import Self

from library.model.config.function import FunctionConfig
from library.model.config.path import PathConfig
from library.model.module import ModuleMetadata
from library.util.module import Modules

func_cfg: FunctionConfig = create(FunctionConfig)
path_cfg: PathConfig = create(PathConfig)
CONFIG_PATH = Path(path_cfg.config) / "group_config"
CONFIG_PATH.mkdir(parents=True, exist_ok=True)


class GroupSwitch(BaseModel):
    value: dict[str, bool] = {}
    """开关值"""

    default: bool = func_cfg.default
    """默认开关值"""

    def get(self, module: str | ModuleMetadata) -> bool:
        """获取开关值"""
        if isinstance(module, str):
            module = it(Modules).get(module)
        if module.advanced.enable_by_default:
            return True
        return self.value.get(module.pack, self.default)

    def update(self, module: str | ModuleMetadata, value: bool):
        """更新开关值"""
        if isinstance(module, str):
            module = it(Modules).get(module)
        if module.advanced.allow_disable or value:
            self.value[module.pack] = value
        else:
            raise NotImplementedError(f"模块 {module.pack} 不允许被禁用")

    def set_default(self, value: bool):
        """设置默认开关值"""
        self.default = value

    def save(self, group_id: int):
        """保存开关值"""
        path = CONFIG_PATH / str(group_id)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "switch.json").open("w", encoding="utf-8") as f:
            f.write(self.json(indent=4, ensure_ascii=False))

    @classmethod
    def load(cls, group_id: int) -> Self:
        """加载开关值"""
        path = CONFIG_PATH / str(group_id) / "switch.json"
        try:
            return cls.parse_file(path)
        except (FileNotFoundError, ValidationError, JSONDecodeError):
            return cls()


class GroupConfig(BaseModel):
    switch: dict[int, GroupSwitch] = {}
    """开关配置"""

    groups: set[int] = set()

    def get_switch(self, group: int) -> GroupSwitch:
        """获取开关"""
        if not (switch := self.switch.get(group)):
            switch = GroupSwitch()
            self.switch[group] = switch
        return switch

    def save(self):
        """保存配置"""
        with (CONFIG_PATH / "data.json").open("w", encoding="utf-8") as f:
            f.write(self.json(indent=4, ensure_ascii=False, include={"groups"}))
        for group in self.switch:
            self.switch[group].save(group)

    def load(self):
        """加载配置"""
        groups: set[int] = set()
        for file in CONFIG_PATH.iterdir():
            if (
                file.is_dir()
                and file.name.isdigit()
                and (file / "switch.json").is_file()
            ):
                groups.add(int(file.name))
        self.groups = groups
        for group in self.groups:
            self.switch[group] = GroupSwitch.load(group)


class GroupConfigCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.model.config.group_config", "GroupConfig"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.config.group_config")

    @staticmethod
    def create(_create_type: Type[GroupConfig]) -> GroupConfig:
        cfg = GroupConfig()
        cfg.load()
        return cfg
