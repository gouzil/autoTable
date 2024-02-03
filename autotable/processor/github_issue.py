from __future__ import annotations

import re

from github.IssueComment import IssueComment
from github.PaginatedList import PaginatedList
from loguru import logger
from mistletoe.block_token import Table
from mistletoe.span_token import RawText

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.analysis import analysis_table_more_people
from autotable.processor.github_title import titleBase
from autotable.storage_model.table import TablePeople


def update_issue_table(table: Table, issue_comments: PaginatedList[IssueComment], enter_re: str) -> Table:
    for table_row in table.children:
        index: str = table_row.children[0].children[0].content

        for issue in issue_comments:
            if re.search(enter_re, issue.body) is None:
                logger.info(f"skip {issue.url}")
                continue

            enter_indexs = re.match(enter_re, issue.body)
            if enter_indexs is None:
                logger.error(f"Matching failed skip {issue.url}")
                continue

            # 如果标题不匹配跳过
            enter_indexs_text = enter_indexs.group("task_id")
            enter_indexs_list: list[str] = titleBase(enter_indexs_text).distribution_parser().mate()
            if index[1:] not in enter_indexs_list:
                continue

            # 更新认领人
            if len(table_row.children[-2].children) == 0:
                table_row.children[-2].children.append(RawText(""))
            # 处理人名
            # 第一位是@位, 第二位是状态位
            people_names: list[TablePeople] = [TablePeople(StatusType.CLAIMED, issue.user.login)]
            people_names.extend(
                [
                    TablePeople(StatusType(x[0]), x[2:])
                    for x in analysis_table_more_people(table_row.children[-2].children[0].content)
                ]
            )
            table_people_names: str = table_row.children[-2].children[0].content
            if len(people_names) == 1:
                table_people_names = f"{people_names[0].status.value}@{people_names[0].github_id}"
            else:
                for people in people_names:
                    # 这里全部以 pr 状态为主
                    if people.github_id not in table_people_names:
                        table_people_names += f"{people.status.value}@{people.github_id}</br>"

            table_row.children[-2].children[0].content = table_people_names

    return table
