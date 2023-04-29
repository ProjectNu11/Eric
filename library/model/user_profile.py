from creart import it
from pydantic import BaseModel, validator

from library.model.permission import FineGrainedPermission, UserPerm
from library.util.permission import PermissionRegistry


class UserProfile(BaseModel):
    """用户资料"""

    id: int
    """ 用户ID """

    name: str
    """ 用户名 """

    permission: UserPerm
    """ 权限等级 """

    fg_permission: list[FineGrainedPermission]
    """ 细粒度权限 """

    @validator("permission", pre=True)
    def _permission_validator(cls, v):
        return v if isinstance(v, UserPerm) else UserPerm.from_name(v)

    @validator("fg_permission", pre=True)
    def _fg_permission_validator(cls, v):
        if not isinstance(v, str):
            return v
        raw = v.split(",")
        permissions = set()
        for i in raw:
            if perm := it(PermissionRegistry).get(i, suppress=True):
                permissions.add(perm)
            else:
                permissions.add(
                    FineGrainedPermission(
                        id=i,
                        name=i,
                        description="Unknown permission.",
                    )
                )
        return list(permissions)

    def to_insertable(self) -> dict[str, str | int]:
        return {
            "id": self.id,
            "name": self.name,
            "permission": self.permission.name,
            "fg_permission": "".join(perm.id for perm in self.fg_permission),
        }
