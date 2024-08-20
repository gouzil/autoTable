from __future__ import annotations

from loguru import logger

from autotable import constant
from autotable.command import check_table_index_repeat, init_issue_table
from autotable.processor.analysis import content2table
from autotable.storage_model.tracker_issues_data import TrackerIssuesData
from tests.util import CaptureLogger


def test_init_issue_table():
    constant.global_table_index_set.clear()
    start_str: str = '<!--table_start="A"-->'
    end_str: str = '<!--table_end="A"-->'
    issue_content = f"""{start_str}
| 序号     | 所在文件                  | 优先级    | 单测覆盖率 |   认领人    | PR         |
| ------ | --------------------- | ------ | :---: | :------: | ---------------------------------------------- |
| 🚧1     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧2     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧3     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🔵4     | ***/all_gather.py     | p1     |       |          |                                                |
| 🟢5     | ***/all_reduce.py     | p1     |       | 🟢@gouzil | gouzil/autotable#4                             |
| 🟡6     | ***/all_to_all.py     | p1     |       | 🟡@gouzil | gouzil/autotable#5                             |
| ✅7     | ***/all_to_all.py     | p1     |       | ✅@gouzil | gouzil/autotable#1<br/>gouzil/autotable#6<br/> |
| ~~🔵8~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |          |                                                |
{end_str}
"""
    tracker_issues_data = TrackerIssuesData("", issue_content, None, None, "")

    new_issue = init_issue_table(tracker_issues_data)

    print(new_issue)

    res = f"""{start_str}
| 序号     | 所在文件                  | 优先级    | 单测覆盖率 | 认领人 | PR  |
| ------ | --------------------- | ------ | :---: | :-: | --- |
| 🔵1     | ***/group.py          | p1     |       |     |     |
| 🔵2     | ***/group.py          | p1     |       |     |     |
| 🔵3     | ***/group.py          | p1     |       |     |     |
| 🔵4     | ***/all_gather.py     | p1     |       |     |     |
| 🔵5     | ***/all_reduce.py     | p1     |       |     |     |
| 🔵6     | ***/all_to_all.py     | p1     |       |     |     |
| 🔵7     | ***/all_to_all.py     | p1     |       |     |     |
| ~~🔵8~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |     |     |
{end_str}
"""

    assert new_issue == res


def test_check_table_index_repeat():
    constant.global_table_index_set.clear()
    issue_content = """| 序号     | 所在文件                  | 优先级    | 单测覆盖率 |   认领人    | PR         |
| ------ | --------------------- | ------ | :---: | :------: | ---------------------------------------------- |
| 🚧1     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧3     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🔵3     | ***/all_gather.py     | p1     |       |          |                                                |
| 🟢5     | ***/all_reduce.py     | p1     |       | 🟢@gouzil | gouzil/autotable#4                             |
| ~~🔵8~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |          |                                                |
"""

    with CaptureLogger(logger) as caplog:
        check_table_index_repeat(content2table(issue_content))

    assert "table index repeat: 3" in caplog.out
