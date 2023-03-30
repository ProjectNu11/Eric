import os
from datetime import datetime

import psutil
from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.twilight import FullMatch, Twilight
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from kayaku import create

from library.decorator import Distribution, Permission
from library.model.config import EricConfig
from library.model.core import EricCore
from library.model.permission import UserPerm
from library.ui import Page
from library.ui.element import Banner, GenericBox, GenericBoxItem, ProgressBar
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message
from library.util.misc import seconds_to_string
from library.util.multi_account.public_group import PublicGroup

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight(PrefixMatch(), FullMatch("sys"))],
        decorators=[Distribution.distribute(), Permission.require(UserPerm.BOT_ADMIN)],
    )
)
async def system_status(app: Ariadne, event: MessageEvent):
    core: EricCore = it(EricCore)
    config: EricConfig = create(EricConfig)
    public_group: PublicGroup = it(PublicGroup)

    mem = psutil.virtual_memory()
    total_memery = round(mem.total / 1024**3, 2)

    proc = psutil.Process(os.getpid())
    proc_mem = proc.memory_info().rss

    page = Page(
        Banner("系统状态"),
        GenericBox(
            GenericBoxItem(
                "登录账号", f"{len(public_group.accounts)} 个 / {len(config.accounts)} 个"
            ),
            GenericBoxItem("启动时间", core.launch_time.strftime("%Y-%m-%d, %H:%M:%S")),
            GenericBoxItem(
                "运行时间",
                seconds_to_string((datetime.now() - core.launch_time).total_seconds()),
            ),
        ),
        GenericBox(
            GenericBoxItem("内存总大小", f"{total_memery} GB"),
        ),
        ProgressBar(
            round(mem.percent / 100, 2),
            "内存使用率",
            f"{round(mem.used / 1024 ** 3, 2)}GB / {total_memery}GB "
            f"({round(mem.used / mem.total * 100, 2)}%)",
        ),
        ProgressBar(
            round(proc_mem / mem.total, 2),
            "Eric 内存占用",
            f"{round(proc_mem / 1024 ** 2, 2)}MB / {total_memery}GB "
            f"({round(proc_mem / mem.total * 100, 2)}%)",
        ),
        GenericBox(
            GenericBoxItem("CPU 物理核心数", str(psutil.cpu_count(logical=False))),
            GenericBoxItem("CPU 频率", f"{psutil.cpu_freq().current}MHz"),
        ),
        ProgressBar(
            (cpu_percent := psutil.cpu_percent()) / 100,
            "CPU 总体占用",
            f"{cpu_percent}%",
        ),
    )
    await send_message(
        event.sender.group if isinstance(event, GroupMessage) else event.sender,
        MessageChain(Image(data_bytes=await page.render(local=True))),
        app.account,
    )
