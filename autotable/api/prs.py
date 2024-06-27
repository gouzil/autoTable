from __future__ import annotations

import asyncio
import re
from contextlib import contextmanager
from datetime import datetime

from loguru import logger

from autotable.storage_model.pull_data import PullRequestData, PullReviewData
from autotable.utils.fetcher import Fetcher


def get_pr_list(start_time: datetime, title_re: str, repo: str = "") -> list[PullRequestData]:
    """
    筛选出符合条件的pull request
    """
    with _temp_set_owner_repo(repo):
        res = asyncio.run(_request_pull_list_data(start_time, title_re))

    logger.debug(f"pr list:{res[::-1]}")
    # 逆序 pr 号小的在前
    return res[::-1]


async def _request_pull_list_data(start_time: datetime, title_re: str):
    """
    异步获取pull request列表, 并筛选出符合条件的pull request
    """
    res: list[PullRequestData] = []
    async for pr in Fetcher.get_github().paginate(
        Fetcher.get_github().rest.pulls.async_list,
        owner=Fetcher.get_owner(),
        repo=Fetcher.get_repo(),
        state="all",
        sort="created",
        direction="desc",
        per_page=100,
    ):
        if not pr.created_at > start_time:
            logger.debug(f"end request pr number: {pr.number}")
            break
        # 如果正则匹配上了就会加入队列
        if re.search(title_re, pr.title):
            reviews_data: list[PullReviewData] = []
            # 获取评论
            async for review in Fetcher.get_github().paginate(
                Fetcher.get_github().rest.pulls.async_list_reviews,
                pull_number=pr.number,
                owner=pr.base.repo.owner.login,
                repo=pr.base.repo.name,
            ):
                assert review.commit_id is not None
                assert review.user is not None
                reviews_data.append(PullReviewData(review.commit_id, review.state, review.body, review.user.login))

            assert pr.user is not None
            res.append(
                PullRequestData(
                    pr.number,
                    pr.title,
                    pr.base.repo.full_name,
                    pr.user.login,
                    pr.state,
                    pr.merged_at is not None,
                    reviews_data,
                )
            )

    return res


@contextmanager
def _temp_set_owner_repo(owner_repo: str):
    """
    用于临时请求其他repo
    """
    old_owner = Fetcher.get_owner()
    old_repo = Fetcher.get_repo()
    if owner_repo != "":
        Fetcher.set_owner_repo(owner_repo)
    yield
    Fetcher.set_owner(old_owner)
    Fetcher.set_repo(old_repo)
