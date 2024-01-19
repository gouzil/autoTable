from __future__ import annotations

from typing import TYPE_CHECKING

from mistletoe.block_token import Table

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.github_title import titleBase

if TYPE_CHECKING:
    from github.PaginatedList import PaginatedList
    from github.PullRequest import PullRequest

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


def update_table(table: Table, title_identifier: str, prs: PaginatedList[PullRequest]) -> Table:
    title_start = title_identifier[:-1]
    title_end = title_identifier[-1]

    # 获取第一个编号, 这里取第二位是因为第一位是状态位
    table_start_index = int(table.children[0].children[0].children[0].content[1:])

    for i in prs:
        # 截取标题的有用信息
        pr_title = i.title[i.title.find(title_start) + len(title_start) : i.title.find(title_end)]
        # 获取编号
        pr_index: list[int] = titleBase(pr_title).distribution_parser().mate()

        for index in pr_index:
            # pr标题中的编号 - 表格开头的第一个编号 = 当前数据的索引
            table_index = index - table_start_index
            # 检查值是否一致 (一致代表顺序, 不重复, 且中间没有跳号)
            assert int(table.children[table_index].children[0].children[0].content[1:]) == index
            table.children[table_index].children[0].children[0].content = f"{status}{index}"

    return table
