from __future__ import annotations

import re
from datetime import datetime

from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from loguru import logger

from autotable.storage_model.pull_data import PullRequestData, PullReviewData
from autotable.utils.fetcher import Fetcher


def get_pr_list(start_time: datetime, title_re: str, repo: str = "") -> list[PullRequestData]:
    """
    筛选出符合条件的pull request
    """
    res: list[PullRequestData] = []
    data: PaginatedList[PullRequest] = Fetcher.get_pr_list(repo)
    for i in data:
        if not i.created_at > start_time:
            logger.debug(f"end request pr number: {i.number}")
            break
        # 如果正则匹配上了就会加入队列
        if re.search(title_re, i.title):
            reviews_ = i.get_reviews()
            reviews_data = [
                PullReviewData(review.commit_id, review.state, review.body, review.user.login) for review in reviews_
            ]
            res.append(
                PullRequestData(i.number, i.title, i.base.repo.full_name, i.user.login, i.state, i.merged, reviews_data)
            )

    logger.debug(f"pr list:{res[::-1]}")
    # 逆序 pr 号小的在前
    return res[::-1]
