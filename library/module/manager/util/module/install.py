from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.interrupt import InterruptControl

from library.model.exception import RequirementResolveFailed
from library.module.manager import RemoteModule
from library.module.manager.util.remote.search import bulk_search
from library.module.manager.util.remote.install import install as remote_install
from library.util.message import send_message
from library.util.misc import QUOTE_PATTERN
from library.util.waiter.friend import FriendConfirmWaiter
from library.util.waiter.group import GroupConfirmWaiter

inc = it(InterruptControl)


def _resolve(*modules: RemoteModule) -> list[RemoteModule]:
    resolved: set[str] = set()
    unresolved: set[RemoteModule] = set(modules)
    result: list[RemoteModule] = []

    while unresolved:
        layer = {
            module
            for module in unresolved
            if {
                _req
                for _req in module.required
                if not _req.startswith("library.module")
            }
            <= resolved
        }

        if not layer:
            for _unsolved in unresolved.copy():
                dependencies, not_found = bulk_search(*_unsolved.required)
                if not_found:
                    raise RequirementResolveFailed(unresolved)
                unresolved |= set(dependencies)
        unresolved -= layer
        resolved |= {module.pack for module in layer}
        result.extend(layer)

    return result


def _get_resolve_failed_msg(*modules: RemoteModule) -> MessageChain:
    msg = "无法解决依赖关系"
    for module in modules:
        msg += f"\n - {module.name} ({module.version})"
        for required in module.required:
            msg += f"\n   - {required}"
    return MessageChain(msg)


def _get_msg_empty() -> MessageChain:
    return MessageChain("参数不足")


async def _propose_install(
    *modules: RemoteModule,
) -> tuple[list[RemoteModule], list[RemoteModule]]:
    success: list[RemoteModule] = []
    failed: list[RemoteModule] = []
    for module in modules:
        try:
            await remote_install(module)
            success.append(module)
        except Exception:  # noqa
            # Already logged, just add to failed list
            failed.append(module)
    return success, failed


def _get_msg_success(success: list[RemoteModule]) -> MessageChain | None:
    if not success:
        return
    msg = f"已安装 {len(success)} 个模块"
    for module in success:
        msg += f"\n - {module.name} ({module.version})"
    return MessageChain(msg)


def _get_msg_failed(failed: list[RemoteModule]) -> MessageChain | None:
    if not failed:
        return
    msg = f"{len(failed)} 个模块安装失败"
    for module in failed:
        msg += f"\n - {module.name} ({module.version})"
    return MessageChain(msg)


def _get_msg_not_found(not_found: list[str]) -> MessageChain | None:
    if not not_found:
        return
    msg = f"未找到 {len(not_found)} 个模块"
    for name in not_found:
        msg += f"\n - {name}"
    return MessageChain(msg)


def _get_msg_wait(*modules: RemoteModule) -> MessageChain:
    msg = f"将安装 {len(modules)} 个模块 (y/n)"
    for module in modules:
        msg += f"\n - {module.name} ({module.version})"
    return MessageChain(msg)


async def _wait_for_confirm(event: MessageEvent) -> bool:
    return await inc.wait(
        GroupConfirmWaiter(event.sender.group, event.sender, "y")
        if isinstance(event, GroupMessage)
        else FriendConfirmWaiter(event.sender, "y"),
        timeout=60,
    )


async def _wait(app: Ariadne, event: MessageEvent, found: list[RemoteModule]):
    await send_message(event, _get_msg_wait(*found), app.account)
    if not await _wait_for_confirm(event):
        return MessageChain("已取消安装")


async def install(
    app: Ariadne, event: MessageEvent, content: str, yes: bool
) -> MessageChain:
    if not content:
        return _get_msg_empty()
    names = [name.strip('"').strip("'") for name in QUOTE_PATTERN.findall(content)]
    found, not_found = bulk_search(*names)
    if not found:
        return _get_msg_not_found(not_found)
    try:
        found = _resolve(*found)
    except RequirementResolveFailed as e:
        return _get_resolve_failed_msg(*e.modules)
    if not yes and (msg := await _wait(app, event, found)):
        return msg
    success, failed = await _propose_install(*found)
    msg = [
        _get_msg_success(success),
        _get_msg_failed(failed),
        _get_msg_not_found(not_found),
    ]
    msg = [m for m in msg if m is not None]
    return MessageChain("\n\n").join(*msg)
