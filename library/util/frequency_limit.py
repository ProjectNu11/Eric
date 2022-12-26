from abc import ABC
from datetime import datetime, timedelta
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module
from graia.ariadne.model import Friend, Group, Member
from kayaku import create

from library.model.config import FrequencyLimitConfig
from library.util.orm import orm
from library.util.orm.table import TempBlacklistTable


class FrequencyLimit:
    """频率限制"""

    @property
    def flush_time(self) -> int:
        """刷新间隔（秒）"""
        return create(FrequencyLimitConfig).flush

    @property
    def user_max(self) -> int:
        """单用户最大请求权重，为 0 时不限制"""
        return create(FrequencyLimitConfig).user_max

    @property
    def field_max(self) -> int:
        """单区域最大请求权重，为 0 时不限制"""
        return create(FrequencyLimitConfig).field_max

    @property
    def global_max(self) -> int:
        return create(FrequencyLimitConfig).global_max

    field: dict[int, list[tuple[int, datetime]]] = {}
    """ 聊天区域请求权重 """

    supplicant: dict[int, list[tuple[int, datetime]]] = {}
    """ 用户请求权重 """

    flagged: dict[int, bool] = {}
    """ 被标记的用户 """

    def add_weight(
        self,
        field: int | Group | Friend,
        supplicant: int | Member | Friend,
        weight: int,
    ):
        """
        添加权重

        Args:
            field: 聊天区域，为 0 时为私聊
            supplicant: 用户
            weight: 权重
        """

        field = 0 if isinstance(field, Friend) else int(field)
        supplicant = int(supplicant)
        log = weight, datetime.now()

        if field not in self.field:
            self.field[field] = [log]
        else:
            self.field[field].append(log)

        if supplicant not in self.supplicant:
            self.supplicant[supplicant] = [log]
        else:
            self.supplicant[supplicant].append(log)

    def cleanup(self):
        """清理过期权重"""

        for field in self.field:
            self.field[field] = [
                (weight, time)
                for weight, time in self.field[field].copy()
                if time + timedelta(seconds=self.flush_time) > datetime.now()
            ]

        for supplicant in self.supplicant:
            self.supplicant[supplicant] = [
                (weight, time)
                for weight, time in self.supplicant[supplicant].copy()
                if time + timedelta(seconds=self.flush_time) > datetime.now()
            ]

    def flush_weight(self):
        """刷新权重"""

        self.field.clear()
        self.supplicant.clear()

    def get_field_weight(self, target: int | Group) -> int:
        """
        获取区域权重

        Args:
            target: 聊天区域，为 0 时为私聊
        """
        return sum(weight for weight, _ in self.field.get(int(target), []))

    def get_supplicant_weight(self, target: int | Member | Friend) -> int:
        """
        获取用户权重

        Args:
            target: 用户
        """
        return sum(weight for weight, _ in self.supplicant.get(int(target), []))

    def get_global_weight(self) -> int:
        """获取全局权重"""
        return sum(
            sum(weight for weight, _ in self.field[field]) for field in self.field
        )

    def check_field(self, target: int | Group) -> bool:
        """
        检查区域权重是否未超出限制

        Args:
            target: 聊天区域，为 0 时为私聊

        Returns:
            是否未超出限制
        """

        return self.field_max == 0 or self.get_field_weight(target) <= self.field_max

    def check_supplicant(self, target: int | Member | Friend) -> bool:
        """
        检查用户权重是否未超出限制

        Args:
            target: 用户

        Returns:
            是否未超出限制
        """

        return self.user_max == 0 or self.get_supplicant_weight(target) <= self.user_max

    def check_global(self) -> bool:
        """检查全局权重是否未超出限制"""
        return self.global_max == 0 or self.get_global_weight() <= self.global_max

    def notified(self, target: int | Member | Friend):
        """
        通知用户

        Args:
            target: 用户
        """

        self.flagged[int(target)] = True

    def is_notified(self, target: int | Member | Friend) -> bool:
        """
        检查用户是否已被通知

        Args:
            target: 用户

        Returns:
            是否已被通知
        """

        return self.flagged[int(target)] if int(target) in self.flagged else False

    async def blacklist_user(self, target: int | Member | Friend):
        """
        将用户加入黑名单

        Args:
            target: 用户
        """

        self.flagged[int(target)] = False
        await orm.insert_or_update(
            TempBlacklistTable,
            [TempBlacklistTable.target == int(target)],
            field=-1,
            target=int(target),
            time=datetime.now(),
            reason="频率限制",
            supplicant=0,
            duration=60 * 60,
        )

    async def blacklist_field(self, target: int | Group):
        """
        将聊天区域加入黑名单

        Args:
            target: 聊天区域
        """

        self.flagged[int(target)] = False
        await orm.insert_or_update(
            TempBlacklistTable,
            [TempBlacklistTable.field == int(target)],
            field=int(target),
            target=-1,
            time=datetime.now(),
            reason="频率限制",
            supplicant=0,
            duration=60 * 60,
        )


class FrequencyLimitCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("library.util.frequency_limit", "FrequencyLimit"),)

    @staticmethod
    def available() -> bool:
        return exists_module("library.util.frequency_limit")

    @staticmethod
    def create(_create_type: Type[FrequencyLimit]) -> FrequencyLimit:
        return FrequencyLimit()
