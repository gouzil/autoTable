from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrackerIssuesData:
    issue_title: str
    issue_content: str
    issue_create_time: datetime | None
    issue_comments: list[IssuesCommentData] | None
    owner_repo: str

    def __hash__(self) -> int:
        return hash(self.issue_title) + hash(self.issue_create_time) + hash(self.owner_repo)


@dataclass(frozen=True)
class IssuesCommentData:
    id: int
    body: str
    url: str
    user_login: str

    def __hash__(self) -> int:
        return hash(self.id) + hash(self.body) + hash(self.user_login)
