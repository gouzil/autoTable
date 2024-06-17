from __future__ import annotations

import time
from typing import TYPE_CHECKING

from autotable.api.prs import get_pr_list
from autotable.processor.analysis import (
    analysis_enter,
    analysis_repo,
    analysis_table_content,
    analysis_table_generator,
    analysis_title,
    content2Table,
)
from autotable.processor.file import replace_table, save_file, to_markdown
from autotable.processor.github_issue import update_issue_table
from autotable.processor.github_prs import update_pr_table
from autotable.processor.github_stats import update_stats_data, update_stats_people, update_stats_table
from autotable.storage_model.tracker_issues_data import TrackerIssuesData

if TYPE_CHECKING:
    from github.PaginatedList import PaginatedList
    from github.PullRequest import PullRequest


def backup(issue_title: str, issue_content: str) -> None:
    save_file(issue_content, time.strftime("%Y-%m-%d-%H-%M-%S") + f"{issue_title}.md", issue_title)


def update_stats(issue_title: str, issue_content: str, dry_run: bool) -> str:
    for start_str, end_str in analysis_table_generator(issue_content):
        doc_table = analysis_table_content(issue_content, start_str, end_str)
        # 这里的repo地址不会被使用, 但是需要解析并删除
        doc_table, _ = analysis_repo(doc_table, "default/repo")
        # 解析表格
        doc_table = content2Table(doc_table)
        # 更新统计数据
        update_stats_data(doc_table, False)

    # 添加统计
    # 解析数据统计表格
    stats_start_str = "<!--stats start bot-->"
    stats_end_str = "<!--stats end bot-->"
    doc_stats_table = content2Table(analysis_table_content(issue_content, stats_start_str, stats_end_str))
    stats_table = update_stats_table(doc_stats_table)
    stats_md = to_markdown(stats_table)
    issue_content = replace_table(issue_content, stats_start_str, stats_end_str, stats_md)

    if dry_run:
        # 保存导出
        save_file(issue_content, time.strftime("%Y-%m-%d-%H-%M-%S") + f"{issue_title}.md", dry_run=dry_run)
    return issue_content


def update_content(
    tracker_issues_data: TrackerIssuesData,
    dry_run: bool,
) -> str:
    # issue内容
    issue_content = tracker_issues_data.issue_content
    # 解析任务开头标题 (这是一个正则表达式)
    title_re = analysis_title(issue_content)
    # 解析报名正则
    enter_re = analysis_enter(issue_content)
    # 获取pr列表
    pr_data: PaginatedList[PullRequest] = get_pr_list(tracker_issues_data.issue_create_time, title_re)

    # 大致思路为表格序号匹配标题序号
    for start_str, end_str in analysis_table_generator(issue_content):
        # 拆分markdown表格
        doc_table = analysis_table_content(issue_content, start_str, end_str)
        # 存储多个 repo 的 pr 数据
        pr_data_list = [pr_data]
        pr_url_use_http_ = False

        # 为当前表格单独解析 repo 地址
        doc_table, repo_list_ = analysis_repo(doc_table, tracker_issues_data.repo)

        # 如果repo地址不一致, 则重新获取pr列表
        if len(repo_list_) != 0:
            for repo_ in repo_list_:
                pr_data_list.append(get_pr_list(tracker_issues_data.issue_create_time, title_re, repo_))
            pr_url_use_http_ = True

        # 解析表格
        doc_table = content2Table(doc_table)

        # 修改表格内容, 根据多个repo的pr数据更新
        for pr_data_ in pr_data_list:
            # 更新pr数据
            doc_table = update_pr_table(
                doc_table,
                title_re,
                pr_data_,
                False
                if pr_data_[0].base.repo.full_name == tracker_issues_data.repo
                else pr_url_use_http_,  # TODO:或许填写了自定义repo都应该使用http, 而不应该区分他是不是自己的repo
            )

        # 评论更新
        doc_table = update_issue_table(doc_table, tracker_issues_data.issue_comments, enter_re)

        # 更新统计数据
        update_stats_data(doc_table)

        # 转换ast到md
        doc_md = to_markdown(doc_table)

        # 如果repo地址不一致, 代表使用自定义repo, 则重新补充repo地址
        if len(repo_list_) != 0:
            doc_md = f'<!--repo="{";".join(repo_list_)}"-->\n' + doc_md

        # 替换原数据表格
        issue_content = replace_table(issue_content, start_str, end_str, doc_md)

    # 添加统计
    # 解析数据统计表格
    stats_start_str = "<!--stats start bot-->"
    stats_end_str = "<!--stats end bot-->"
    if stats_end_str in issue_content:
        doc_stats_table = content2Table(analysis_table_content(issue_content, stats_start_str, stats_end_str))
        stats_table = update_stats_table(doc_stats_table)
        stats_md = to_markdown(stats_table)
        issue_content = replace_table(issue_content, stats_start_str, stats_end_str, stats_md)

    # 替换贡献者名单
    contributors_start_str = "<!--contributors start bot-->"
    contributors_end_str = "<!--contributors end bot-->"
    if contributors_start_str in issue_content:
        issue_content = replace_table(
            issue_content, contributors_start_str, contributors_end_str, update_stats_people()
        )

    # TODO(gouzil): 加个diff
    if dry_run:
        # 保存导出
        save_file(
            issue_content, time.strftime("%Y-%m-%d-%H-%M-%S") + f"{tracker_issues_data.issue_title}.md", dry_run=dry_run
        )
    return issue_content
