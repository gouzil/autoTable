from __future__ import annotations

import re

from loguru import logger
from mistletoe.block_token import Table
from mistletoe.span_token import RawText, Strikethrough

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.github_title import TitleBase
from autotable.processor.utils import update_table_people
from autotable.storage_model.tracker_issues_data import IssuesCommentData


def update_issue_table(table: Table, issue_comments: list[IssuesCommentData], enter_re: re.Pattern) -> Table:
    for table_row in table.children:
        if isinstance(table_row.children[0].children[0], Strikethrough):
            continue

        assert isinstance(table_row.children[0].children[0], RawText)
        assert isinstance(table_row.children[0].children[0].content, str)
        assert not table_row.children[0].children[0].content.startswith("~")
        index: str = table_row.children[0].children[0].content

        for issue in issue_comments:
            if enter_re.search(issue.body) is None:
                logger.debug(f"skip {issue.url}")
                continue

            enter_indexs = enter_re.match(issue.body)
            if enter_indexs is None:
                logger.debug(f"Matching failed skip {issue.url}")
                continue

            # 如果标题不匹配跳过
            enter_indexs_text = enter_indexs.group("task_id")
            enter_indexs_list: list[str] = TitleBase(enter_indexs_text).distribution_parser().mate()
            if index[1:] not in enter_indexs_list:
                continue

            # 更新序号
            # 当前序号
            status: StatusType = StatusType(index[0])

            if status < StatusType.CLAIMED:
                # 设置序号状态
                table_row.children[0].children[0].content = f"{StatusType.CLAIMED.value}{index[1:]}"

            # 更新认领人
            if len(table_row.children[-2].children) == 0:
                table_row.children[-2].children.append(RawText(""))

            table_row.children[-2].children[0].content = update_table_people(
                StatusType.CLAIMED, issue.user_login, table_row.children[-2].children[0].content
            )

    return table
