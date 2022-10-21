from pathlib import Path

from git import Repo, Commit, Head


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
