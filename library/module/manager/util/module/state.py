from creart import it
from graia.ariadne.message.chain import MessageChain

from library.model.config import GroupConfig
from library.model.module import Module
from library.module.manager.util.module.search import bulk_search_module
from library.util.misc import QUOTE_PATTERN


def _bulk_change_module_state(
    *modules: Module, field: int, value: bool
) -> tuple[list[Module], list[Module]]:
    success: list[Module] = []
    failed: list[Module] = []
    group_cfg: GroupConfig = it(GroupConfig)
    switch = group_cfg.get_switch(field)
    for module in modules:
        try:
            switch.update(module, value)
            group_cfg.save()
            success.append(module)
        except NotImplementedError:
            failed.append(module)
    return success, failed


def _propose_change_state(
    *names: str, field: int, value: bool
) -> tuple[list[Module], list[Module], list[str]]:
    modules, not_found = bulk_search_module(*names)
    success, failed = _bulk_change_module_state(*modules, field=field, value=value)
    return success, failed, not_found


def _get_msg_empty() -> MessageChain:
    return MessageChain(
        '用法：\n - 打开模块 "模块名" "模块名"...\n - 关闭模块 "模块名" "模块名"...'
    )


def _get_msg_success(*result: Module, value: bool) -> MessageChain | None:
    if not result:
        return
    msg = f"已{'打开' if value else '关闭'} {len(result)} 个模块"
    for result in result:
        msg += f"\n - {result.name}"
    return MessageChain(msg)


def _get_msg_failed(*result: Module, value: bool) -> MessageChain | None:
    if not result:
        return
    msg = f"{len(result)} 个模块{'打开' if value else '关闭'}失败"
    for result in result:
        msg += f"\n - {result.name}"
    return MessageChain(msg)


def _get_msg_not_found(*result: str) -> MessageChain | None:
    if not result:
        return
    msg = f"未找到 {len(result)} 个模块"
    for result in result:
        msg += f"\n - {result}"
    return MessageChain(msg)


def change_state(content: str, field: int, value: bool) -> MessageChain:
    if not content:
        return _get_msg_empty()
    names = [name.strip('"').strip("'") for name in QUOTE_PATTERN.findall(content)]
    success, failed, not_found = _propose_change_state(*names, field=field, value=value)
    msg = [
        _get_msg_success(*success, value=value),
        _get_msg_failed(*failed, value=value),
        _get_msg_not_found(*not_found),
    ]
    msg = [m for m in msg if m is not None]
    return MessageChain("\n\n").join(*msg)
