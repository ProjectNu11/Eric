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

    def register_repo(self, repo_type: str, *data: str):
        if repo_type.lower() == "github" and len(data) == 3:
            self.plugin_repo.append(f"github${data[0]}/${data[1]}${data[2]}")
        elif repo_type.lower() == "http" and len(data) == 1:
            url = data[0].rstrip("/")
            self.plugin_repo.append(f"http${url}")
        else:
            raise ValueError("无效的仓库类型或参数")
