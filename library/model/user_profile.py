from dataclasses import dataclass, field


@dataclass
class UserProfile:
    """用户资料模型"""

    id: int
    """ 用户 ID """

    fields: list[int]
    """ 用户组 ID 列表 """

    name: str
    """ 用户名 """

    nickname: str
    """ 昵称 """

    preferred_name: str
    """ 首选名 """

    chat_count: int = 0
    """ 聊天次数 """

    usage_count: int = 0
    """ 使用次数 """

    module_preferences: dict[str, ...] = field(default_factory=dict)
    """ 模块偏好设置 """

    def register_module_preference(self, module: str, preference: dict[str, ...]):
        """注册模块偏好设置"""
        self.module_preferences[module] = preference

    def get_module_preference(self, module: str) -> dict[str, ...]:
        """获取模块偏好设置"""
        return self.module_preferences.get(module, {})
