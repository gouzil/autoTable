from __future__ import annotations

from githubkit import GitHub, TokenAuthStrategy, UnauthAuthStrategy
from githubkit.retry import RETRY_RATE_LIMIT, RETRY_SERVER_ERROR, RetryChainDecision
from githubkit.versions.latest.models import Issue

OWNER_REPO_SPLIT = 2


class Fetcher:
    gh: GitHub | None
    owner: str | None
    repo: str | None

    @classmethod
    def set_github(cls, token: str) -> None:
        if token == "":
            cls.gh = GitHub(
                accept_format="application/json",
                auth=UnauthAuthStrategy(),
                auto_retry=RetryChainDecision(RETRY_RATE_LIMIT, RETRY_SERVER_ERROR),
                http_cache=True,
            )
        else:
            cls.gh = GitHub(
                accept_format="application/json",
                auth=TokenAuthStrategy(token),
                auto_retry=RetryChainDecision(RETRY_RATE_LIMIT, RETRY_SERVER_ERROR),
                http_cache=True,
            )

    @classmethod
    def get_github(cls) -> GitHub:
        assert cls.gh is not None
        return cls.gh

    @classmethod
    def set_repo(cls, repo: str) -> None:
        cls.repo = repo

    @classmethod
    def get_repo(cls) -> str:
        assert cls.repo is not None
        return cls.repo

    @classmethod
    def set_owner(cls, owner: str) -> None:
        cls.owner = owner

    @classmethod
    def get_owner(cls) -> str:
        assert cls.owner is not None
        return cls.owner

    @classmethod
    def set_owner_repo(cls, owner_repo: str) -> None:
        res = owner_repo.split("/")
        assert len(res) == OWNER_REPO_SPLIT
        cls.owner = res[0]
        cls.repo = res[1]
        cls.check_owner_repo()

    @classmethod
    def get_owner_repo(cls) -> str:
        assert cls.owner is not None
        assert cls.repo is not None
        return f"{cls.owner}/{cls.repo}"

    @classmethod
    def get_issue(cls, issues_id: int) -> Issue:
        assert cls.gh is not None
        return cls.gh.rest.issues.get(cls.get_owner(), cls.get_repo(), issues_id).parsed_data

    @classmethod
    def set_issue(cls, issues_id: int, issue_content: str) -> None:
        assert cls.gh is not None
        assert cls.repo is not None
        cls.gh.rest.issues.update(cls.get_owner(), cls.get_repo(), issues_id, body=issue_content)

    # 所有的 set repo 都应该使用这个函数, 防止大小写问题
    @classmethod
    def check_owner_repo(cls):
        assert cls.owner is not None and cls.repo is not None
        assert cls.gh is not None
        res = cls.gh.rest.repos.get(cls.owner, cls.repo).parsed_data
        cls.owner = res.owner.login
        cls.repo = res.name
