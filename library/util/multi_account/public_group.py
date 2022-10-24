import contextlib
import time
from abc import ABC
from typing import Type

from creart import AbstractCreator, CreateTargetInfo, exists_module, add_creator
from graia.ariadne import Ariadne
from graia.ariadne.message.element import Source
from graia.ariadne.model import Group
from kayaku import create

from library.model.config.eric import EricConfig


class PublicGroup:
    """公共群分发"""

    data: dict[int, set[int]]
    """ 群组数据 """

    def __init__(self):
        self.data = {}

    async def init_account(self, account: int):
        with contextlib.suppress(Exception):
            app = Ariadne.current(account)
            for group in await app.get_group_list():
                if group.id in self.data:
                    self.data[group.id].add(app.account)
                else:
                    self.data[group.id] = {app.account}
        print(self.data)

    async def init_all(self):
        """初始化数据"""
        config = create(EricConfig)
        for account in config.accounts:
            await self.init_account(account)

    def add_group(self, group: Group | int, account: int):
        """
        添加群组

        Args:
            group (Group | int): 群组
            account (int): 账号
        """
        group = int(group)
        if group in self.data:
            self.data[group].add(account)
        else:
            self.data[group] = {account}

    def remove_group(self, group: Group | int, account: int):
        """
        移除群组

        Args:
            group (Group | int): 群组
            account (int): 账号
        """
        group = int(group)
        if group in self.data and self.data[group]:
            self.data[group].remove(account)

    def get_index(self, group: Group | int, account: int) -> int:
        """
        获取索引

        Args:
            group (Group | int): 群组
            account (int): 账号

        Returns:
            int: 索引

        Raises:
            ValueError: 未找到索引
        """
        group = int(group)
        if group in self.data and account in self.data[group]:
            return list(self.data[group]).index(account)
        raise ValueError

    def get_accounts(self, group: Group | int) -> set[int]:
        """
        获取账号列表

        Args:
            group (Group | int): 群组

        Returns:
            set[int]: 账号列表
        """
        group = int(group)
        return self.data[group] if group in self.data else set()

    def remove_account(self, account: int):
        """
        移除账号

        Args:
            account (int): 账号
        """
        for group in self.data:
            if account in self.data[group]:
                self.data[group].remove(account)

    def need_distribute(self, group: Group | int, account: int) -> bool:
        """
        是否需要分发

        Args:
            group (Group | int): 群组
            account (int): 账号

        Returns:
            bool: 是否需要分发
        """
        group = int(group)
        if group in self.data and account in self.data[group]:
            print("Need Distribute")
            return len(self.data[group]) > 1
        return False

    def execution_stop(self, group: Group | int, account: int, source: Source) -> bool:
        """
        是否执行停止

        Args:
            group (Group | int): 群组
            account (int): 账号
            source (Source): 消息链 Source

        Returns:
            bool: 是否执行停止
        """
        group = int(group)
        if group not in self.data:
            self.add_group(group, account)
            return True
        return (source.id + int(time.mktime(source.time.timetuple()))) % len(
            self.data[group]
        ) != self.get_index(group, account)


class PublicGroupClassCreator(AbstractCreator, ABC):
    targets = (
        CreateTargetInfo("library.util.multi_account.public_group", "PublicGroup"),
    )

    @staticmethod
    def available() -> bool:
        return exists_module("library.util.multi_account.public_group")

    @staticmethod
    def create(_create_type: Type[PublicGroup]) -> PublicGroup:
        return PublicGroup()


add_creator(PublicGroupClassCreator)
