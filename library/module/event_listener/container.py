from datetime import datetime

from graia.ariadne.event import MiraiEvent
from graia.ariadne.event.message import ActiveMessage
from graia.ariadne.message import Quote
from graia.ariadne.model import Group


class _EventListenerContainer:
    container: dict[int, dict[ActiveMessage, tuple[datetime, MiraiEvent]]] = {}

    @classmethod
    def add(cls, field: int | Group, message: ActiveMessage, event: MiraiEvent):
        cls.container.setdefault(field, {})[message] = (datetime.now(), event)
        cls.cleanup()

    @classmethod
    def cleanup(cls):
        for group, messages in cls.container.copy().items():
            for message, (timestamp, _) in messages.copy().items():
                if (datetime.now() - timestamp).seconds > 60 * 60:
                    cls.container[group].pop(message)
            if not cls.container[group]:
                cls.container.pop(group)

    @classmethod
    def check(cls, quote: Quote) -> bool:
        if (group_id := quote.group_id) not in cls.container:
            return False
        return bool(
            next(
                (msg for msg in cls.container[group_id] if msg.id == quote.id),
                None,
            )
        )
