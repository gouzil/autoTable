from __future__ import annotations

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.analysis import content2Table
from autotable.processor.file import to_markdown
from autotable.processor.github_stats import update_stats_data, update_stats_people, update_stats_table
from autotable.storage_model.table import TableStatistics


def test_update_stats_data():
    doc_table_content = """| 序号     | 所在文件                  | 优先级    | 单测覆盖率 |   认领人    | PR                                             |
| ------ | --------------------- | ------ | :---: | :------: | ---------------------------------------------- |
| 🚧1     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧2     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🚧3     | ***/group.py          | p1     |       | 🚧@gouzil | gouzil/autotable#1                             |
| 🔵4     | ***/all_gather.py     | p1     |       |          |                                                |
| 🟢5     | ***/all_reduce.py     | p1     |       | 🟢@gouzil | gouzil/autotable#4                             |
| 🟡6     | ***/all_to_all.py     | p1     |       | 🟡@gouzil | gouzil/autotable#5                             |
| ✅7     | ***/all_to_all.py     | p1     |       | ✅@gouzil | gouzil/autotable#1<br/>gouzil/autotable#6<br/> |
| ✅8     | ***/all_to_all.py     | p1     |       | ✅@gouzil | gouzil/autotable#1<br/>gouzil/autotable#6<br/> |
| ~~🔵9~~ | ~~***/all_to_all.py~~ | ~~p1~~ |       |          |                                                |
"""  # noqa: E501

    # 重置
    TableStatistics.status = {StatusKey: 0 for StatusKey in StatusType}
    TableStatistics.all_merge = {}

    update_stats_data(content2Table(doc_table_content))
    assert TableStatistics.all_merge["gouzil"] == 2  # noqa: PLR2004
    assert TableStatistics.status[StatusType.CLAIMED] == 0
    assert TableStatistics.status[StatusType.NEXT_STAGE] == 1
    assert TableStatistics.status[StatusType.REPAIRING] == 3  # noqa: PLR2004
    assert TableStatistics.status[StatusType.PENDING_MERGE] == 1

    assert update_stats_people() == "> 排名不分先后 @gouzil(2) \n"


def test_update_stats_table():
    doc_table_content = """| 任务数量 | 🔵 可认领 | 🚧 迁移中 | 🟢 待合入 | ✅ 完成 | 🟡 下阶段推进 | 🏁完成率  |
| ---- | ----- | ----- | ----- | ---- | ------- | ---- |
| 7   | 7    | 0     | 0     | 0    | 0       | 0.0% |
"""
    # 重置
    TableStatistics.status = {StatusKey: 0 for StatusKey in StatusType}
    TableStatistics.all_merge = {}

    TableStatistics.status[StatusType.CLAIMED] = 0
    TableStatistics.status[StatusType.NEXT_STAGE] = 1
    TableStatistics.status[StatusType.REPAIRING] = 3
    TableStatistics.status[StatusType.PENDING_MERGE] = 1
    TableStatistics.status[StatusType.COMPLETED] = 2
    res_table_content = to_markdown(update_stats_table(content2Table(doc_table_content)))
    print(res_table_content)

    res = """| 任务数量 | 🔵 可认领 | 🚧 迁移中 | 🟢 待合入 | ✅ 完成 | 🟡 下阶段推进 | 🏁完成率  |
| ---- | ----- | ----- | ----- | ---- | ------- | ----- |
| 7    | 0     | 3     | 1     | 2    | 1       | 28.6% |
"""
    assert res == res_table_content
