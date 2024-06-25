from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PullRequestData:
    number: int
    title: str
    base_repo_full_name: str
    user_login: str
    state: str
    merged: bool
    reviews: list[PullReviewData]

    # 原始pygithub数据
    # NOTE: 这里如果使用原始数据, 还是会导致使用 pygithub 的问题
    # origin_data: PullRequest

    # 其实只需要计算number就可以了
    def __hash__(self) -> int:
        return hash(self.number) + hash(self.title) + hash(self.state)

    def get_reviews(self):
        return self.reviews


@dataclass(frozen=True)
class PullReviewData:
    commit_id: str
    state: str
    body: str
    user_login: str
    # origin_data: PullRequest  # 原始pygithub数据

    def __hash__(self) -> int:
        return hash(self.commit_id) + hash(self.state)
