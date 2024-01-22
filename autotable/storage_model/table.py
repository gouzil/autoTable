from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType


class TablePr:
    status: StatusType
    pr_num: int

    def __init__(self, status: StatusType, pr_num: int) -> None:
        self.status = status
        self.pr_num = pr_num


class TablePeople:
    status: StatusType
    github_id: str

    def __init__(self, status: StatusType, github_id: str) -> None:
        self.status = status
        self.github_id = github_id
