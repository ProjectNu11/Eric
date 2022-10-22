import re
from pathlib import Path

from aiohttp import ClientSession
from git import Repo, Commit, Head
from kayaku import create

from library.model.config.eric import EricConfig


def get_current_repo() -> Repo | None:
    if (git_path := Path.cwd() / ".git").exists() and git_path.is_dir():
        return Repo(Path.cwd())
    return None


def get_current_commit(repo: Repo) -> Commit:
    try:
        return next(repo.iter_commits())
    except StopIteration as e:
        raise RuntimeError("无法获取当前提交，请检查当前目录是否为 Git 仓库") from e


def get_current_branch(repo: Repo) -> Head:
    return repo.active_branch


def get_github_repo(repo: Repo) -> str:
    return re.search(r"(?<=github.com/).+?(?=\.git)", repo.remote().url).group()


async def get_remote_commit_sha(repo: str, branch: str) -> str:
    link = f"https://api.github.com/repos/{repo}/commits/{branch}"
    config: EricConfig = create(EricConfig)
    async with ClientSession() as session:
        async with session.get(link, proxy=config.proxy) as resp:
            return (await resp.json()).get("sha", "")


async def compare_commits(repo: str, base: str, head: str) -> list[dict]:
    link = f"https://api.github.com/repos/{repo}/compare/{base}...{head}"
    config: EricConfig = create(EricConfig)
    async with ClientSession() as session:
        async with session.get(link, proxy=config.proxy) as resp:
            return (await resp.json()).get("commits", [])


async def check_update() -> list[dict]:
    repo = get_current_repo()
    if repo is None:
        return []
    current_commit = get_current_commit(repo)
    current_branch = get_current_branch(repo)
    github_repo = get_github_repo(repo)
    remote_commit_sha = await get_remote_commit_sha(github_repo, current_branch.name)
    if remote_commit_sha == current_commit.hexsha:
        return []
    history = await compare_commits(
        github_repo, current_commit.hexsha, remote_commit_sha
    )
    history.reverse()
    return history


def perform_update():
    repo = get_current_repo()
    if repo is None:
        return
    repo.remotes.origin.pull()
