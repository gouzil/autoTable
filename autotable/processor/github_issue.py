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
from autotable.utils.strtool import str_translate


def update_issue_table(table: Table, issue_comments: PaginatedList[IssueComment]) -> Table:
    for issue in issue_comments:
        if "报名" not in issue.body:
            continue

        issue_body = str_translate(issue.body)
        m = re.search(r"\d", issue_body)

        if not m:
            logger.debug(f"{{{issue.body}}} parse error")
            continue

        # 获取第一个编号, 这里取第二位是因为第一位是状态位
        # 防止第一个任务是删除任务: ~🔵1~
        if table.children[0].children[0].children[0].content[0] == "~":
            table_start_index = int(table.children[0].children[0].children[0].content[2:-1])
        else:
            table_start_index = int(table.children[0].children[0].children[0].content[1:])

        # issue 中报名的标题
        issue_indexs = titleBase(issue_body[m.start() :]).distribution_parser().mate()
        for index in issue_indexs:
            # pr标题中的编号 - 表格开头的第一个编号 = 当前数据的索引
            table_index = index - table_start_index
            # 更新认领人状态
            # 倒数第二列为认领人列
            if len(table.children[table_index].children[-2].children) == 0:
                table.children[table_index].children[-2].children.append(RawText(""))
            table_claim_people: str = table.children[table_index].children[-2].children[0].content
            # 处理人名
            # 第一位是@位, 第二位是状态位
            people_names: list[TablePeople] = [TablePeople(StatusType.CLAIMED, issue.user.login)]
            people_names.extend(
                [TablePeople(StatusType(x[0]), x[2:]) for x in analysis_table_more_people(table_claim_people)]
            )
            table_people_names = ""
            if len(people_names) == 1:
                table_people_names = f"{people_names[0].status.value}@{people_names[0].github_id}"
            else:
                for people in people_names:
                    # 这里全部以 pr 状态为主
                    if people.github_id not in table_claim_people:
                        table_people_names += f"{people.status.value}@{people.github_id}</br>"

            table.children[table_index].children[-2].children[0].content = table_people_names

    return table
