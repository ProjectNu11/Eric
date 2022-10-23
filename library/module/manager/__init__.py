import re

from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.twilight import (
    Twilight,
    ElementMatch,
    FullMatch,
    UnionMatch,
    WildcardMatch,
    RegexResult,
)
from graia.ariadne.util.saya import listen, dispatch, decorate
from graia.saya import Channel

from library.decorator.distribute import Distribution
from library.decorator.mention import MentionMeOptional
from library.decorator.permission import Permission
from library.model.config.group_config import GroupConfig
from library.model.module import Module
from library.model.permission import UserPerm
from library.module.manager.util import search_module
from library.util.dispatcher import PrefixMatch
from library.util.message import send_message

channel = Channel.current()

STATE_PATTERN = re.compile(r"""(".+?"|'.+?'|[^ "']+)""")


@listen(GroupMessage)
@dispatch(
    Twilight(
        ElementMatch(At, optional=True) @ "at",
        PrefixMatch(optional=True),
        UnionMatch("打开", "关闭") @ "action",
        FullMatch("插件"),
        WildcardMatch() @ "content",
    )
)
@decorate(
    MentionMeOptional.check(),
    Distribution.distribute(),
    Permission.require(UserPerm.ADMINISTRATOR),
)
async def manager_change_group_module_state(
    app: Ariadne, event: MessageEvent, action: RegexResult, content: RegexResult
):
    action: str = action.result.display
    content: str = content.result.display
    success = 0
    failed: list[str] = []
    if modules := STATE_PATTERN.findall(content):
        modules: list[str] = [module.strip('"').strip("'") for module in modules]
        modules: list[Module] = [
            mod for module in modules if (mod := search_module(module))
        ]
        switch = it(GroupConfig).get_switch(int(event.sender.group))
        for module in modules:
            try:
                switch.update(module, action == "打开")
                success += 1
            except NotImplementedError:
                failed.append(module.name)
    if failed:
        msg = (
            f"已{action}插件{success}个\n" f"失败{len(failed)}个\n" f"失败列表：{', '.join(failed)}"
        )
    else:
        msg = f"已{action}插件{success}个"
    await send_message(event.sender.group, MessageChain(msg), app.account)
