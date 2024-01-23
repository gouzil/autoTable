from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType


class TablePr:
    status: StatusType
    pr_num: int

    def __init__(self, status: StatusType, pr_num: int) -> None:
        self.status = status
        self.pr_num = pr_num

    def __eq__(self, __value: TablePr) -> bool:
        return self.pr_num == __value.pr_num

    def __hash__(self) -> int:
        return hash(self.pr_num)


class TablePeople:
    status: StatusType
    github_id: str

    def __init__(self, status: StatusType, github_id: str) -> None:
        self.status = status
        self.github_id = github_id

    def __eq__(self, __value: TablePeople) -> bool:
        return self.github_id == __value.github_id

    def __hash__(self) -> int:
        return hash(self.github_id)
