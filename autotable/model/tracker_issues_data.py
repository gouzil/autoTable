from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from github.IssueComment import IssueComment
from github.PaginatedList import PaginatedList


@dataclass(frozen=True)
class TrackerIssuesData:
    issue_title: str
    issue_content: str
    issue_create_time: datetime
    issue_comments: PaginatedList[IssueComment]
