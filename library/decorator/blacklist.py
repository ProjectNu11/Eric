from typing import NoReturn

from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from loguru import logger
from sqlalchemy import select

from library.util.orm import orm
from library.util.orm.table import BlacklistTable


class Blacklist:
    @classmethod
    def check(cls, show_log: bool = False) -> Depend:
        async def judge(event: MessageEvent) -> NoReturn:
            field = int(event.sender.group) if isinstance(event, GroupMessage) else 0
            supplicant = int(event.sender)
            if any(
                [
                    await cls.check_field(field),
                    await cls.check_supplicant(supplicant, field),
                    await cls.check_supplicant(supplicant, -1),
                ]
            ):
                if show_log:
                    logger.warning(f"[Blacklist] {field}: {supplicant} 在黑名单中")
                raise ExecutionStop()

        return Depend(judge)

    @classmethod
    async def check_field(cls, field: int | Group) -> bool:
        return await cls.check_by_condition(
            BlacklistTable.target == 0,
            BlacklistTable.field == int(field),
            table=BlacklistTable,
        )

    @classmethod
    async def check_supplicant(
        cls, supplicant: int | Member | Friend, field: int | Group
    ) -> bool:
        return await cls.check_by_condition(
            BlacklistTable.target == int(supplicant),
            BlacklistTable.field == int(field),
            table=BlacklistTable,
        )

    @staticmethod
    async def check_by_condition(*conditions, table) -> bool:
        return bool(await orm.all(select(table).where(*conditions)))

    # TODO Implement TempBlacklistTable
