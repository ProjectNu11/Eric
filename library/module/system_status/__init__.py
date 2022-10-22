from datetime import datetime

import psutil
from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema

from library.depend.distribute import Distribution
from library.model.config.eric import EricConfig
from library.model.core import EricCore
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.misc import seconds_to_string

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight(PrefixMatch(), FullMatch("sys"))],
        decorators=[Distribution.distribute()],
    )
)
async def system_status(app: Ariadne, event: MessageEvent):
    core: EricCore = it(EricCore)
    config: EricConfig = it(EricConfig)

    mem = psutil.virtual_memory()
    total_memery = round(mem.total / 1024**3, 2)
    await send_message(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(
            Plain(
                f"登录账号：{len(config.accounts)} 个\n"
                f"启动时间：{core.launch_time.strftime('%Y-%m-%d, %H:%M:%S')}\n"
                f"已运行时间：{seconds_to_string((datetime.now() - core.launch_time).seconds)}\n"
                "内存相关：\n    "
                f"内存总大小：{total_memery}GB\n    "
                f"内存使用量：{round(mem.used / 1024 ** 3, 2)}GB / {total_memery}GB ({round(mem.used / mem.total * 100, 2)}%)\n    "
                f"内存空闲量：{round(mem.free / 1024 ** 3, 2)}GB / {total_memery}GB ({round(mem.free / mem.total * 100, 2)}%)\n"
                "CPU相关：\n    "
                f"CPU 物理核心数：{psutil.cpu_count(logical=False)}\n    "
                f"CPU总体占用：{psutil.cpu_percent()}%\n    "
                f"CPU频率：{psutil.cpu_freq().current}MHz"
            )
        ),
        app.account,
    )
