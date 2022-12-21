import traceback
from contextlib import suppress
from datetime import datetime
from io import StringIO

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import FullMatch, Twilight
from graia.broadcast.builtin.event import ExceptionThrowed
from graiax.shortcut import decorate, dispatch, listen
from kayaku import create

from library.decorator import Distribution, Permission
from library.model.config.eric import EricConfig
from library.model.permission import UserPerm
from library.util.image import render_md
from library.util.message import send_message
from library.util.multi_account.public_group import PublicGroup


@listen(ExceptionThrowed)
async def except_handle(app: Ariadne, event: ExceptionThrowed):
    if not isinstance(event.event, (GroupMessage, FriendMessage)):
        return

    if isinstance(event.event, GroupMessage):
        p_group = it(PublicGroup)
        if p_group.need_distribute(
            event.event.sender.group, app.account
        ) and p_group.execution_stop(
            event.event.sender.group, app.account, event.event.source
        ):
            return

    with StringIO() as fp:
        traceback.print_tb(event.exception.__traceback__, file=fp)
        tb = fp.getvalue()

    img = await render_md(_generate_msg(event, tb))
    await send_message(
        event.event,
        MessageChain(Image(data_bytes=img)),
        app.account,
        quote=event.event.source,
    )

    config: EricConfig = create(EricConfig)
    for owner in config.owners:
        with suppress(Exception):
            await send_message(
                owner, MessageChain(Image(data_bytes=img)), app.account, is_group=False
            )
    for dev_group in config.dev_groups:
        with suppress(Exception):
            await send_message(
                dev_group,
                MessageChain(Image(data_bytes=img)),
                app.account,
                is_group=True,
            )


@listen(GroupMessage, FriendMessage)
@dispatch(Twilight(FullMatch(".raise")))
@decorate(Distribution.distribute(), Permission.require(UserPerm.BOT_ADMIN))
async def raise_runtime_error():
    raise RuntimeError("Manually raised error for testing purpose")


def _generate_msg(event: ExceptionThrowed, tb: str) -> str:
    config: EricConfig = create(EricConfig)

    return f"""
# {config.name} 在执行操作时发生以下异常

## 异常时间

```text
{datetime.now():%Y年%m月%d日 %H:%M:%S}
```

## 异常详情

群组：`{event.event.sender.group.id if isinstance(event.event, GroupMessage) else "私聊"}`

用户：`{event.event.sender.id}`

消息：`{event.event.message_chain.display}`

## 异常类型

```python
{type(event.exception)}
```

## 异常内容

```text
{str(event.exception)}
```

## 异常追踪

```python
{tb}
```
"""
