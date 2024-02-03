from __future__ import annotations

import re
from typing import TYPE_CHECKING

from loguru import logger
from mistletoe.block_token import Table
from mistletoe.span_token import RawText

from autotable.autotable_type.autotable_type import StatusType
from autotable.autotable_type.github_type import PrType, get_pr_type
from autotable.processor.analysis import analysis_review, analysis_table_more_people
from autotable.processor.github_title import titleBase
from autotable.storage_model.table import TablePeople

if TYPE_CHECKING:
    from github.PaginatedList import PaginatedList
    from github.PullRequest import PullRequest
    from github.PullRequestReview import PullRequestReview

"""
table.header:
|                     序号                        |                     文件位置                     |  认领人  |  PR  |
| {table.header.children[0].children[0].content} |  {table.header.children[1].children[0].content} |

table.children:
|                          🔵1                        | test_varname_inplace_ipu.py | @gouzil  | #123 |
| {table.children[0].children[0].children[0].content} | {table.children[0].children[1].children[0].content} |
|                          🔵2                        | test_eval_model_ipu.py | @gouzil | #456 |
| {table.children[1].children[0].children[0].content} | {table.children[1].children[1].children[0].content} |
"""


def update_pr_table(table: Table, title_re: str, prs: PaginatedList[PullRequest]) -> Table:
    # 记录已经关闭了的号码
    close_number: set[int] = set()

    for table_row in table.children:
        index: str = table_row.children[0].children[0].content
        # 跳过已经删除的行
        if "~" in index:
            continue

        # 查找pr列表
        for pr in prs:
            # 转换为自己的类型
            pr_state: PrType = get_pr_type(pr)
            # 跳过已经关闭了的pr
            if pr_state is PrType.CLOSED:
                close_number.add(pr.number)
                continue

            pr_indexs_re = re.match(title_re, pr.title)

            if pr_indexs_re is None:
                logger.error(f"{pr.number} Parsing title error")
                continue

            pr_indexs_text = pr_indexs_re.group("task_id")
            pr_index_list: list[str] = titleBase(pr_indexs_text).distribution_parser().mate()

            # 如果与序号不匹配跳过
            if index[1:] not in pr_index_list:
                continue
            pr_reviews: list[PullRequestReview] = []
            for x in pr.get_reviews():
                if x.state == "APPROVED":
                    pr_reviews.append(x)

            # 确认状态, 当前行的状态, 第一位永远为状态位
            status: StatusType = pr_match_status(pr_state, pr_reviews, index)

            # 设置序号状态
            table_row.children[0].children[0].content = f"{status.value}{index[1:]}"

            # 更新 pr 号, 倒数第一列为 pr 号列
            if len(table_row.children[-1].children) == 0:
                table_row.children[-1].children.append(RawText(""))
            pr_table_list: list[int] = [pr.number]
            pr_table_list.extend(
                [int(x[1:]) for x in analysis_table_more_people(table_row.children[-1].children[0].content)]
            )
            pr_table_list = list(set(pr_table_list))
            table_pr_num: str = ""
            if len(pr_table_list) == 1:
                table_pr_num = f"#{pr_table_list[0]}"
            else:
                for pr_table in pr_table_list:
                    # 不生成关闭的pr
                    if pr_table in close_number:
                        continue
                    table_pr_num += f"#{pr_table}<br/>"

            table_row.children[-1].children[0].content = table_pr_num

            # 更新认领人
            if len(table_row.children[-2].children) == 0:
                table_row.children[-2].children.append(RawText(""))
            # 处理人名
            # 第一位是@位, 第二位是状态位
            people_names: list[TablePeople] = [TablePeople(status, pr.user.login)]
            people_names.extend(
                [
                    TablePeople(StatusType(x[0]), x[2:])
                    for x in analysis_table_more_people(table_row.children[-2].children[0].content)
                ]
            )
            people_names = TablePeople_list_repeat(people_names)
            table_people_names: str = ""
            if len(people_names) == 1:
                table_people_names = f"{people_names[0].status.value}@{people_names[0].github_id}"
            else:
                for people in people_names:
                    table_people_names += f"{people.status.value}@{people.github_id}<br/>"

            table_row.children[-2].children[0].content = table_people_names

    return table


# 理想状态
"""
| 🔵1 | test_varname_inplace_ipu.py | 🚧@gouzil</br>🚧@gouzil | 🟢#123</br>🚧#456 |
"""


def pr_match_status(pr_state: PrType, pr_reviews: list[PullRequestReview], table_content: str) -> StatusType:
    """
    匹配pr类型到表格状态

    优先级: review > pr状态 > 表单原有内容
    """
    res_type = StatusType(table_content[0])

    # 内容截取转换, 比对
    pr_state_: StatusType = pr_state.match_pr_table()
    # pr_state_ > res_type
    # 🚧 > 🔵
    if pr_state_.compare(res_type):
        res_type = pr_state_

    # 截取reviews中的单独设置
    pr_reviews_count = 0  # 如果有review, 且没有标记🟡
    for review in pr_reviews:
        pr_reviews_count += 1
        review_indexs_str: str | None = analysis_review(review.body)
        if review_indexs_str is None:
            continue
        assert isinstance(review_indexs_str, str)
        review_indexs: list[str] = [str(x) for x in titleBase(review_indexs_str).distribution_parser().mate()]
        # 如果表格编号在 review 里则标记🟡
        if table_content[1:] in review_indexs:
            # 转为下一步确认
            return StatusType.NEXT_STAGE

    # 如果 review 不为空, 且 pr 状态不是 merged
    if pr_reviews_count != 0 and pr_state_ != StatusType.COMPLETED:
        return StatusType.PENDING_MERGE

    return res_type


# TablePeople 去重, 这里会调整状态
def TablePeople_list_repeat(TablePeople_list: list[TablePeople]) -> list[TablePeople]:
    res: list[TablePeople] = []
    for people in TablePeople_list:
        write = True
        for res_index, res_data in enumerate(res):
            if people.github_id == res_data.github_id and people.status == res_data.status:
                write = False
                break
            if people.github_id != res_data.github_id:
                continue
            # 取较大的那个状态更新
            if res_data.status.compare(people.status):
                write = False
            else:
                res[res_index].status = people.status
                write = False
        if write:
            res.append(people)

    return res
