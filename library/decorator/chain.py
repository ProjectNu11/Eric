from graia.ariadne.event import MiraiEvent
from graia.ariadne.message import Quote
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.broadcast import DecoratorInterface, ExecutionStop, RequirementCrashed
from kayaku import create

from library.decorator import EricDecorator
from library.model import EricConfig
from library.model.exception import RebuildMessageFailed
from library.model.message import RebuiltMessage


class QuotingOrAtMe(EricDecorator):
    pre = True
    one_at: bool

    @property
    def supported_events(self) -> set[type[MiraiEvent]]:
        return set()

    def __init__(self, one_at: bool = False):
        self.one_at = one_at

    async def _check_quote(self, i: DecoratorInterface) -> bool:
        quote: Quote | None = await self.lookup_param(
            i, "__decorator_parameter_quote__", Quote | None, None
        )
        if not quote:
            return False
        try:
            cfg: EricConfig = create(EricConfig)
            target_id = quote.group_id or (-quote.sender_id)
            return (
                await RebuiltMessage.from_orm(quote.id, target_id)
            ).sender in cfg.accounts
        except RebuildMessageFailed:
            return False

    async def _check_at(self, i: DecoratorInterface) -> bool:
        chain = await self.lookup_param(
            i, "__decorator_parameter__", MessageChain, None
        )
        if not (ats := chain.get(At)):
            return False
        cfg: EricConfig = create(EricConfig)
        return (
            len(set(cfg.accounts).intersection(at.target for at in ats)) == 1
            if self.one_at
            else any(at.target in cfg.accounts for at in ats)
        )

    async def target(self, i: DecoratorInterface):
        try:
            if not (await self._check_quote(i) or await self._check_at(i)):
                raise RequirementCrashed
        except RequirementCrashed as e:
            raise ExecutionStop from e
        return await i.dispatcher_interface.lookup_param(
            "__decorator_parameter__", MessageChain, None
        )
