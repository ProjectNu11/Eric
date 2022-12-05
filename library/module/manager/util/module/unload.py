from creart import it
from graia.ariadne.message.chain import MessageChain
from graia.saya import Saya
from kayaku import create
from loguru import logger

from library.model.config.state import ModuleState
from library.model.module import Module
from library.util.misc import QUOTE_PATTERN
from library.util.module import Modules

saya = Saya.current()


def unload(module: Module):
    assert (
        chn := saya.channels.get(module.pack, None)
    ), f"模块 {module.name} ({module.pack}) 未加载"
    assert module.advanced.allow_disable, (
        f"无法更改插件 {module.name} ({module.pack}) 的状态，"
        f"插件状态固定为 {module.advanced.allow_disable}"
    )
    module.loaded = False
    state: ModuleState = create(ModuleState)
    state.unload(module.pack)
    saya.uninstall_channel(chn)
    logger.info(f"[Manager] 卸载模块 {module.name} ({module.pack})")


def _bulk_unload(*modules: Module) -> tuple[int, list[str]]:
    success: int = 0
    failed: list[str] = []
    for module in modules:
        try:
            unload(module)
            success += 1
        except AssertionError as e:
            failed.append(e.args[0])
    return success, failed


def _perform_bulk(*modules: str) -> tuple[int, list[str], list[str]]:
    not_found: list[str] = []
    _mods = it(Modules)
    result: list[Module] = []
    for module in modules:
        if not (
            _mod := _mods.search(
                lambda mod: any(
                    [
                        module.lower() == mod.name.lower(),
                        module.lower() == mod.pack.lower().split(".")[-1],
                        module.lower()
                        == mod.name.lower().replace(" ", "").split(".")[-1],
                    ]
                )
            )
        ):
            not_found.append(module)
        else:
            result.append(_mod[0])
    success, failed = _bulk_unload(*result)
    return success, failed, not_found


def _get_msg_success(success: int) -> MessageChain | None:
    return MessageChain(f"成功卸载 {success} 个模块") if success else None


def _get_msg_failed(failed: list[str]) -> MessageChain | None:
    return (
        MessageChain(f"{len(failed)} 个模块卸载失败：\n" + "\n".join(failed))
        if failed
        else None
    )


def _get_msg_not_found(not_found: list[str]) -> MessageChain | None:
    return (
        MessageChain(f"{len(not_found)} 个模块未找到：\n" + "\n".join(not_found))
        if not_found
        else None
    )


def _get_msg(success: int, failed: list[str], not_found: list[str]) -> MessageChain:
    msg = [
        _get_msg_success(success),
        _get_msg_failed(failed),
        _get_msg_not_found(not_found),
    ]
    return MessageChain([m for m in msg if m])


def perform_unload(content: str) -> MessageChain:
    modules = [name.strip('"').strip("'") for name in QUOTE_PATTERN.findall(content)]
    success, failed, not_found = _perform_bulk(*modules)
    return _get_msg(success, failed, not_found)
