from __future__ import annotations

from typing import ClassVar

from github import Auth, Github
from github.Issue import Issue
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from github.Repository import Repository


class Fetcher:
    gh: Github | None
    repo: Repository | None
    # 对已经获取过的pr做缓存
    repo_pr_list: ClassVar[dict[str, PaginatedList[PullRequest]]] = {}

    @classmethod
    def set_github(cls, token: str) -> None:
        if token == "":
            cls.gh = Github(per_page=100)
        else:
            cls.gh = Github(auth=Auth.Token(token), per_page=100)  # 最大直接设置到100最大值

    @classmethod
    def get_github(cls) -> Github:
        assert cls.gh is not None
        return cls.gh

    @classmethod
    def set_repo(cls, repo: str) -> None:
        assert cls.gh is not None
        cls.repo = cls.gh.get_repo(repo)

    @classmethod
    def get_issue(cls, issues_id: int) -> Issue:
        assert cls.repo is not None
        return cls.repo.get_issue(issues_id)

    @classmethod
    def set_issue(cls, issues_id: int, issue_content: str) -> None:
        assert cls.repo is not None
        cls.repo.get_issue(issues_id).edit(body=issue_content)

    @classmethod
    def get_pr_list(cls, repo_name: str) -> PaginatedList[PullRequest]:
        assert cls.gh is not None
        assert cls.repo is not None

        repo_: Repository = cls.repo

        # 用于临时获取其他repo
        if repo_name != "":
            repo_ = cls.gh.get_repo(repo_name)
        else:
            repo_name = repo_.full_name
        cls.repo_pr_list.setdefault(repo_name, repo_.get_pulls(state="all"))
        return cls.repo_pr_list[repo_name]
