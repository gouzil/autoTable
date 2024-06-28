from __future__ import annotations

from mistletoe.block_token import Table
from mistletoe.span_token import RawText, Strikethrough

from autotable.autotable_type.autotable_type import StatusType
from autotable.processor.analysis import analysis_table_more_people
from autotable.storage_model.table import TablePeople


def update_table_people(status: StatusType, user_name: str, table_row: str) -> str:
    # 处理人名
    # 第一位是@位, 第二位是状态位
    people_names: list[TablePeople] = [TablePeople(status, user_name)]
    people_names.extend([TablePeople(StatusType(x[0]), x[2:]) for x in analysis_table_more_people(table_row)])
    people_names = TablePeople_list_repeat(people_names)
    table_people_names: str = ""
    if len(people_names) == 1:
        table_people_names = f"{people_names[0].status.value}@{people_names[0].github_id}"
    else:
        for people in people_names:
            # 这里全部以 pr 状态为主
            if people.github_id not in table_people_names:
                table_people_names += f"{people.status.value}@{people.github_id}<br/>"
    return table_people_names


# TODO: 考虑移动到 TablePeople 类中
# TablePeople 去重, 这里会调整状态
def TablePeople_list_repeat(TablePeople_list: list[TablePeople]) -> list[TablePeople]:
    res: list[TablePeople] = []
    for people in TablePeople_list:
        write = True
        for res_index, res_data in enumerate(res):
            if people.github_id == res_data.github_id and people.status == res_data.status:
                write = False
                break
            if people.github_id != res_data.github_id:
                continue
            # 取较大的那个状态更新
            if res_data.status > people.status:
                write = False
            else:
                res[res_index].status = people.status
                write = False
        if write:
            res.append(people)

    return res


def clean_table_people(table: Table) -> Table:
    for table_row in table.children:
        # 跳过已经删除的行
        if isinstance(table_row.children[0].children[0], Strikethrough):
            continue

        assert isinstance(table_row.children[0].children[0], RawText)
        assert isinstance(table_row.children[0].children[0].content, str)
        assert not table_row.children[0].children[0].content.startswith("~")
        index: str = table_row.children[0].children[0].content

        status_type_list = [t.value for t in StatusType]

        for t in status_type_list:
            if index.startswith(t):
                table_row.children[0].children[0].content = f"{StatusType.PENDING.value}{index[len(t) :]}"
                break
        else:
            table_row.children[0].children[0].content = f"{StatusType.PENDING.value}{index}"

        if len(table_row.children[-2].children) != 0:
            table_row.children[-2].children[0].content = ""
        if len(table_row.children[-1].children) != 0:
            table_row.children[-1].children[0].content = ""

    return table
