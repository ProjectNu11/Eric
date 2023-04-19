from typing import NoReturn

from graia.ariadne import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.element import At, Quote, Source
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend


class MentionMeOptional:
    @staticmethod
    def check() -> Depend:
        async def judge(app: Ariadne, event: MessageEvent) -> NoReturn:
            msg_copy = event.message_chain.copy().exclude(Source, Quote)
            if isinstance((at := msg_copy[0]), At):
                if at.target != app.account:  # type: ignore
                    raise ExecutionStop

        return Depend(judge)
