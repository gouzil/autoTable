from __future__ import annotations

from datetime import datetime

from github.IssueComment import IssueComment
from github.PaginatedList import PaginatedList

from autotable.utils.fetcher import Fetcher


def get_issues(
    issues_id: int,
) -> tuple[str, str, datetime, PaginatedList[IssueComment]]:
    """
    返回:
        issue.title: 标题
        issue.body: 内容
        issue.create_time: 创建时间
        issue.comments: 获取评论
    """
    issue = Fetcher.get_issue(issues_id)
    assert isinstance(issue.title, str)
    assert isinstance(issue.body, str)
    assert isinstance(issue.created_at, datetime)
    return issue.title, issue.body, issue.created_at, issue.get_comments()
