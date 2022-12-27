import sys

from graia.ariadne import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.twilight import (
    ArgResult,
    RegexResult,
    Twilight,
    UnionMatch,
)
from graia.saya import Channel
from loguru import logger
from prompt_toolkit.styles import Style

from library.model.exception import SkipRequiring
from library.module.console.text import wrap
from library.module.manager import UPDATE_EN, lock
from library.module.manager.match import GET_CONFIG_EN
from library.module.manager.util.config.get import mgr_get_module_config
from library.module.manager.util.remote.update import update_gen_msg
from library.util.dispatcher import PrefixMatch

channel = Channel.current()

if "--console" not in sys.argv:
    raise SkipRequiring("未指定 --console")


@channel.use(
    ConsoleSchema([Twilight(PrefixMatch(optional=True), UnionMatch("stop", "exit"))])
)
async def console_stop(app: Ariadne, console: Console):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 你确定要退出吗? "), ("", " (y/n) ")],
        style=Style([("warn", "bg:#cccccc fg:#d00000")]),
    )
    if res.lower() in {"y", "yes"}:
        app.stop()
        console.stop()


@channel.use(ConsoleSchema([Twilight(PrefixMatch(optional=True), UPDATE_EN)]))
async def console_update():
    try:
        assert not lock.locked(), "未能取得管理器锁，请检查是否正在其他操作"
        async with lock:
            logger.info(wrap("正在拉取仓库更新中..."))
            logger.info(wrap(await update_gen_msg()))
    except AssertionError as e:
        logger.error(wrap(e.args[0]))


@channel.use(ConsoleSchema([Twilight(PrefixMatch(optional=True), GET_CONFIG_EN)]))
async def console_get_group_config(group: ArgResult, content: RegexResult):
    group = group.result
    content = content.result.display
    result = mgr_get_module_config(group, content)
    logger.info(wrap(result))
