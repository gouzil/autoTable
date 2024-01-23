from __future__ import annotations

from typing import TYPE_CHECKING

from mistletoe.block_token import Table
from mistletoe.span_token import RawText

from autotable.autotable_type.autotable_type import StatusType
from autotable.autotable_type.github_type import PrType, get_pr_type
from autotable.processor.analysis import analysis_review, analysis_table_more_people
from autotable.processor.github_title import titleBase
from autotable.storage_model.table import TablePeople, TablePr
from autotable.utils.strtool import str_translate

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


def update_pr_table(table: Table, title_identifier: str, prs: PaginatedList[PullRequest]) -> Table:
    # 中英符号转换
    title_start = str_translate(title_identifier[:-1])
    title_end = str_translate(title_identifier[-1])

    # 获取第一个编号, 这里取第二位是因为第一位是状态位
    # 防止第一个任务是删除任务: ~🔵1~
    if table.children[0].children[0].children[0].content[0] == "~":
        table_start_index = int(table.children[0].children[0].children[0].content[2:-1])
    else:
        table_start_index = int(table.children[0].children[0].children[0].content[1:])

    # 记录pr号码
    # pr.number
    close_number: list[int] = []

    for pr in prs:
        # 转换为自己的类型
        pr_state: PrType = get_pr_type(pr)
        if pr_state is PrType.CLOSED:
            close_number.append(pr.number)
            continue

        # 中英符号转换
        title = str_translate(pr.title)
        # 截取标题的有用信息
        pr_title = title[title.find(title_start) + len(title_start) : title.find(title_end)]
        # 获取编号
        pr_index: list[int] = titleBase(pr_title).distribution_parser().mate()
        # 获取reviews
        pr_reviews: PaginatedList[PullRequestReview] = pr.get_reviews()

        for index in pr_index:
            # pr标题中的编号 - 表格开头的第一个编号 = 当前数据的索引
            table_index = index - table_start_index
            table_content: str = table.children[table_index].children[0].children[0].content
            # 题号删除不更新
            if "~" in table_content:
                continue

            # 检查值是否一致 (一致代表顺序, 不重复, 且中间没有跳号)
            assert int(table_content[1:]) == index

            # 确认状态
            status: StatusType = pr_match_status(pr_state, pr_reviews, table_content)

            # 设置序号状态
            table.children[table_index].children[0].children[0].content = f"{status.value}{index}"

            # 更新 pr 号
            # 倒数第一列为 pr 号列
            if len(table.children[table_index].children[-1].children) == 0:
                table.children[table_index].children[-1].children.append(RawText(""))
            table_pr_index: str = table.children[table_index].children[-1].children[0].content
            # 这里直接处理成 pr 号处理
            pr_table_list: list[int] = [pr.number]
            pr_table_list.extend([int(x[1:]) for x in analysis_table_more_people(table_pr_index)])
            pr_table_list = list(set(pr_table_list))
            table_pr_num = ""
            if len(pr_table_list) == 1:
                table_pr_num = f"#{pr_table_list[0]}"
            else:
                for pr_table in pr_table_list:
                    # 不生成关闭的pr
                    if pr_table in close_number:
                        continue
                    table_pr_num += f"#{pr_table}</br>"

            table.children[table_index].children[-1].children[0].content = table_pr_num

            # 更新认领人状态
            # 倒数第二列为认领人列
            if len(table.children[table_index].children[-2].children) == 0:
                table.children[table_index].children[-2].children.append(RawText(""))
            table_claim_people: str = table.children[table_index].children[-2].children[0].content
            # 处理人名
            # 第一位是@位, 第二位是状态位
            people_names: list[TablePeople] = [TablePeople(pr_state.match_pr_table(), pr.user.login)]
            people_names.extend(
                [TablePeople(StatusType(x[0]), x[2:]) for x in analysis_table_more_people(table_claim_people)]
            )
            people_names = list(set(people_names))
            table_people_names = ""
            if len(people_names) == 1:
                table_people_names = f"{people_names[0].status.value}@{people_names[0].github_id}"
            else:
                for people in people_names:
                    table_people_names += f"{people.status.value}@{people.github_id}</br>"

            table.children[table_index].children[-2].children[0].content = table_people_names

    return table


# 理想状态
"""
| 🔵1 | test_varname_inplace_ipu.py | 🚧@gouzil</br>🚧@gouzil | 🟢#123</br>🚧#456 |
"""


def pr_match_status(pr_state: PrType, pr_reviews: PaginatedList[PullRequestReview], table_content: str) -> StatusType:
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
