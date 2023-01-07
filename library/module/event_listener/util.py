import pickle
import uuid

import aiofiles
from creart import it
from graia.ariadne.event import MiraiEvent
from graia.ariadne.event.mirai import RequestEvent
from graia.ariadne.message import Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Group
from graia.broadcast import ExecutionStop
from graia.saya import Channel
from kayaku import create

from library.module.event_listener.config import (
    _EventListenerConfig,
    _EventListenerGroupConfig,
)
from library.module.event_listener.container import _EventListenerContainer
from library.util.group_config import module_create
from library.util.message import send_message
from library.util.misc import camel_to_snake
from library.util.module import Modules

channel = Channel.current()
module = it(Modules).get(channel.module)
data_path = module.data_path


async def _send_message(
    target: Group | Friend | int,
    message_chain: MessageChain | str,
    account: int,
    event: MiraiEvent,
    *,
    is_group: bool = None,
    suppress: bool = True,
    resend: bool = True,
    quote: Source | int | None = None,
    excluded_account: set[int] = None,
):
    if not message_chain:
        return
    if not (
        msg := await send_message(
            target,
            message_chain
            if isinstance(message_chain, MessageChain)
            else MessageChain(message_chain),
            account,
            is_group=is_group,
            suppress=suppress,
            resend=resend,
            quote=quote,
            excluded_account=excluded_account,
        )
    ):
        return
    field = 0 if isinstance(target, Friend) else int(target)
    _EventListenerContainer.add(field=field, message=msg, event=event)


def _get_cfg(field: int, event: MiraiEvent, /, **kwargs) -> tuple[str, str]:
    # Main config
    cls: str = camel_to_snake(event.__class__.__name__)
    cfg: _EventListenerConfig = create(_EventListenerConfig, flush=True)
    if not getattr(cfg, f"{cls}_switch", False):
        raise ExecutionStop
    msg: str = getattr(cfg, cls, "")

    # Group config
    group_cfg: _EventListenerGroupConfig = module_create(
        _EventListenerGroupConfig, field=field, flush=True
    )
    group_msg: str = getattr(group_cfg, cls, "")
    if getattr(group_cfg, f"{cls}_switch", None) is False:
        raise ExecutionStop
    return (group_msg or msg).format(**kwargs), msg.format(**kwargs)


async def _pickle_request(account: int, event: RequestEvent) -> str:
    request_id = event.request_id
    cls: str = camel_to_snake(event.__class__.__name__)
    uuid_str = str(uuid.uuid5(uuid.NAMESPACE_OID, f"{request_id}_{cls}"))
    path = data_path / str(account)
    path.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path / f"{uuid_str}.pkl", "wb") as f:
        await f.write(pickle.dumps(event))
    return uuid_str


async def _unpickle_request(account: int, request_id: str):
    path = data_path / str(account)
    path.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path / f"{request_id}.pkl", "rb") as f:
        return pickle.loads(await f.read())
