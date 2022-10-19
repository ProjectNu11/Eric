from dataclasses import field

from kayaku import config


@config("library.service.manager")
class ManagerConfig:
    """管理配置"""

    plugin_repo: list[str] = field(default_factory=list)
    """ 插件仓库 """
