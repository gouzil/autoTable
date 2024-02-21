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
from autotable.processor.analysis import (
    analysis_enter,
    analysis_table_content,
    analysis_table_generator,
    analysis_title,
)
from autotable.processor.file import replace_table, save_file, to_markdown
from autotable.processor.github_issue import update_issue_table
from autotable.processor.github_prs import update_pr_table
from autotable.processor.github_stats import update_stats_data, update_stats_people, update_stats_table
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


def init(
    repo: str,
    token: str,
    log_level: str = "INFO",
):
    # 初始化
    init_logger(log_level)
    Fetcher.set_github(token)
    Fetcher.set_repo(repo)


@app.command()
def issue_update(
    repo: str,
    issues_id: int,
    token: str,
    log_level: str = "INFO",
):
    init(repo, token, log_level)
    # 获取issue内容
    issue_title, issue_content, issue_create_time, issue_comments = get_issues(issues_id)

    # 解析任务开头标题 (这是一个正则表达式)
    title_re = analysis_title(issue_content)
    # 解析报名正则
    enter_re = analysis_enter(issue_content)
    # 获取pr列表
    pr_data: PaginatedList[PullRequest] = get_pr_list(issue_create_time, title_re)

    # 大致思路为表格序号匹配标题序号

    for start_str, end_str in analysis_table_generator(issue_content):
        # 解析表格
        doc_table = analysis_table_content(issue_content, start_str, end_str)

        # 修改表格内容
        doc_table = update_pr_table(doc_table, title_re, pr_data)

        # 评论更新
        doc_table = update_issue_table(doc_table, issue_comments, enter_re)

        # 更新统计数据
        update_stats_data(doc_table)

        # 转换ast到md
        doc_md = to_markdown(doc_table)
        # 替换原数据表格
        issue_content = replace_table(issue_content, start_str, end_str, doc_md)

    # 添加统计
    # 解析数据统计表格
    stats_start_str = "<!--stats start bot-->"
    stats_end_str = "<!--stats end bot-->"
    doc_stats_table = analysis_table_content(issue_content, stats_start_str, stats_end_str)
    stats_table = update_stats_table(doc_stats_table)
    stats_md = to_markdown(stats_table)
    issue_content = replace_table(issue_content, stats_start_str, stats_end_str, stats_md)

    # 替换贡献者名单
    contributors_start_str = "<!--contributors start bot-->"
    contributors_end_str = "<!--contributors end bot-->"
    md = replace_table(issue_content, contributors_start_str, contributors_end_str, update_stats_people())

    # TODO(gouzil): 加个diff
    # 保存导出
    save_file(md, time.strftime("%Y-%m-%d-%H-%M-%S") + issue_title + ".md")


@app.command()
def issue_update_stats(repo: str, issues_id: int, token: str, log_level: str = "INFO"):
    init(repo, token, log_level)
    # 获取issue内容
    issue_title, issue_content, _, _ = get_issues(issues_id)
    for start_str, end_str in analysis_table_generator(issue_content):
        # 解析表格
        doc_table = analysis_table_content(issue_content, start_str, end_str)
        # 更新统计数据
        update_stats_data(doc_table, False)

    # 添加统计
    # 解析数据统计表格
    stats_start_str = "<!--stats start bot-->"
    stats_end_str = "<!--stats end bot-->"
    doc_stats_table = analysis_table_content(issue_content, stats_start_str, stats_end_str)
    stats_table = update_stats_table(doc_stats_table)
    stats_md = to_markdown(stats_table)
    issue_content = replace_table(issue_content, stats_start_str, stats_end_str, stats_md)

    # 保存导出
    save_file(issue_content, time.strftime("%Y-%m-%d-%H-%M-%S") + issue_title + ".md")


@app.command()
def issue_backup(repo: str, issues_id: int, token: str, log_level: str = "INFO"):
    init(repo, token, log_level)
    issues_title, issue_content, _, _ = get_issues(issues_id)
    save_file(issue_content, time.strftime("%Y-%m-%d-%H-%M-%S") + issues_title + ".md", issues_title)


if __name__ == "__main__":  # pragma: no cover
    app()
