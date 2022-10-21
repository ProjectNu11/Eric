from pathlib import Path

from git import Repo, Commit, Head


def get_current_repo() -> Repo | None:
    if (git_path := Path.cwd() / ".git").exists() and git_path.is_dir():
        return Repo(Path.cwd())
    return None


def get_current_commit(repo: Repo) -> Commit:
    return next(repo.iter_commits())


def get_current_branch(repo: Repo) -> Head:
    return repo.active_branch
