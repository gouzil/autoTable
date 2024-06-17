from __future__ import annotations

from mistletoe.block_token import Table
from mistletoe.span_token import Strikethrough

from autotable.processor.analysis import analysis_table_more_people


def migrate_pr_url_02to03(doc_table: Table, repo_fall_name: str) -> Table:
    for table_row in doc_table.children:
        # 跳过空行
        if len(table_row.children[-1].children) == 0:
            continue

        if isinstance(table_row.children[-1].children[0], Strikethrough):
            pr_content: str = table_row.children[-1].children[0].children[0].content
        else:
            pr_content: str = table_row.children[-1].children[0].content

        res_pr_content: str = ""
        for index, pr_ in enumerate(analysis_table_more_people(pr_content)):
            if index == 1:
                res_pr_content += "<br/>"
            if pr_.startswith("#"):
                res_pr_content += f"{repo_fall_name}{pr_}"
            elif pr_.startswith("https://"):
                res_pr_content += pr_.replace("https://github.com/", "").replace("/pull/", "#")
            if index > 0:
                res_pr_content += "<br/>"

        # 替换回去
        if isinstance(table_row.children[-1].children[0], Strikethrough):
            table_row.children[-1].children[0].children[0].content = res_pr_content
        else:
            table_row.children[-1].children[0].content = res_pr_content

    return doc_table
