from __future__ import annotations

import asyncio
import math
import re
from contextlib import contextmanager
from datetime import datetime

from githubkit.versions.latest.models import IssueSearchResultItem
from loguru import logger

from autotable.constant import global_request_pull_list_cache
from autotable.storage_model import PullRequestData, PullReviewData
from autotable.utils.async_exe import async_run
from autotable.utils.fetcher import Fetcher


def get_pr_list(
    start_time: datetime, title_re: re.Pattern, search_content: str, repo: str = ""
) -> list[PullRequestData]:
    """
    筛选出符合条件的pull request
    """
    with _temp_set_owner_repo(repo):
        if global_request_pull_list_cache.get(Fetcher.get_owner_repo()) is not None:
            return global_request_pull_list_cache[Fetcher.get_owner_repo()]
        res: list[PullRequestData] = async_run(_request_pull_list_data(start_time, title_re, search_content))
        global_request_pull_list_cache[Fetcher.get_owner_repo()] = res

    logger.debug(f"pr list:{res[::-1]}")
    # 逆序 pr 号小的在前
    return res[::-1]


async def _request_pull_list_data(
    start_time: datetime, title_re: re.Pattern, search_content: str
) -> list[PullRequestData]:
    """
    异步获取pull request列表, 并筛选出符合条件的pull request
    """
    res: list[PullRequestData] = []
    sem = asyncio.Semaphore(10)  # 限制并发数
    # Note: search_content 前面有一个空格, 用于分割 created 的内容
    q = f"is:pr repo:{Fetcher.get_owner_repo()} created:>=" + start_time.strftime("%Y-%m-%d") + f" {search_content}"
    search_res = (
        Fetcher.get_github()
        .rest.search.issues_and_pull_requests(
            q=q,
            sort="created",
            order="desc",
            per_page=100,
        )
        .parsed_data
    )

    # 创建并行列表
    search_res_items: list[IssueSearchResultItem] = search_res.items
    pr_tasks = []
    for page in range(2, math.ceil(search_res.total_count / 100) + 1):
        pr_tasks.append(asyncio.create_task(_next_page_search_pr(page, q, sem)))

    for pr_results in await asyncio.gather(*pr_tasks):
        search_res_items.extend(pr_results)

    # 临时存放需要的 pr, 的下标
    tmp_pr_index_list = []
    for index, pr in enumerate(search_res_items):
        # 如果正则匹配上了就会加入队列
        if title_re.search(pr.title):
            tmp_pr_index_list.append(index)

    # 获取评论
    pr_review_tasks = []
    pr_reviews = {}
    for index in tmp_pr_index_list:
        pr_review_tasks.append(asyncio.create_task(_get_reviews(search_res_items[index].number, sem)))

    # 把所有评论插入到一个大的字典中
    pr_reviews_results = await asyncio.gather(*pr_review_tasks)
    for review in pr_reviews_results:
        pr_reviews.update(review)

    for index in tmp_pr_index_list:
        pr: IssueSearchResultItem = search_res_items[index]

        assert pr.user is not None
        assert pr.pull_request is not None

        res.append(
            PullRequestData(
                pr.number,
                pr.title,
                Fetcher.get_owner_repo(),
                pr.user.login,
                pr.state,
                pr.pull_request.merged_at is not None,
                pr_reviews[pr.number],
            )
        )

    return res


async def _next_page_search_pr(page: int, q: str, sem) -> list[IssueSearchResultItem]:
    async with sem:
        search_res = await Fetcher.get_github().rest.search.async_issues_and_pull_requests(
            q=q,
            sort="created",
            order="desc",
            page=page,
            per_page=100,
        )
        return search_res.parsed_data.items


async def _get_reviews(pr_number: int, sem) -> dict[int, list[PullReviewData]]:
    async with sem:
        reviews_data: list[PullReviewData] = []
        # 获取评论
        async for review in Fetcher.get_github().paginate(
            Fetcher.get_github().rest.pulls.async_list_reviews,
            pull_number=pr_number,
            owner=Fetcher.get_owner(),
            repo=Fetcher.get_repo(),
        ):
            assert review.commit_id is not None
            assert review.user is not None
            reviews_data.append(PullReviewData(review.commit_id, review.state, review.body, review.user.login))
        return {pr_number: reviews_data}


@contextmanager
def _temp_set_owner_repo(owner_repo: str):
    """
    用于临时请求其他repo
    """
    old_owner_repo = Fetcher.get_owner_repo()
    if owner_repo != "":
        Fetcher.set_owner_repo(owner_repo)
    yield
    Fetcher.set_owner_repo(old_owner_repo)
