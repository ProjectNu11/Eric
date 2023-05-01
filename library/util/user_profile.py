from graia.ariadne.model import Friend, Member
from sqlalchemy import select

from library.model import UserProfile
from library.model.exception import UserProfileNotFound
from library.model.permission import UserPerm
from library.util.orm import orm
from library.util.orm.table import UserProfileTable


class UserRegistry:
    @staticmethod
    async def _get_raw(key: int | Member | Friend) -> dict[str, ...]:
        if data := orm.fetchone_dt(
            select(
                UserProfileTable.id,
                UserProfileTable.name,
                UserProfileTable.permission,
                UserProfileTable.fg_permission,
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
            name=user.name,
            permission=await UserPerm.get(user, check_member_perm=False, no_query=True)
            if isinstance(user, Member)
            else UserPerm.MEMBER,
            fg_permission=[],
        )
        await cls.update_profile(profile)
        return profile

    @classmethod
    async def get_profile(cls, key: int | Member | Friend) -> UserProfile:
        data = await cls._get_raw(key)
        if data is None:
            raise UserProfileNotFound(key)
        return UserProfile(**data)

    @classmethod
    async def get_or_create_profile(cls, user: Member | Friend) -> UserProfile:
        try:
            return await cls.get_profile(user)
        except UserProfileNotFound:
            return await cls.create_profile(user)
