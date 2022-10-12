from json import JSONDecodeError

from loguru import logger

from library.model.config.eric import CONFIG_FILE_PATH, EricConfig

try:
    config = EricConfig().from_file()
except FileNotFoundError:
    config = EricConfig()
    config.to_file()
    logger.warning("配置文件不存在，已创建默认配置文件")
    logger.warning("请修改配置文件后重启")
    exit(1)
except JSONDecodeError:
    CONFIG_FILE_PATH.rename(CONFIG_FILE_PATH.with_suffix(".json.bak"))
    config = EricConfig()
    config.to_file()
    logger.error("配置文件解析错误，请检查配置文件")
    logger.warning("已备份原配置文件并创建默认配置文件")
    exit(1)

config.to_file()
