from __future__ import annotations

from github import Auth, Github
from github.Issue import Issue
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from github.Repository import Repository


class Fetcher:
    gh: Github | None
    repo: Repository | None

    @classmethod
    def set_github(cls, token: str) -> None:
        Fetcher.gh = Github(auth=Auth.Token(token), per_page=100) # 最大直接设置到100最大值

    @classmethod
    def get_github(cls) -> Github:
        return cls.gh

    @classmethod
    def set_repo(cls, repo: str) -> None:
        cls.repo = cls.gh.get_repo(repo)

    @classmethod
    def get_issue(cls, issues_id:int) -> Issue:
        return cls.repo.get_issue(issues_id)

    @classmethod
    def get_pr_list(cls, repo: str) -> PaginatedList[PullRequest]:
        repo_: Repository = cls.repo
        if repo:
            repo_ = cls.gh.get_repo(repo)
        return repo_.get_pulls()

