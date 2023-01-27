from dataclasses import field

from kayaku import config

from library.model.repo import (
    GenericPluginRepo,
    GitHubPluginRepo,
    GitLabPluginRepo,
    HTTPPluginRepo,
)


@config("library.service.manager")
class ManagerConfig:
    """管理配置"""

    plugin_repo: list[str] = field(default_factory=list)
    """
    模块仓库，绝大多数情况下不需要手动配置

    格式：
        Github: `github$<owner>/<repo>$<branch>`
        GitLab: `gitlab$<base>/<owner>/<repo>$<branch>`
        Http:   `http$<url>`
    """

    self_auto_update: bool = True
    """ 自动更新，是否在启动时自动更新本体 """

    plugin_auto_update: bool = True
    """ 自动更新，是否自动拉取模块更新 """

    plugin_auto_upgrade: bool = False
    """ 自动更新，是否自动升级模块 """

    def register_repo(self, repo_type: str, *data: str):
        if repo_type.lower() == "github" and len(data) in {3, 2}:
            if len(data) == 3:
                self.plugin_repo.append(f"github${data[0]}/{data[1]}${data[2]}")
            else:
                self.plugin_repo.append(f"github${data[0]}/{data[1]}$modules")
        elif repo_type.lower() == "http" and len(data) == 1:
            url = data[0].rstrip("/")
            self.plugin_repo.append(f"http${url}")
        else:
            raise ValueError("无效的仓库类型或参数")

    def parse_repo(self) -> list[GenericPluginRepo]:
        repos: list[GenericPluginRepo] = []
        for repo in self.plugin_repo:
            if repo.startswith("github$"):
                repos.append(self._parse_github_repo(repo))
            elif repo.startswith("http$"):
                repos.append(self._parse_http_repo(repo))
        return repos

    @staticmethod
    def _parse_github_repo(data: str) -> GitHubPluginRepo:
        _, _repo, branch = data.split("$", maxsplit=2)
        owner, repo = _repo.split("/", maxsplit=1)
        return GitHubPluginRepo(owner=owner, repo=repo, branch=branch)

    @staticmethod
    def _parse_gitlab_repo(data: str) -> GitLabPluginRepo:
        _, _repo, branch = data.split("$", maxsplit=2)
        base, _repo = _repo.split("/", maxsplit=1)
        owner, repo = _repo.split("/", maxsplit=1)
        return GitLabPluginRepo(base=base, owner=owner, repo=repo, branch=branch)

    @staticmethod
    def _parse_http_repo(data: str) -> HTTPPluginRepo:
        _, url = data.split("$", maxsplit=1)
        return HTTPPluginRepo(url=url)
