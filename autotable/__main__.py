from __future__ import annotations

import time
from typing import TYPE_CHECKING

import typer
from loguru import logger
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.style import Style

from autotable.api.issues import get_issues
from autotable.api.prs import get_pr_list
from autotable.processor.analysis import analysis_table, analysis_title
from autotable.processor.file import replace_table, save_file, to_markdown
from autotable.processor.github_issue import update_issue_table
from autotable.processor.github_prs import update_pr_table
from autotable.utils.fetcher import Fetcher

if TYPE_CHECKING:
    from github.PaginatedList import PaginatedList
    from github.PullRequest import PullRequest

app = typer.Typer()


def init_logger(log_level: str):
    handler = RichHandler(console=Console(style=Style()), highlighter=NullHighlighter(), markup=True)
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)
    logger.add("./logs/autotable.log", rotation="5MB", encoding="utf-8", enqueue=True, retention="10d")


@app.command()
def issue_update(
    repo: str,
    issues_id: int,
    token: str,
    start_str: str = "<!--task start bot-->",
    end_str: str = "<!--task end bot-->",
    log_level: str = "INFO",
):
    # 初始化日志
    init_logger(log_level)
    Fetcher.set_github(token)
    Fetcher.set_repo(repo)

    # 获取issue内容
    issue_title, issue_content, issue_create_time, issue_comments = get_issues(issues_id)
    # 解析表格
    doc_table = analysis_table(issue_content, start_str, end_str)
    # 解析任务开头标题
    title_name = analysis_title(issue_content)

    # 修改表格内容
    # 获取pr列表, (这里标题最后一位为结束字符)
    # TODO(gouzil): 这里需要去重
    pr_data: PaginatedList[PullRequest] = get_pr_list(issue_create_time, title_name[:-1])
    doc_table = update_pr_table(doc_table, title_name, pr_data)

    # 评论更新
    doc_table = update_issue_table(doc_table, issue_comments)

    # 转换ast到md
    md = to_markdown(doc_table)
    # 替换原数据表格
    md = replace_table(issue_content, start_str, end_str, md)
    # print(md)
    # print(title_name)

    # 添加统计

    save_file(md, time.strftime("%Y-%m-%d-%H-%M-%S") + issue_title + ".md")


@app.command()
def issue_backup(repo: str, issues_id: int, token: str, log_level: str = "INFO"):
    init_logger(log_level)
    Fetcher.set_github(token)
    Fetcher.set_repo(repo)
    issues_title, issue_content, _, _ = get_issues(issues_id)
    save_file(issue_content, time.strftime("%Y-%m-%d-%H-%M-%S") + issues_title + ".md", issues_title)


if __name__ == "__main__":  # pragma: no cover
    app()
