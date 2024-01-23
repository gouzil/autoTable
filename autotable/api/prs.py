from __future__ import annotations

from datetime import datetime

from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from loguru import logger

from autotable.utils.fetcher import Fetcher


def get_pr_list(start_time: datetime, start_title: str) -> PaginatedList[PullRequest]:
    """
    筛选出符合条件的pull request
    """
    res: PaginatedList[PullRequest] = []
    data: PaginatedList[PullRequest] = Fetcher.get_pr_list()
    for i in data:
        if not i.created_at > start_time:
            logger.debug(f"end request pr number: {i.number}")
            break
        if start_title in i.title:
            res.append(i)

    # 逆序 pr 号小的在前
    return res[::-1]
