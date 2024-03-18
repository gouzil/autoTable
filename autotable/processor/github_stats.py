from __future__ import annotations

from mistletoe.block_token import Table
from mistletoe.span_token import Strikethrough

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.analysis import analysis_table_more_people
from autotable.storage_model.table import TablePeople, TableStatistics


def update_stats_data(doc_table: Table, update_people: bool = True):
    for table_row in doc_table.children:
        # 对已删除任务特判, 但任然会记录状态位
        if isinstance(table_row.children[0].children[0], Strikethrough):
            assert isinstance(table_row.children[0].children[0].children[0].content[0], str)
            stats: StatusType = StatusType(table_row.children[0].children[0].children[0].content[0])
        else:
            assert isinstance(table_row.children[0].children[0].content, str)
            assert not table_row.children[0].children[0].content.startswith("~")
            stats: StatusType = StatusType(table_row.children[0].children[0].content[0])

        TableStatistics.status[stats] += 1

        if stats == StatusType.COMPLETED and update_people:
            people_names: list[TablePeople] = [
                TablePeople(StatusType(x[0]), x[2:])
                for x in analysis_table_more_people(table_row.children[-2].children[0].content)
            ]
            for people in people_names:
                # 找到那个被合入的人, 更新
                if people.status == StatusType.COMPLETED:
                    if people.github_id not in TableStatistics.all_merge:
                        TableStatistics.all_merge[people.github_id] = 1
                    else:
                        TableStatistics.all_merge[people.github_id] += 1


def update_stats_table(stats_table: Table) -> Table:
    status_type_list: list[str] = [x.value for x in StatusType]
    status_type_list.append("🏁")
    # 统计表中有哪些是需要统计的
    for index, stats_index in enumerate(stats_table.header.children):
        status = stats_index.children[0].content[0]
        # 排除没有状态位的
        if status not in status_type_list:
            continue
        if status == "🏁":
            sum_total: float = (
                TableStatistics.status[StatusType.COMPLETED] / sum(TableStatistics.status.values())
            ) * 100
            stats_table.children[0].children[index].children[0].content = f"{sum_total:.1f}%"
            continue
        stats_table.children[0].children[index].children[0].content = str(TableStatistics.status[StatusType(status)])

    return stats_table


def update_stats_people() -> str:
    res: str = "> 排名不分先后 "

    for k, v in TableStatistics.all_merge.items():
        res += f"@{k}({v}) "

    return res + "\n"
