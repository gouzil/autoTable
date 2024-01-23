from __future__ import annotations

from mistletoe.block_token import Table

from autotable.autotable_type.autotable_type import StatusType


def update_stats_table(stats_table: Table, doc_table: Table) -> Table:
    status_type_list: list[str] = [x.value for x in StatusType]
    # 统计状态, value是列下标
    status_stats: dict[StatusType, int] = {}
    # 统计表中有哪些是需要统计的
    for index, stats_index in enumerate(stats_table.header.children):
        status = stats_index.children[0].content[0]
        # 排除没有状态位的
        if status not in status_type_list:
            continue
        status_stats[StatusType(status)] = index

    # 统计任务表中的数据
    for doc_index in doc_table.children:
        if doc_index.children[0].children[0].content[0] == "~":
            continue
        status = StatusType(doc_index.children[0].children[0].content[0])
        if status in status_stats:
            # 通过下标找到对应的值位置
            count: str = stats_table.children[0].children[status_stats[status]].children[0].content
            assert count.isdigit()
            stats_table.children[0].children[status_stats[status]].children[0].content = str(int(count) + 1)

    return stats_table
