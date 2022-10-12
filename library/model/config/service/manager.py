from pydantic import BaseModel


class ManagerConfig(BaseModel):
    """管理配置"""

    plugin_repo: str = ""
    """ 插件仓库 """
