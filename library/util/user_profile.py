import json

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.model import Friend, Member
from pydantic import BaseModel, validator
from sqlalchemy import select

from library.model.event.util import UserProfilePendingUpdate
from library.model.exception import UserProfileNotFound
from library.model.permission import UserPerm
from library.util.orm import orm
from library.util.orm.table import UserProfileTable
from library.util.permission import FineGrainedPermission, PermissionRegistry


class UserProfile(BaseModel):
    """用户资料"""

    id: int
    """ 用户ID """

    fields: list[int]
    """ 用户组ID列表 """

    name: str
    """ 用户名 """

    nickname: str
    """ 昵称 """

    preferred_name: str
    """ 首选名 """

    permission: UserPerm
    """ 权限等级 """

    fg_permission: list[FineGrainedPermission]
    """ 细粒度权限 """

    module_preferences: dict[str, str]
    """ 模块偏好设置 """

    @validator("permission", pre=True)
    def _permission_validator(cls, v):
        return v if isinstance(v, UserPerm) else UserPerm.from_name(v)

    @validator("fields", "module_preferences", pre=True)
    def _json_validator(cls, v):
        return json.loads(v) if isinstance(v, str) else v

    @validator("fg_permission", pre=True)
    def _fg_permission_validator(cls, v):
        if not isinstance(v, str):
            return v
        raw = json.loads(v)
        permissions = set()
        for i in raw:
            if perm := it(PermissionRegistry).get(i, suppress=True):
                permissions.add(perm)
        return list(permissions)

    def to_insertable(self) -> dict[str, ...]:
        return {
            "id": str(self.id),
            "fields": str(self.fields),
            "name": self.name,
            "nickname": self.nickname,
            "preferred_name": self.preferred_name,
            "permission": self.permission.name,
            "fg_permission": str(self.fg_permission),
            "module_preferences": json.dumps(
                self.module_preferences, ensure_ascii=False
            ),
        }


class UserRegistry:
    @staticmethod
    async def _get_raw(key: int | Member | Friend) -> dict[str, ...]:
        if data := orm.fetchone_dt(
            select(
                UserProfileTable.id,
                UserProfileTable.fields,
                UserProfileTable.name,
                UserProfileTable.nickname,
                UserProfileTable.preferred_name,
                UserProfileTable.permission,
                UserProfileTable.fg_permission,
                UserProfileTable.module_preferences,
            )
            .where(UserProfileTable.id == int(key))  # type: ignore
            .limit(1),
        ):
            async for d in data:
                return d

    @staticmethod
    async def update_profile(profile: UserProfile):
        await orm.insert_or_update(
            UserProfileTable,
            [UserProfileTable.id == profile.id],
            **profile.to_insertable(),
        )

    @classmethod
    async def create_profile(cls, user: Member | Friend) -> UserProfile:
        profile = UserProfile(
            id=int(user),
            fields=[],
            name=user.name,
            nickname=user.nickname if isinstance(user, Friend) else user.name,
            preferred_name=user.name,
            permission=await UserPerm.get(user, check_member_perm=False, no_query=True)
            if isinstance(user, Member)
            else UserPerm.MEMBER,
            fg_permission=[],
            module_preferences={},
        )
        await cls.update_profile(profile)
        Ariadne.broadcast.postEvent(UserProfilePendingUpdate(profile))
        return profile

    async def get_profile(self, key: int | Member | Friend) -> UserProfile:
        data = await self._get_raw(key)
        if data is None:
            raise UserProfileNotFound(key)
        return UserProfile(**data)
