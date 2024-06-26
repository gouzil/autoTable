from __future__ import annotations

from autotable.processor.analysis import content2Table
from autotable.processor.file import to_markdown
from autotable.processor.github_issue import update_issue_table
from autotable.storage_model.tracker_issues_data import IssuesCommentData


def test_update_issue_table():
    enter_re = r"(\[|【)报名(\]|】)(:|：)(?P<task_id>[\S\s]+)"  # noqa: RUF001
    doc_table_content = """| 序号     | 所在文件        | 优先级    | 单测覆盖率 |    认领人    | PR  |
| ------ | ------------ |  ------ | :---: | :-------------------------------: | --- |
| 🙋1     | ***/group.py          | p1     |        |         🙋@user            |   |
| 🔵2     |  ***/group.py          | p1     |       |                     |    |
| 🔵3     |  ***/group.py          | p1     |       |                     |    |
| 🙋4     |  ***/all_gather.py     | p1     |       |        🙋@gouzil    |    |
| 🙋5     |  ***/all_reduce.py     | p1     |       |        🙋@gouzil    |    |
| 🔵6     |  ***/all_to_all.py     | p1     |       |                    |     |
| 🔵7     |  ***/all_to_all.py     | p1     |       |                    |     |
| ~~🔵8~~ |  ~~***/all_to_all.py~~ | ~~p1~~ |       |                    |    |
"""

    issue_comment_data1 = IssuesCommentData(1, "[报名]: 1, 2, 3", "url", "gouzil")
    issue_comment_data2 = IssuesCommentData(2, "报名: 7", "url", "user")
    issue_comment_data_list = [issue_comment_data1, issue_comment_data2]
    res_table_content = to_markdown(
        update_issue_table(content2Table(doc_table_content), issue_comment_data_list, enter_re)
    )
    res = """| 序号     | 所在文件                  | 优先级    | 单测覆盖率 |           认领人            | PR  |
| ------ | --------------------- | ------ | :---: | :----------------------: | --- |
| 🙋1     | ***/group.py          | p1     |       | 🙋@gouzil<br/>🙋@user<br/> |     |
| 🙋2     | ***/group.py          | p1     |       |         🙋@gouzil         |     |
| 🙋3     | ***/group.py          | p1     |       |         🙋@gouzil         |     |
| 🙋4     | ***/all_gather.py     | p1     |       |         🙋@gouzil         |     |
| 🙋5     | ***/all_reduce.py     | p1     |       |         🙋@gouzil         |     |
| 🔵6     | ***/all_to_all.py     | p1     |       |                          |     |
| 🔵7     | ***/all_to_all.py     | p1     |       |                          |     |
| ~~🔵8~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |                          |     |
"""
    assert res == res_table_content
