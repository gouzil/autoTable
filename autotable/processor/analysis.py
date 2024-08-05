from __future__ import annotations

import re

from loguru import logger
from mistletoe import Document, ast_renderer
from mistletoe.block_token import Table


# 解析markdown表格
def analysis_table_content(content: str, start_str: str, end_str: str) -> str:
    """切分 markdown 表格内容"""
    return content[content.find(start_str) + len(start_str) : content.find(end_str)]


def content2table(content: str) -> Table:
    """将 markdown 表格转换为 Table 对象"""
    doc = Document(content.split("\n"))
    assert isinstance(doc.children[0], Table)

    # 渲染一下ast, 方便调试
    logger.debug(ast_renderer.get_ast(doc))

    return doc.children[0]


# 解析任务列表markdown中任务的标题
def analysis_title(content: str) -> str:
    """
    解析pr开头标题, 这里返回的应该是正则表达式

    <!--title_name=""-->
    """
    title_start = '<!--title_name="'
    title_end = '"-->'
    content = content[content.find(title_start) + len(title_start) :]
    return content[: content.find(title_end)]


def analysis_review(content: str) -> str | None:
    """
    解析 review 中对 bot 的操作

    <!--bot_next=""-->
    """
    bot_start = '<!--bot_next="'
    bot_end = '"-->'

    if bot_start not in content:
        return None

    content = content[content.find(bot_start) + len(bot_start) :]
    return content[: content.find(bot_end)]


def analysis_enter(content: str) -> str:
    """
    报名解析

    <!--enter=""-->
    """
    enter_start = '<!--enter="'
    enter_end = '"-->'
    if enter_start not in content:
        raise RuntimeError("not find enter")

    content = content[content.find(enter_start) + len(enter_start) :]
    return content[: content.find(enter_end)]


def analysis_pr_search_content(content: str) -> str:
    """
    解析搜索内容, 解析出来的内容可以用于搜索

    <!--pr_search_content=""-->
    """
    search_start = '<!--pr_search_content="'
    search_end = '"-->'
    if search_start not in content:
        return ""

    content = content[content.find(search_start) + len(search_start) :]
    return content[: content.find(search_end)]


def analysis_table_more_people(content: str) -> list[str]:
    """
    分割人或者pr号
    """
    if len(content) == 0:
        return []
    if "<br/>" in content:
        if content.endswith("<br/>"):
            return content.split("<br/>")[:-1]
        else:
            return content.split("<br/>")
    return [content]


def analysis_table_generator(issue_content: str):
    """
    表单迭代器, 用于判断表格是否存在, 并返回开始和结束字段
    """
    start_str: str = '<!--table_start="{}"-->'
    end_str: str = '<!--table_end="{}"-->'
    for trace_index in range(ord("A"), ord("Z") + 1):
        # 如果这个表格不存在就跳过
        if start_str.format(chr(trace_index)) not in issue_content:
            continue
        yield (start_str.format(chr(trace_index)), end_str.format(chr(trace_index)))


def analysis_repo(issue_content: str, repo: str) -> tuple[str, list[str]]:
    """
    解析repo地址, 支持多个repo, 使用;分割

    <!--repo=""-->
    """
    if "/" not in repo:
        logger.error("please check repo")
        raise RuntimeError(f"repo format error: {repo}")

    repo_start = '<!--repo="'
    repo_end = '"-->'
    if repo_start not in issue_content:
        return issue_content, [repo]

    repo_text_list = re.search(f"{repo_start}(.*){repo_end}", issue_content)
    assert repo_text_list is not None
    res_repo = repo_text_list.group(1).split(";")
    if res_repo[-1] == "":
        res_repo.pop()
    res_repo = list(set(res_repo))

    return issue_content.replace(f"{repo_start}{repo_text_list.group(1)}{repo_end}", ""), res_repo


def analysis_pull_start_time(issue_content: str) -> str:
    """
    解析pull开始时间

    <!--start_pull_time=""-->
    """
    start_time_start = '<!--start_pull_time="'
    start_time_end = '"-->'
    if start_time_start not in issue_content:
        return ""

    content = issue_content[issue_content.find(start_time_start) + len(start_time_start) :]
    return content[: content.find(start_time_end)]
