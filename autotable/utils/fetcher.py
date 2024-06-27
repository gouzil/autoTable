from __future__ import annotations

from githubkit import GitHub, TokenAuthStrategy, UnauthAuthStrategy
from githubkit.retry import RETRY_RATE_LIMIT, RETRY_SERVER_ERROR, RetryChainDecision
from githubkit.versions.latest.models import Issue


class Fetcher:
    gh: GitHub | None
    owner: str | None
    repo: str | None

    @classmethod
    def set_github(cls, token: str) -> None:
        if token == "":
            cls.gh = GitHub(
                auth=UnauthAuthStrategy(),
                auto_retry=RetryChainDecision(RETRY_RATE_LIMIT, RETRY_SERVER_ERROR),
                http_cache=True,
            )
        else:
            cls.gh = GitHub(
                auth=TokenAuthStrategy(token),
                auto_retry=RetryChainDecision(RETRY_RATE_LIMIT, RETRY_SERVER_ERROR),
                http_cache=True,
            )  # 最大直接设置到100最大值

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
        assert len(res) == 2
        cls.owner = res[0]
        cls.repo = res[1]

    @classmethod
    def get_issue(cls, issues_id: int) -> Issue:
        assert cls.gh is not None
        return cls.gh.rest.issues.get(cls.get_owner(), cls.get_repo(), issues_id).parsed_data

    @classmethod
    def set_issue(cls, issues_id: int, issue_content: str) -> None:
        assert cls.gh is not None
        assert cls.repo is not None
        cls.gh.rest.issues.update(cls.get_owner(), cls.get_repo(), issues_id, body=issue_content)
