from pydantic import BaseModel, validator


class ManagerConfig(BaseModel):
    """管理配置"""

    plugin_repo: list[str] = []
    """ 插件仓库 """

    @validator("plugin_repo", pre=True)
    def _manager_config_plugin_repo(cls, plugin_repo) -> list[str]:
        if isinstance(plugin_repo, str):
            plugin_repo = [plugin_repo]
        return list(set(plugin_repo))
