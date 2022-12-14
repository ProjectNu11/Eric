import traceback
from contextlib import suppress
from datetime import datetime
from io import StringIO

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.broadcast.builtin.event import ExceptionThrowed
from graiax.shortcut import listen
from kayaku import create

from library.model.config import EricConfig
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


def _generate_msg(event: ExceptionThrowed, tb: str) -> str:
    config: EricConfig = create(EricConfig)

    return f"""
# {config.name} ????????????????????????????????????

## ????????????

```text
{datetime.now():%Y???%m???%d??? %H:%M:%S}
```

## ????????????

?????????`{event.event.sender.group.id if isinstance(event.event, GroupMessage) else "??????"}`

?????????`{event.event.sender.id}`

?????????`{event.event.message_chain.display}`

## ????????????

```python
{type(event.exception)}
```

## ????????????

```text
{str(event.exception)}
```

## ????????????

```python
{tb}
```
"""
