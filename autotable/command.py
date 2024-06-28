from __future__ import annotations

import time
from datetime import datetime

from autotable.api.prs import get_pr_list
from autotable.processor.analysis import (
    analysis_enter,
    analysis_pull_start_time,
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
from autotable.processor.utils import clean_table_people
from autotable.storage_model.pull_data import PullRequestData
from autotable.storage_model.tracker_issues_data import TrackerIssuesData
from autotable.utils.migrate import migrate_pr_url_02to03


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
    reset_table: bool,
) -> str:
    assert tracker_issues_data.issue_create_time is not None
    assert tracker_issues_data.issue_comments is not None

    # issue内容
    issue_content = tracker_issues_data.issue_content
    # 解析任务开头标题 (这是一个正则表达式)
    title_re = analysis_title(issue_content)
    # 解析报名正则
    enter_re = analysis_enter(issue_content)
    # 解析pr开始搜索时间
    pull_start_time = analysis_pull_start_time(issue_content)
    if pull_start_time == "":
        pull_start_time = tracker_issues_data.issue_create_time
    else:
        pull_start_time = datetime.strptime(pull_start_time, "%Y-%m-%d")

    # 获取pr列表
    pr_data: list[PullRequestData] = get_pr_list(pull_start_time, title_re)

    # 大致思路为表格序号匹配标题序号
    for start_str, end_str in analysis_table_generator(issue_content):
        # 拆分markdown表格
        doc_table = analysis_table_content(issue_content, start_str, end_str)
        # 存储多个 repo 的 pr 数据
        pr_data_list = [pr_data] if len(pr_data) != 0 else []

        # 为当前表格单独解析 repo 地址
        doc_table, repo_list_ = analysis_repo(doc_table, tracker_issues_data.owner_repo)

        # 如果repo地址不一致, 则重新获取pr列表
        if len(repo_list_) != 0:
            for repo_ in [
                repo
                for repo in repo_list_
                if repo not in [pr[0].base_repo_full_name for pr in pr_data_list]  # 去重
            ]:
                pull_request_list = get_pr_list(pull_start_time, title_re, repo_)
                # 去除pr列表为空的repo
                if len(pull_request_list) != 0:
                    pr_data_list.append(pull_request_list)

        # 解析表格
        doc_table = content2Table(doc_table)

        if reset_table:
            # 重置表格内的所有数据
            doc_table = clean_table_people(doc_table)

        # 修改表格内容, 根据多个repo的pr数据更新
        for pr_data_ in pr_data_list:
            assert len(pr_data_) != 0
            # 更新pr数据
            doc_table = update_pr_table(doc_table, title_re, pr_data_)

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


def replacement_pr_url(tracker_issues_data: TrackerIssuesData) -> str:
    """
    替换url

    https://github.com/gouzil/autoTable/pull/1 -> gouzil/autoTable#1
    #1 -> gouzil/autoTable#1

    """
    # issue内容
    issue_content = tracker_issues_data.issue_content

    for start_str, end_str in analysis_table_generator(issue_content):
        # 拆分markdown表格
        doc_table = analysis_table_content(issue_content, start_str, end_str)

        # 为当前表格单独解析 repo 地址
        doc_table, repo_list_ = analysis_repo(doc_table, tracker_issues_data.owner_repo)

        # 解析表格
        doc_table = content2Table(doc_table)

        doc_table = migrate_pr_url_02to03(doc_table, tracker_issues_data.owner_repo)

        # 转换ast到md
        doc_md = to_markdown(doc_table)

        # 如果repo地址不一致, 代表使用自定义repo, 则重新补充repo地址
        if len(repo_list_) != 0:
            doc_md = f'<!--repo="{";".join(repo_list_)}"-->\n' + doc_md

        # 替换原数据表格
        issue_content = replace_table(issue_content, start_str, end_str, doc_md)

    return issue_content


def init_issue_table(tracker_issues_data: TrackerIssuesData) -> str:
    """初始化表格"""

    # issue内容
    issue_content = tracker_issues_data.issue_content

    for start_str, end_str in analysis_table_generator(issue_content):
        # 拆分markdown表格
        doc_table = analysis_table_content(issue_content, start_str, end_str)
        # 为当前表格单独解析 repo 地址
        doc_table, _ = analysis_repo(doc_table, "/")  # 这里不会用到repo地址
        # 解析表格
        doc_table = content2Table(doc_table)
        # 重置表格内的所有数据
        doc_table = clean_table_people(doc_table)
        # 转换ast到md
        doc_md = to_markdown(doc_table)
        # 替换原数据表格
        issue_content = replace_table(issue_content, start_str, end_str, doc_md)
    return issue_content
