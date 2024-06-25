from __future__ import annotations

import re

from loguru import logger
from mistletoe.block_token import Table
from mistletoe.span_token import RawText, Strikethrough

from autotable.autotable_type.autotable_type import StatusType
from autotable.autotable_type.github_type import PrType, get_pr_type
from autotable.constant import global_error_prs, global_pr_reviews_cache, global_pr_title_index_cache
from autotable.processor.analysis import analysis_review, analysis_table_more_people
from autotable.processor.github_title import titleBase
from autotable.processor.utils import update_table_people
from autotable.storage_model.pull_data import PullRequestData, PullReviewData

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


def update_pr_table(table: Table, title_re: str, prs: list[PullRequestData]) -> Table:
    # 记录已经关闭了的号码
    close_prs: set[PullRequestData] = set()

    for table_row in table.children:
        # 跳过已经删除的行
        if isinstance(table_row.children[0].children[0], Strikethrough):
            continue

        assert isinstance(table_row.children[0].children[0], RawText)
        assert isinstance(table_row.children[0].children[0].content, str)
        assert not table_row.children[0].children[0].content.startswith("~")
        index: str = table_row.children[0].children[0].content

        # 查找pr列表
        for pr in prs:
            # 转换为自己的类型
            pr_state: PrType = get_pr_type(pr)
            # 跳过已经关闭了的pr
            if pr_state is PrType.CLOSED:
                close_prs.add(pr)
                continue

            if (
                global_pr_title_index_cache.setdefault(pr.base_repo_full_name, {}) == {}
                or pr.number not in global_pr_title_index_cache[pr.base_repo_full_name]
            ):
                # NOTE: 直接使用 match 会与 search 的不一致
                pr_title = re.search(title_re, pr.title)
                assert pr_title is not None
                pr_indexs_re = re.match(title_re, pr_title.group())

                if pr_indexs_re is None:
                    if pr not in global_error_prs.setdefault(pr.base_repo_full_name, set()):
                        global_error_prs[pr.base_repo_full_name].add(pr)
                        logger.warning(f"{pr.number} Parsing title error, title: {pr.title}")
                    continue

                pr_indexs_text = pr_indexs_re.group("task_id")

                # 防止一些不是序号的标题
                try:
                    pr_index_list: list[str] = titleBase(pr_indexs_text).distribution_parser().mate()
                except RuntimeError:
                    if pr not in global_error_prs.setdefault(pr.base_repo_full_name, set()):
                        global_error_prs[pr.base_repo_full_name].add(pr)
                        logger.warning(f"{pr.number} Parsing title error, title: {pr.title}")
                    continue
                global_pr_title_index_cache[pr.base_repo_full_name][pr.number] = pr_index_list
            else:
                pr_index_list = global_pr_title_index_cache[pr.base_repo_full_name][pr.number]

            # 如果与序号不匹配跳过
            if index[1:] not in pr_index_list:
                continue

            # 只有 reviews 的状态是 APPROVED 才是需要判断的
            pr_reviews: list[PullReviewData] = []
            # 如果没有缓存则获取
            if pr.number not in global_pr_reviews_cache.setdefault(pr.base_repo_full_name, {}):
                for x in pr.get_reviews():
                    if x.state == "APPROVED":
                        pr_reviews.append(x)
                global_pr_reviews_cache[pr.base_repo_full_name][pr.number] = pr_reviews
            else:
                pr_reviews = global_pr_reviews_cache[pr.base_repo_full_name][pr.number]

            # 确认状态, 当前行的状态, 第一位永远为状态位
            status: StatusType = pr_match_status(pr_state, pr_reviews, index)

            # 设置序号状态
            table_row.children[0].children[0].content = f"{status.value}{index[1:]}"

            # 更新 pr 号
            if len(table_row.children[-1].children) == 0:
                table_row.children[-1].children.append(RawText(""))
            table_row.children[-1].children[0].content = update_pr_url(
                table_row.children[-1].children[0].content, pr, close_prs
            )

            # 更新认领人
            if len(table_row.children[-2].children) == 0:
                table_row.children[-2].children.append(RawText(""))

            table_row.children[-2].children[0].content = update_table_people(
                status, pr.user_login, table_row.children[-2].children[0].content
            )

    return table


def pr_match_status(pr_state: PrType, pr_reviews: list[PullReviewData], table_content: str) -> StatusType:
    """
    匹配pr类型到表格状态

    优先级: review > pr状态 > 表单原有内容
    """
    res_type = StatusType(table_content[0])

    # 内容截取转换, 比对
    pr_state_: StatusType = pr_state.match_pr_table()
    # pr_state_ > res_type
    # 🚧 > 🔵
    # 🚧 > 🙋
    if pr_state_ > res_type:
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


def update_pr_url(table_row: str, pr: PullRequestData, close_prs: set[PullRequestData]) -> str:
    """更新 pr 号, 倒数第一列为 pr 号列, 根据是否为其他仓库决定是否使用 http 链接"""
    table_pr_num: str = ""
    pr_table_list = [f"{pr.base_repo_full_name}#{pr.number}"]
    pr_table_list.extend(analysis_table_more_people(table_row))
    pr_table_list = list(set(pr_table_list))
    if len(pr_table_list) == 1:
        table_pr_num = pr_table_list[0]
    else:
        for pr_table in pr_table_list:
            # 不生成关闭的pr
            if pr_table in [f"{x.base_repo_full_name}#{x.number}" for x in close_prs]:
                continue
            table_pr_num += f"{pr_table}<br/>"

    return table_pr_num
