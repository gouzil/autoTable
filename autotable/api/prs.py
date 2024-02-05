from __future__ import annotations

import re
from datetime import datetime

from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from loguru import logger

from autotable.utils.fetcher import Fetcher


def get_pr_list(start_time: datetime, title_re: str) -> PaginatedList[PullRequest]:
    """
    筛选出符合条件的pull request
    """
    res: PaginatedList[PullRequest] = []
    data: PaginatedList[PullRequest] = Fetcher.get_pr_list()
    for i in data:
        if not i.created_at > start_time:
            logger.debug(f"end request pr number: {i.number}")
            break
        # 如果正则匹配上了就会加入队列
        if re.search(title_re, i.title):
            res.append(i)

    # 逆序 pr 号小的在前
    return res[::-1]
