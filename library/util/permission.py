from dataclasses import dataclass


@dataclass
class FineGrainedPermission:
    """细粒度权限"""

    id: str
    """ 权限 ID，推荐使用 `channel.module:name` 等具有唯一性的字符串 """

    name: str
    """ 权限名称 """

    description: str = ""
    """ 权限描述 """

    def __repr__(self):
        return (
            f"<FineGrainedPermission id={self.id} "
            f"name={self.name} description={self.description}>"
        )

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.id)


class PermissionRegistry:
    """权限注册表"""

    _registry: set[FineGrainedPermission]

    def __init__(self):
        self._registry = set()

    def register(self, *permissions: FineGrainedPermission):
        """
        注册权限

        Args:
            permissions: 细粒度权限
        """
        self._registry.update(permissions)

    def unregister(self, *permissions: FineGrainedPermission):
        """
        注销权限

        Args:
            permissions: 细粒度权限
        """
        self._registry.difference_update(permissions)

    def get(self, _id: str) -> FineGrainedPermission:
        """
        获取权限

        Args:
            _id: 细粒度权限 ID

        Returns:
            细粒度权限

        Raises:
            KeyError: 未找到权限
        """
        for permission in self._registry:
            if permission.id == _id:
                return permission
        raise KeyError(f"Permission {_id} not found")

    def __getitem__(self, item: str) -> FineGrainedPermission:
        return self.get(item)

    def __contains__(self, item: str | FineGrainedPermission) -> bool:
        if isinstance(item, FineGrainedPermission):
            return item in self._registry
        return item in (permission.id for permission in self._registry)

    def __iter__(self):
        return iter(self._registry)

    def __len__(self):
        return len(self._registry)
