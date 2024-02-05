from __future__ import annotations

from typing import ClassVar

from autotable.autotable_type.autotable_type import StatusType


class TablePr:
    def __init__(self, status: StatusType, pr_num: int) -> None:
        self.status: StatusType = status
        self.pr_num: int = pr_num


class TablePeople:
    def __init__(self, status: StatusType, github_id: str) -> None:
        self.status: StatusType = status
        self.github_id: str = github_id

    def __eq__(self, __value: TablePeople) -> bool:
        return self.github_id == __value.github_id and self.status == __value.status


# 统计数据总会
class TableStatistics:
    status: ClassVar[dict[StatusType, int]] = {StatusKey: 0 for StatusKey in StatusType}
    all_merge: ClassVar[dict[str, int]] = {}
