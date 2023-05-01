from library.model.permission import FineGrainedPermission


class PermissionRegistry:
    """权限注册表"""

    _registry: set[FineGrainedPermission]

    def __init__(self):
        self._registry = set()

    def register(self, *permissions: FineGrainedPermission):
        """
        注册权限，一般情况下无需手动调用

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

    def get(self, _id: str, *, suppress: bool = False) -> FineGrainedPermission:
        """
        获取权限

        Args:
            _id: 细粒度权限 ID
            suppress: 是否抑制异常

        Returns:
            细粒度权限

        Raises:
            KeyError: 未找到权限
        """
        for permission in self._registry:
            if permission.id == _id:
                return permission
        if not suppress:
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
