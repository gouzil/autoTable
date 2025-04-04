from __future__ import annotations

from datetime import datetime

from autotable.storage_model import IssuesCommentData, TrackerIssuesData
from autotable.utils.async_exe import async_run
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

    issue_comments: list[IssuesCommentData] = async_run(_get_issue_comments(issues_id))

    return TrackerIssuesData(
        issue_title=issue.title,
        issue_content=issue.body,
        issue_create_time=issue.created_at,
        issue_comments=issue_comments,
        owner_repo=Fetcher.get_owner_repo(),
    )


async def _get_issue_comments(
    issues_id: int,
) -> list[IssuesCommentData]:
    """
    获取issue评论
    """

    issue_comments: list[IssuesCommentData] = []

    async for comment in Fetcher.get_github().paginate(
        Fetcher.get_github().rest.issues.async_list_comments,
        owner=Fetcher.get_owner(),
        repo=Fetcher.get_repo(),
        issue_number=issues_id,
        per_page=100,
    ):
        assert comment.user is not None
        issue_comments.append(IssuesCommentData(comment.id, comment.body, comment.url, comment.user.login))
    return issue_comments
