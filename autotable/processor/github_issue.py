from __future__ import annotations

from github.IssueComment import IssueComment
from github.PaginatedList import PaginatedList
from mistletoe.block_token import Table


def update_issue_table(table: Table, issue_comments: PaginatedList[IssueComment]) -> Table:
    return table
