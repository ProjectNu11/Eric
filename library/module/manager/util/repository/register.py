from creart import it
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.interrupt import InterruptControl
from kayaku import create

from library.model.config import ManagerConfig
from library.module.manager.model.repository import ParsedRepository
from library.util.message import send_message
from library.util.waiter.friend import FriendMessageWaiter, FriendSelectWaiter
from library.util.waiter.group import GroupMessageWaiter, GroupSelectWaiter

inc = it(InterruptControl)


async def _wait_for_repo_type(event: MessageEvent) -> str:
    return await inc.wait(
        (
            GroupSelectWaiter(event.sender.group, event.sender, "github", "http")
            if isinstance(event, GroupMessage)
            else FriendSelectWaiter(event.sender, "github", "http")
        ),
        timeout=60,
    )


async def _wait_for_reply(msg: str, app: Ariadne, event: MessageEvent) -> str:
    await send_message(event, MessageChain(msg), app.account)
    reply = await inc.wait(
        (
            GroupMessageWaiter(event.sender.group, event.sender)
            if isinstance(event, GroupMessage)
            else FriendMessageWaiter(event.sender)
        ),
        timeout=60,
    )
    return reply.message_chain.display


def _parse_github_reply(reply: str) -> str:
    mgr_cfg: ManagerConfig = create(ManagerConfig)
    owner, repo = reply.split("/")
    branch = ""
    if ":" in repo:
        repo, branch = repo.split(":")
    branch = branch or "modules"
    mgr_cfg.register_repo("github", owner, repo, branch)
    return f"已注册仓库 {owner}/{repo}:{branch}"


def _parse_http_reply(reply: str) -> str:
    mgr_cfg: ManagerConfig = create(ManagerConfig)
    mgr_cfg.register_repo("http", reply)
    return f"已注册仓库 {reply}"


async def wait_and_register(app: Ariadne, event: MessageEvent):
    await send_message(
        event,
        MessageChain("请在一分钟内发送需要注册的仓库类型 (github/gitlab/http)"),
        app.account,
    )
    repo_type = await _wait_for_repo_type(event)
    # TODO implement GitLab
    reply = await _wait_for_reply(
        (
            "请在一分钟内发送需要注册的仓库地址\n"
            "示例：owner/repo\n"
            "示例：owner/repo:branch\n"
            '如未填写分支，则将使用默认分支 "modules"'
            if repo_type == "github"
            else "请在一分钟内发送需要注册的仓库地址\n示例：example.com"
        ),
        app,
        event,
    )
    msg = (_parse_github_reply if repo_type == "github" else _parse_http_reply)(reply)
    it(ParsedRepository).__init__()
    return msg
