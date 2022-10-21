from datetime import datetime, timedelta

from graia.ariadne.model import Member, Friend, Group
from kayaku import create

from library.model.config.eric import EricConfig


class FrequencyLimit:
    """频率限制"""

    @property
    def flush_time(self) -> int:
        """刷新间隔（秒）"""
        return create(EricConfig).function.frequency_limit.flush

    @property
    def user_max(self) -> int:
        """单用户最大请求权重，为 0 时不限制"""
        return create(EricConfig).function.frequency_limit.user_max

    @property
    def field_max(self) -> int:
        """单区域最大请求权重，为 0 时不限制"""
        return create(EricConfig).function.frequency_limit.field_max

    @property
    def global_max(self) -> int:
        return create(EricConfig).function.frequency_limit.global_max

    field: dict[int, list[tuple[int, datetime]]] = {}
    """ 聊天区域请求权重 """

    supplicant: dict[int, list[tuple[int, datetime]]] = {}
    """ 用户请求权重 """

    flagged: dict[int, tuple[bool, datetime]] = {}
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

        if field not in self.field:
            self.field[field] = [(weight, datetime.now())]
        else:
            self.field[field].append((weight, datetime.now()))

        if supplicant not in self.supplicant:
            self.supplicant[supplicant] = [(weight, datetime.now())]
        else:
            self.supplicant[supplicant].append((weight, datetime.now()))

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

    def set_flag(self, target: int | Member | Friend, flag: bool):
        """
        标记用户

        Args:
            target: 用户
            flag: 标记，False 时为未通知，True 时为已通知
        """

        self.flagged[int(target)] = (flag, datetime.now())

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
