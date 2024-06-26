from __future__ import annotations

from datetime import datetime

from autotable.storage_model.tracker_issues_data import IssuesCommentData, TrackerIssuesData
from autotable.utils.fetcher import Fetcher


def get_issues(
    issues_id: int,
) -> TrackerIssuesData:
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

    issue_comments = [
        IssuesCommentData(comment.id, comment.body, comment.url, comment.user.login) for comment in issue.get_comments()
    ]

    return TrackerIssuesData(
        issue_title=issue.title,
        issue_content=issue.body,
        issue_create_time=issue.created_at,
        issue_comments=issue_comments,
        repo=issue.repository.full_name,
    )
