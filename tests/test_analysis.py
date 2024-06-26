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
    content2Table,
)
from autotable.processor.file import replace_table, to_markdown


def test_analysis_title():
    "测试解析任务标题正则"
    title = r'<!--title_name="\[Cleanup\]\[(?P<task_id>[\S\s]+)\]"-->'
    assert analysis_title(title) == r"\[Cleanup\]\[(?P<task_id>[\S\s]+)\]"


def test_analysis_table_content():
    "解析是否为表格"
    start_str: str = '<!--table_start="A"-->'
    end_str: str = '<!--table_end="A"-->'
    table = """|  序号  |       文件位置        |   认领人    | PR  |
| :--: | :---------------: | :------: | :-: |
| 🚧A-1 |  amp_o2_pass.py   | 🚧@gouzil | #1  |
| 🔵A-2 | test_cummax_op.py |          |     |
"""

    issues_content = f"{start_str}\ntable\n{end_str}"

    res = content2Table(analysis_table_content(f"{start_str}\n{table}{end_str}", start_str, end_str))
    assert isinstance(res, Table)
    assert to_markdown(res) == table
    assert replace_table(issues_content, start_str, end_str, table) == f"{start_str}\n{table}{end_str}"


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
    test_repo = "gouzil/test"
    issue_content = f"""
<!--table_start="B"-->
<!--repo="{repo}"-->
| 序号    | 文件                                          | API 数量 | 认领人 Github id    | PR 链接  |
| ----- | ------------------------------------------- | ------ | ---------------- | ------ |
| 🔵B-1  | paddle/tensor/array.py                      | 4      |       | |
<!--table_end="B"-->
"""
    rep_issue = issue_content.replace(f'<!--repo="{repo}"-->', "")
    assert analysis_repo(issue_content, test_repo) == (rep_issue, [repo])
    assert analysis_repo(rep_issue, test_repo) == (rep_issue, [test_repo])

    issue_content_ = issue_content.replace(f'<!--repo="{repo}"-->', f'<!--repo="{repo};{repo}"-->')
    repos_issue_ = issue_content_.replace(f'<!--repo="{repo};{repo}"-->', "")
    assert analysis_repo(issue_content_, test_repo) == (repos_issue_, [repo])

    issue_content_ = issue_content.replace(f'<!--repo="{repo}"-->', f'<!--repo="{repo};{test_repo}"-->')
    repos_issue_ = issue_content_.replace(f'<!--repo="{repo};{test_repo}"-->', "")
    analysis_res = analysis_repo(issue_content_, test_repo)
    assert analysis_res[0] == repos_issue_
    assert analysis_res[1] == [repo, test_repo] or analysis_res[1] == [test_repo, repo]

    try:
        analysis_repo(issue_content, "")
        raise AssertionError()
    except RuntimeError as e:
        assert str(e) == "repo format error: "
