import asyncio
import re
import subprocess
import time

from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.message.parser.twilight import (
    Twilight,
    ElementMatch,
    RegexMatch,
    FullMatch,
    WildcardMatch,
    MatchResult,
)
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from kayaku import create
from loguru import logger

from library.decorator.blacklist import Blacklist
from library.decorator.function_call import FunctionCall
from library.decorator.permission import Permission
from library.decorator.timer import timer
from library.model.config.eric import EricConfig
from library.model.permission import UserPerm
from library.util.image import render_md
from library.util.message import send_message
from library.util.misc import seconds_to_string

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    ElementMatch(At),
                    RegexMatch(r"[\n\r]?", optional=True),
                    FullMatch("shell"),
                    FullMatch(">"),
                    WildcardMatch().flags(re.S) @ "command",
                ]
            )
        ],
        decorators=[
            MentionMe(),
            Permission.require(UserPerm.BOT_OWNER),
            Blacklist.check(),
            FunctionCall.record(channel.module),
        ],
    )
)
@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("shell"),
                    FullMatch(">"),
                    WildcardMatch().flags(re.S) @ "command",
                ]
            )
        ],
        decorators=[
            Permission.require(UserPerm.BOT_OWNER),
            Blacklist.check(),
            FunctionCall.record(channel.module),
        ],
    )
)
async def execute_command(app: Ariadne, event: MessageEvent, command: MatchResult):
    command: str = command.result.display.strip()
    if not command:
        return await send_message(event, MessageChain("Command is empty."), app.account)
    logger.info(f"Executing command: {command!r}")
    stdout, stderr, time_cost = await execute(command)
    logger.success(f"Finished executing command: {command!r}")
    image = await render(command, stdout, stderr, time_cost)
    await send_message(event, MessageChain(Image(data_bytes=image)), app.account)


def _execute(command: str) -> tuple[str, str]:
    process = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout = process.stdout
    stderr = process.stderr
    try:
        return stdout.decode("utf-8"), stderr.decode("utf-8")
    except UnicodeDecodeError:
        return stdout.decode("gbk"), stderr.decode("gbk")


@timer(channel.module)
async def execute(command: str) -> tuple[str, str, float]:
    start_time = time.perf_counter()
    stdout, stderr = await asyncio.to_thread(_execute, command)
    return stdout, stderr, time.perf_counter() - start_time


async def render(command: str, stdout: str, stderr: str, time_used: float) -> bytes:
    config: EricConfig = create(EricConfig)
    _time_int = int(time_used)
    _time_float = time_used - _time_int
    time_str = f"{seconds_to_string(_time_int)} {_time_float} 毫秒"

    md = f"""
# {config.name} 已执行完成

## 执行代码

```shell
{command}
```

## 执行耗时

```text
{time_str}
```

## 标准输出

```text
{stdout}
```
"""

    if stderr:
        md += f"""## 错误输出

```text
{stderr}
```
"""

    return await render_md(md)
