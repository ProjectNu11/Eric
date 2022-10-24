from dataclasses import field

from kayaku import config


@config("library.service.manager")
class ManagerConfig:
    """管理配置"""

    plugin_repo: list[str] = field(default_factory=list)
    """
    插件仓库，绝大多数情况下不需要手动配置

    格式：
        Github: `github$<owner>/<repo>$<branch>`
        Http:   `http$<url>`
    """

    auto_update: bool = True
    """ 自动更新，是否在启动时自动更新本体 """
