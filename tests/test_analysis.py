from __future__ import annotations

from mistletoe.block_token import Table

from autotable.processor.analysis import (
    analysis_enter,
    analysis_repo,
    analysis_review,
    analysis_table_content,
    analysis_table_generator,
    analysis_table_more_people,
    analysis_title,
)


def test_analysis_title():
    "测试解析任务标题正则"
    title = r'<!--title_name="\[Cleanup\]\[(?P<task_id>[\S\s]+)\]"-->'
    assert analysis_title(title) == r"\[Cleanup\]\[(?P<task_id>[\S\s]+)\]"


def test_analysis_table_content():
    "解析是否为表格"
    start_str: str = '<!--table_start="A"-->'
    end_str: str = '<!--table_end="A"-->'
    table = f"""
{start_str}
|  序号  |  文件位置  |  认领人  |  PR  |
| :---: | :---: | :---: | :---: |
| 🚧A-1 | amp_o2_pass.py |  🚧@gouzil  | #1 |
| 🔵A-2 | test_cummax_op.py |   |  |
{end_str}
"""
    res = analysis_table_content(table, start_str, end_str)
    assert isinstance(res, Table)


def test_analysis_enter():
    "解析贡献者"
    res = analysis_enter(
        r'<!--enter="(\[|【)报名(\]|】)(:|：)(?P<task_id>[\S\s]+)"-->'  # noqa: RUF001
    )
    assert res == r"(\[|【)报名(\]|】)(:|：)(?P<task_id>[\S\s]+)"  # noqa: RUF001


def test_analysis_review():
    "解析 review 对 bot 操作"
    res = analysis_review('<!--bot_next="A-1,A-2"--> ')
    assert res == "A-1,A-2"


def test_analysis_table_more_people():
    res1 = analysis_table_more_people("@gouzil<br/>@gouzil<br/>")
    assert res1 == ["@gouzil", "@gouzil"]

    res2 = analysis_table_more_people("@gouzil<br/>@gouzil")
    assert res2 == ["@gouzil", "@gouzil"]

    res3 = analysis_table_more_people("")
    assert res3 == []

    res4 = analysis_table_more_people("@gouzil")
    assert res4 == ["@gouzil"]


def test_analysis_table_iter():
    issues_content = """
<!--table_start="A"-->
<!--table_end="A"-->
<!--table_start="C"-->
<!--table_end="C"-->
<!--table_start="D"-->
<!--table_end="D"-->
"""
    astab = analysis_table_generator(issues_content)
    assert list(astab) == [
        ('<!--table_start="A"-->', '<!--table_end="A"-->'),
        ('<!--table_start="C"-->', '<!--table_end="C"-->'),
        ('<!--table_start="D"-->', '<!--table_end="D"-->'),
    ]


def test_analysis_repo():
    repo = "gouzil/autoTable"
    issue_content = """
<!--table_start="B"-->
<!--repo="gouzil/autoTable"-->
| 序号    | 文件                                          | API 数量 | 认领人 Github id    | PR 链接  |
| ----- | ------------------------------------------- | ------ | ---------------- | ------ |
| 🔵B-1  | paddle/tensor/array.py                      | 4      |       | |
<!--table_end="B"-->
"""
    rep_issue = issue_content.replace(f'<!--repo="{repo}"-->', "")
    assert analysis_repo(issue_content, "gouzil/test") == (rep_issue, repo)
    assert analysis_repo(rep_issue, "gouzil/test") == (rep_issue, "gouzil/test")
