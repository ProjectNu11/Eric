from abc import ABC
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, add_creator, exists_module
from loguru import logger
from pydantic import AnyHttpUrl, BaseModel, validator
from typing_extensions import Self

from library.model.config.database import DatabaseConfig
from library.model.config.function import FunctionConfig
from library.model.config.path import PathConfig
from library.model.config.service import ServiceConfig

CONFIG_FILE_PATH: Path = Path("config.json")


class EricConfig(BaseModel):
    """Eric 配置"""

    __instance: Self = None

    name: str = "Eric"
    """ 机器人名称 """

    accounts: list[int] = []
    """ 机器人账号 """

    description: str = ""
    """ 机器人描述 """

    environment: str = ""
    """ 包管理器 """

    host: AnyHttpUrl = ""
    """ mirai-api-http 服务器地址 """

    verify_key: str = ""
    """ mirai-api-http 服务器验证密钥 """

    owners: list[int] = []
    """ 机器人所有者 """

    dev_groups: list[int] = []
    """ 机器人开发者群 """

    debug: bool = False
    """ 是否开启调试模式 """

    proxy: str = None
    """ 代理 """

    log_rotate: None | int = 7
    """ 日志文件保留天数 """

    path: PathConfig = PathConfig()
    """ 路径配置 """

    database: DatabaseConfig = DatabaseConfig()
    """ 数据库配置 """

    function: FunctionConfig = FunctionConfig()
    """ 功能配置 """

    service: ServiceConfig = ServiceConfig()
    """ 服务配置 """

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @staticmethod
    def from_file(path: str | Path = CONFIG_FILE_PATH) -> Self:
        """从文件加载配置"""
        if isinstance(path, str):
            path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        return EricConfig.parse_file(path, allow_pickle=True)

    def to_file(self, path: str | Path = CONFIG_FILE_PATH) -> None:
        """保存配置到文件"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.json(indent=4, ensure_ascii=False, exclude={"__instance"}))

    @validator("environment")
    def _validate_environment(cls, value: str) -> str:
        value = value.lower()
        if value in {"pip", "poetry"}:
            return value
        raise ValueError("仅支持 pip 和 poetry 两种包管理器")


class EricConfigClassCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.model.config.eric", "EricConfig"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.model.config.eric")

    @staticmethod
    def create(create_type: Type[EricConfig]) -> EricConfig:
        try:
            config = EricConfig().from_file()
        except FileNotFoundError:
            config = EricConfig()
            config.to_file()
            logger.warning("配置文件不存在，已创建默认配置文件")
            logger.warning("请修改配置文件后重启")
            exit(1)
        except JSONDecodeError:
            CONFIG_FILE_PATH.rename(
                CONFIG_FILE_PATH.with_suffix(
                    f".json.bak{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
            )
            config = EricConfig()
            config.to_file()
            logger.error("配置文件解析错误，请检查配置文件")
            logger.warning("已备份原配置文件并创建默认配置文件")
            exit(1)

        return config


add_creator(EricConfigClassCreator)
